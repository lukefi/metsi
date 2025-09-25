from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar


T_co = TypeVar("T_co", covariant=True)


@dataclass
class ExportableContainer(Generic[T_co]):
    """ Output container for application results """
    export_objects: List[T_co]
    additional_vars: Optional[List[str]]
