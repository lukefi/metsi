import bisect
from functools import cache, partial
from pathlib import Path
from typing import TypeVar, Generic, Any, Union, IO
from collections.abc import Iterator, Iterable

from lukefi.metsi.app.app_io import MetsiConfiguration
from lukefi.metsi.app.app_types import SimResults
from lukefi.metsi.domain.utils.collectives import CollectFn, GetVarFn, compile_collector, getvarfn, autocollective
from lukefi.metsi.sim.core_types import OperationPayload

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
            indices = [i for i in range(first, last) if (self.idx[i] - start) % stride == 0]
        else:
            try:
                it = iter(idx)
            except TypeError:
                return self.data[self.idx.index(idx)]
            else:
                indices = [self.idx.index(i) for i in it]
        return CollectiveSeries(
            data=[self.data[i] for i in indices],
            index=[self.idx[i] for i in indices]
        )

    def __iter__(self) -> Iterator[T]:
        yield from self.data


def getseries(schedule: OperationPayload, name: str) -> CollectiveSeries:
    """Get a `CollectiveSeries` for the collective `name` from an `OperationPayload`."""
    data, index = [], []
    for t, c in schedule.collected_data.operation_results["report_collectives"].items():  # type: ignore
        if name in c:
            data.append(c[name])
            index.append(t)
    return CollectiveSeries(data=data, index=index)


def j_row(out: IO, fns: list[CollectFn], getvar: GetVarFn):
    """Write a row to a J file."""
    buf = []
    n = None
    for f in fns:
        v = f(getvar)
        if isinstance(v, str) or not isinstance(v, Iterable):
            n = 1
            buf.append(v)
        elif isinstance(v, Iterable):
            it = iter(v)
            l = len(buf)
            buf.extend(it)
            n = len(buf) - l
        if hasattr(f, "n"):
            if n != getattr(f, "n"):
                raise RuntimeError(f"Collector {f} yielded an inconsistent number of results: {getattr(f, "n")} != {n}")
        else:
            setattr(f, "n", n)
    out.write("\t".join(map(str, buf)))
    out.write("\n")


def j_xda(out: IO, data: SimResults, xvariables: list[str]):
    """Write xdata file."""
    collectives = {
        k for schedules in data.values()
        for payload in schedules
        for c in payload.collected_data.operation_results["report_collectives"].values()  # type: ignore
        for k in c
    }
    xvars = list(map(compile_collector, xvariables or collectives))
    for schedules in data.values():
        for s in schedules:
            j_row(
                out=out,
                fns=xvars,
                getvar=cache(getvarfn(
                    partial(lambda name, sched: (
                        getseries(sched, name) if name in collectives
                        else autocollective(getattr(sched.computational_unit, name))
                    ), sched=s)
                ))
            )


def j_cda(out: IO, data: SimResults, cvariables: list[str]):
    """Write cdata file."""
    cvars = list(map(compile_collector, ["len(schedules)", *cvariables]))
    for schedules in data.values():
        j_row(
            out=out,
            fns=cvars,
            getvar=cache(getvarfn(
                partial(lambda name, sched: autocollective(
                    getattr(sched[0].computational_unit, name)), sched=schedules),
                schedules=schedules
            ))
        )


def j_out(data: SimResults,
          cda_filepath: Path,
          xda_filepath: Path,
          cvariables: list[str],
          xvariables: list[str]):
    """Write J files."""
    with open(cda_filepath, "a", encoding="utf-8") as f:
        j_cda(f, data, cvariables)
    with open(xda_filepath, "a", encoding="utf-8") as f:
        j_xda(f, data, xvariables)


def parse_j_config(config: MetsiConfiguration, decl: dict) -> dict:
    return {
        'cda_filepath': Path(config.target_directory, decl.get("cda_filename", "data.cda")),
        'xda_filepath': Path(config.target_directory, decl.get("xda_filename", "data.xda")),
        'cvariables': decl.get("cvariables", []),
        'xvariables': decl.get("xvariables", [])
    }
