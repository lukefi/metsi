from typing import List, Callable
from forestdatamodel.model import ForestStand

def exclude_sapling_trees(stands: List[ForestStand]) -> List[ForestStand]:
    return stands

def exclude_empty_stands(stands: List[ForestStand])-> List[ForestStand]:
    return stands

operation_lookup = {
    'exclude_sapling_trees': exclude_sapling_trees,
    'exclude_empty_stands': exclude_empty_stands
}

def __get_preprocessing_funcs(operations: list) -> List[Callable]:
    funcs = []
    for operation in operations:
        if operation in operation_lookup:
            funcs.append(operation_lookup[operation])
        else:
            raise ValueError(f"{operation} is not a valid preprocessing operation.")
    return funcs

def preprocess_stands(stands: List[ForestStand], operations: list) -> List[ForestStand]:
    """Applies the given preprocessing operations to the given stands
    :returns: preprocessed stands
    """
    funcs = __get_preprocessing_funcs(operations)
    for func in funcs:
        stands = func(stands)
    return stands