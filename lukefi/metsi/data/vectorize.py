import numpy as np
import numpy.typing as npt
from typing import Optional, Any
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum
from lukefi.metsi.domain.forestry_types import StandList
from dataclasses import dataclass
from lukefi.metsi.data.formats.util import get_or_default 



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
        ("latvuskerros", np.float64) # NOTE: for benchmarking purposes
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
                raise("Vectorized data is not contiguous")
        self.set_size(attr_dict)
        return self

    def is_contiguous(self, name):
        arr = getattr(self, name)
        return True if arr.flags['CONTIGUOUS'] and arr.flags['C_CONTIGUOUS'] else False 

    def set_size(self, attr_dict):
        size = len(attr_dict.get('identifier', []))
        setattr(self, 'size', size)

    def defaultify(self, values: list, dtype: npt.DTypeLike) -> list:
        return [ self.to_default(v, dtype) for v in values]

    def to_default(self, value: Optional[Any], field_type: npt.DTypeLike) -> Any:
        """ Replace None with appropriate defaults based on field type. """
        int_default = -1
        str_default = ""
        float_default = np.nan
        bool_default = False
        tuple_default = (np.nan, np.nan, np.nan)
        object_default = None
        
        if value is None:
            if np.issubdtype(field_type, np.integer):
                return int_default
            elif np.issubdtype(field_type, np.floating):
                return float_default
            elif np.issubdtype(field_type, np.str_):
                return str_default
            elif np.issubdtype(field_type, np.bool_):
                return bool_default
            elif np.issubdtype(field_type, np.void):
                return tuple_default
            else:
                return object_default
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

def vectorize(stands: StandList, **operation_params) -> StandList:
   
    target = operation_params.get('target', None)
    if target == None:
        target = ['reference_trees', 'tree_strata']
    else:
        target = [target]

    for stand in stands:
        for t in target:
            attr_dict = {}

            for data in getattr(stand, t, []):
                delattr(data, "stand")
                for k, v in data.__dict__.items():
                    attr_dict.setdefault(k, []).append(v)

            # Overwrite old forestry data
            container_obj = CONTAINERS.get(t)
            setattr(stand, t, container_obj().vectorize(attr_dict))

    return stands


__all__ = ["vectorize"]

if __name__ == "__main__":
    stands = [ForestStand(reference_trees=[ReferenceTree(species=1), ReferenceTree(species=2)])]
    vectorize(stands)
    print()