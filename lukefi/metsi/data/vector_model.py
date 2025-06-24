from typing import Any, Optional
import numpy as np
import numpy.typing as npt

DTYPES_TREE: dict[str, npt.DTypeLike] = {
    "identifier": np.dtype("U20"),
    "tree_number": np.int32,
    "species": np.int32,
    "breast_height_diameter": np.float64,
    "height": np.float64,
    "measured_height": np.float64,
    "breast_height_age": np.float64,
    "biological_age": np.float64,
    "stems_per_ha": np.float64,
    "origin": np.int32,
    "management_category": np.int32,
    "saw_log_volume_reduction_factor": np.float64,
    "pruning_year": np.int16,
    "age_when_10cm_diameter_at_breast_height": np.int16,
    "stand_origin_relative_position": np.dtype((np.float64, (3,))),
    "lowest_living_branch_height": np.float64,
    "tree_category": np.str_,
    "storey": np.int32,
    "sapling": np.bool_,
    "tree_type": np.dtype("U20"),
    "tuhon_ilmiasu": np.dtype("U20"),
    "latvuskerros": np.float64  # NOTE: for benchmarking purposes
}

DTYPES_STRATA: dict[str, npt.DTypeLike] = {
    "identifier": np.dtype("U20"),
    "species": np.int32,
    "mean_diameter": np.float64,
    "mean_height": np.float64,
    "breast_height_age": np.float64,
    "biological_age": np.int32,
    "stems_per_ha": np.float64,
    "basal_area": np.float64,
    "origin": np.int32,
    "management_category": np.int32,
    "saw_log_volume_reduction_factor": np.float64,
    "cutting_year": np.int32,
    "age_when_10cm_diameter_at_breast_height": np.int16,
    "tree_number": np.int32,
    "stand_origin_relative_position": np.dtype((np.float64, (3,))),
    "lowest_living_branch_height": np.float64,
    "storey": np.int32,
    "sapling_stems_per_ha": np.float64,
    "sapling_stratum": np.bool_,
    "number_of_generated_trees": np.int32
}


class VectorData():
    def __init__(self, dtypes: dict[str, npt.DTypeLike]):
        self.dtypes = dtypes

    def vectorize(self, attr_dict):
        for k, v in attr_dict.items():
            setattr(self, k, np.array(self.defaultify(v, self.dtypes[k]), self.dtypes[k]))
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


class ReferenceTrees(VectorData):
    size: int
    identifier: npt.NDArray[np.str_]
    tree_number: npt.NDArray[np.int32]
    species: npt.NDArray[np.int32]
    breast_height_diameter: npt.NDArray[np.float64]
    height: npt.NDArray[np.float64]
    measured_height: npt.NDArray[np.float64]
    breast_height_age: npt.NDArray[np.float64]
    biological_age: npt.NDArray[np.float64]
    stems_per_ha: npt.NDArray[np.float64]
    origin: npt.NDArray[np.int32]
    management_category: npt.NDArray[np.int32]
    saw_log_volume_reduction_factor: npt.NDArray[np.float64]
    pruning_year: npt.NDArray[np.int16]
    age_when_10cm_diameter_at_breast_height: npt.NDArray[np.int16]
    stand_origin_relative_position: npt.NDArray[np.float64]
    lowest_living_branch_height: npt.NDArray[np.float64]
    tree_category: npt.NDArray[np.str_]
    storey: npt.NDArray[np.int32]
    sapling: npt.NDArray[np.bool_]
    tree_type: npt.NDArray[np.str_]
    tuhon_ilmiasu: npt.NDArray[np.str_]
    latvuskerros: npt.NDArray[np.float64]

    def __init__(self):
        super().__init__(DTYPES_TREE)


class Strata(VectorData):
    size: int
    identifier: npt.NDArray[np.str_]
    species: npt.NDArray[np.int32]
    mean_diameter: npt.NDArray[np.float64]
    mean_height: npt.NDArray[np.float64]
    breast_height_age: npt.NDArray[np.float64]
    biological_age: npt.NDArray[np.int32]
    stems_per_ha: npt.NDArray[np.float64]
    basal_area: npt.NDArray[np.float64]
    origin: npt.NDArray[np.int32]
    management_category: npt.NDArray[np.int32]
    saw_log_volume_reduction_factor: npt.NDArray[np.float64]
    cutting_year: npt.NDArray[np.int32]
    age_when_10cm_diameter_at_breast_height: npt.NDArray[np.int16]
    tree_number: npt.NDArray[np.int32]
    stand_origin_relative_position: npt.NDArray[np.float64]
    lowest_living_branch_height: npt.NDArray[np.float64]
    storey: npt.NDArray[np.int32]
    sapling_stems_per_ha: npt.NDArray[np.float64]
    sapling_stratum: npt.NDArray[np.bool_]
    number_of_generated_trees: npt.NDArray[np.int32]

    def __init__(self):
        super().__init__(DTYPES_STRATA)
