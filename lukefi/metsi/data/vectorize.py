from typing import Any
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.data.vector_model import ReferenceTrees, Strata
from lukefi.metsi.app.utils import MetsiException


CONTAINERS = {
    "reference_trees": ReferenceTrees,
    "tree_strata": Strata
}


def vectorize(stands: list[ForestStand], **operation_params) -> list[ForestStand]:
    """
    Modifies a list of ForestStand objects' reference_trees and tree_strata into a struct-of-arrays style.
    The lists of ReferenceTree and TreeStratum are converted into ReferenceTrees and Strata with numpy arrays for
    each attribute.

    Note that this should be the default representation in the future and the conversion from array-of-structs
    should no longer be necessary.

    Args:
        stands (list[ForestStand]): List of ForestStand objects in standard AoS format

    Returns:
        list[ForestStand]: A reference to the same list is returned after the objects are modified in-place
    """

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
                raise MetsiException(f"Unknown target type '{t}'")
            setattr(stand, f"{t}_soa", container_obj().vectorize(attr_dict))

    return stands


__all__ = ["vectorize"]
