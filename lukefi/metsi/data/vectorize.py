from dataclasses import dataclass
from typing import Optional, Any
from pprint import pprint
import numpy as np
import numpy.typing as npt
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import ForestStand, ReferenceTree
from lukefi.metsi.domain.forestry_types import StandList


DTYPE_TREE = np.dtype([
    ("identifier", "U20"),
    ("tree_number", np.int32),
    ("species", np.int32),
    ("breast_height_diameter", np.float64),
    ("height", np.float64),
    ("measured_height", np.float64),
    ("breast_height_age", np.float64),
    ("biological_age", np.float64),
    ("stems_per_ha", np.float64),
    ("origin", np.int32),
    ("management_category", np.int32),
    ("saw_log_volume_reduction_factor", np.float64),
    ("pruning_year", np.int16),
    ("age_when_10cm_diameter_at_breast_height", np.int16),
    ("stand_origin_relative_position", np.float64, (3,)),
    ("lowest_living_branch_height", np.float64),
    ("tree_category", np.str_),
    ("storey", np.int32),
    ("sapling", np.bool_),
    ("tree_type", "U20"),
    ("tuhon_ilmiasu", "U20"),
    ("latvuskerros", np.float64)  # NOTE: for benchmarking purposes
])

DTYPE_STRATA = np.dtype([
    ("identifier", "U20"),
    ("species", np.int32),
    ("mean_diameter", np.float64),
    ("mean_height", np.float64),
    ("breast_height_age", np.float64),
    ("biological_age", np.int32),
    ("stems_per_ha", np.float64),
    ("basal_area", np.float64),
    ("origin", np.int32),
    ("management_category", np.int32),
    ("saw_log_volume_reduction_factor", np.float64),
    ("cutting_year", np.int32),
    ("age_when_10cm_diameter_at_breast_height", np.int16),
    ("tree_number", np.int32),
    ("stand_origin_relative_position", np.float64, (3,)),
    ("lowest_living_branch_height", np.float64),
    ("storey", np.int32),
    ("sapling_stems_per_ha", np.float64),
    ("sapling_stratum", np.bool_),
    ("number_of_generated_trees", np.int32)
])


@dataclass
class VectorData():
    def __init__(self, dtype):
        self.dtype = dtype

    def vectorize(self, attr_dict):
        for k, v in attr_dict.items():
            setattr(self, k, np.array(self.defaultify(v, self.dtype[k]), self.dtype[k]))
            if not self.is_contiguous(k):
                raise Exception("Vectorized data is not contiguous")
        self.set_size(attr_dict)
        return self

    def is_contiguous(self, name):
        arr = getattr(self, name)
        return bool(arr.flags['CONTIGUOUS']) and bool(arr.flags['C_CONTIGUOUS'])

    def set_size(self, attr_dict):
        size = len(attr_dict.get('identifier', []))
        setattr(self, 'size', size)

    def defaultify(self, values: list, dtype: npt.DTypeLike) -> list:
        return [self.to_default(v, dtype) for v in values]

    def to_default(self, value: Optional[Any], field_type: npt.DTypeLike) -> Any:
        """ Replace None with appropriate defaults based on field type. """
        int_default = -1
        str_default = ""
        float_default = np.nan
        bool_default = False
        tuple_default = (np.nan, np.nan, np.nan)
        object_default = None
        retval: Any

        if value is None:
            if np.issubdtype(field_type, np.integer):
                retval = int_default
            elif np.issubdtype(field_type, np.floating):
                retval = float_default
            elif np.issubdtype(field_type, np.str_):
                retval = str_default
            elif np.issubdtype(field_type, np.bool_):
                retval = bool_default
            elif np.issubdtype(field_type, np.void):
                retval = tuple_default
            else:
                retval = object_default
            return retval
        return value


@dataclass
class ReferenceTrees(VectorData):

    def __init__(self):
        super().__init__(DTYPE_TREE)


@dataclass
class Strata(VectorData):

    def __init__(self):
        super().__init__(DTYPE_STRATA)


CONTAINERS = {
    "reference_trees": ReferenceTrees,
    "tree_strata": Strata
}


def vectorize(stands: list[ForestStand], **operation_params) -> list[ForestStand]:
    target = operation_params.get('target', None)
    if target is None:
        target = ['reference_trees', 'tree_strata']
    else:
        target = [target]

    for stand in stands:
        for t in target:
            attr_dict: dict[str, Any] = {}

            for data in getattr(stand, t, []):
                delattr(data, "stand")
                for k, v in data.__dict__.items():
                    attr_dict.setdefault(k, []).append(v)

            # Overwrite old forestry data
            container_obj = CONTAINERS.get(t)
            if not container_obj:
                raise Exception(f"Unknown target type '{t}'")
            setattr(stand, t, container_obj().vectorize(attr_dict))

    return stands


__all__ = ["vectorize"]

if __name__ == "__main__":
    stands_ = [ForestStand(reference_trees=[ReferenceTree(species=TreeSpecies(1)),
                                           ReferenceTree(species=TreeSpecies(2))])]
    vectorize(stands_)
    pprint(stands_)
