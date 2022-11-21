import bisect
from functools import cache
import sys
from typing import IO, Any, Generic, Iterator, TypeVar, Union
from app.app_io import generate_program_configuration, Mela2Configuration, parse_cli_arguments
from app.file_io import simulation_declaration_from_yaml_file, read_full_simulation_result_dirtree
from sim.collectives import CollectFn, GetVarFn, autocollective, compile, getvarfn
from sim.core_types import OperationPayload


T = TypeVar("T")
class CollectiveSeries(Generic[T]):
    """Collective value series. NOTE: `index` is assumed to be sorted."""

    def __init__(self, data: list[T], index: list):
        self.data = data
        self.idx = index

    def __getitem__(self, idx: Any) -> Union[T, "CollectiveSeries[T]"]:
        if isinstance(idx, slice):
            if not self.idx:
                return CollectiveSeries([], [])
            start, stop, stride = idx.indices(self.idx[-1])
            first = bisect.bisect_left(self.idx, start)
            last = bisect.bisect_right(self.idx, stop)
            indices = [i for i in range(first, last) if (self.idx[i]-start)%stride == 0]
        else:
            try:
                it = iter(idx)
            except TypeError:
                return self.data[self.idx.index(idx)]
            else:
                indices = [self.idx.index(i) for i in it]
        return CollectiveSeries(
            data = [self.data[i] for i in indices],
            index = [self.idx[i] for i in indices]
        )

    def __iter__(self) -> Iterator[T]:
        yield from self.data


def getseries(schedule: OperationPayload, name: str) -> CollectiveSeries:
    """Get a `CollectiveSeries` for the collective `name` from an `OperationPayload`."""
    data, index = [], []
    for t,c in schedule.aggregated_results.operation_results["report_collectives"].items(): # type: ignore
        if name in c:
            data.append(c[name])
            index.append(t)
    return CollectiveSeries(data=data, index=index)


def j_row(out: IO, fns: list[CollectFn], getvar: GetVarFn):
    """Write a row to a J file."""
    buf = []
    for f in fns:
        v = f(getvar)
        try:
            it = iter(v)
        except TypeError:
            # not iterable
            n = 1
            buf.append(v)
        else:
            l = len(buf)
            buf.extend(it)
            n = len(buf) - l
        if hasattr(f, "n"):
            if n != f.n:
                raise RuntimeError(f"Collector {f} yielded an inconsistent number of results: {f.n} != {n}")
        else:
            f.n = n
    out.write("\t".join(map(str, buf)))
    out.write("\n")


def j_xda(out: IO, decl: dict, data: dict[str, list[OperationPayload]]):
    """Write xdata file."""
    collectives = {
        k for schedules in data.values()
        for payload in schedules
        for c in payload.aggregated_results.operation_results["report_collectives"].values() # type: ignore
        for k in c
    }
    xvars = list(map(compile, decl.get("xvariables", collectives)))
    for schedules in data.values():
        for s in schedules:
            j_row(
                out = out,
                fns = xvars,
                getvar = cache(getvarfn(
                    lambda name: (
                        getseries(s, name) if name in collectives
                        else autocollective(getattr(s.simulation_state, name))
                    )
                ))
            )


def j_cda(out: IO, decl: dict, data: dict[str, list[OperationPayload]]):
    """Write cdata file."""
    cvars = list(map(compile, ["len(schedules)", *decl.get("cvariables", [])]))
    for schedules in data.values():
        j_row(
            out = out,
            fns = cvars,
            getvar = cache(getvarfn(
                lambda name: autocollective(getattr(schedules[0].simulation_state, name)),
                schedules = schedules
            ))
        )


def j_out(configuration: Mela2Configuration, decl: dict, data: dict[str, list[OperationPayload]]):
    """Write J files."""
    with open(f"{configuration.target_directory}/{decl.get('cda', 'data.cda')}", "w") as f:
        j_cda(f, decl, data)
    with open(f"{configuration.target_directory}/{decl.get('xda', 'data.xda')}", "w") as f:
        j_xda(f, decl, data)


def main():
    cli_arguments = parse_cli_arguments(sys.argv[1:])
    control_file = Mela2Configuration.control_file if cli_arguments.control_file is None else cli_arguments.control_file
    try:
        control_structure = simulation_declaration_from_yaml_file(control_file)
    except:
        print(f"Application control file path '{control_file}' can not be read. Aborting....")
        return
    app_arguments = generate_program_configuration(cli_arguments, control_structure['app_configuration'])

    data = read_full_simulation_result_dirtree(app_arguments.input_path)
    decl = simulation_declaration_from_yaml_file(app_arguments.control_file)
    format = decl.get("format", "j").lower()
    if format == "j":
        j_out(decl, data)
    else:
        raise ValueError("Unknown output format: '{}'".format(format))


if __name__ == "__main__":
    main()
