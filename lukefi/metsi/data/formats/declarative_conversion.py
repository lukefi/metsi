from typing import Any, Tuple, Callable, List

class Conversion():

    def __init__(self, conf_f: Callable, indices: Tuple = (), object_type: Any = None):
        self.conf_f = conf_f
        self.indices = indices
        self.object_type = object_type

    def extract_index(self, data: List):
        return ( data[i] for i in self.indices )

    def __call__(self, data: List, obj: Any):
        datavars = self.extract_index(data)
        obj = () if self.object_type is None else (obj,)
        input = [*datavars, *obj]
        return self.conf_f(*input)


class ConversionMapper():

    def __init__(self, conversion_declaration: dict[str, Any]):
          self.declaration = conversion_declaration
    
    def _filter_declaration_by_instance(self, obj: Any) -> dict[str, Any]:
        subset = {}
        for k, dconv in self.declaration.items():
            if not dconv.object_type or (dconv.object_type and isinstance(obj, dconv.object_type)):
                subset.update( { k : dconv } )
        return subset

    def apply_conversions(self, obj: Any, source: list[Any]) -> dict[str: Any]:
        """ Applies declared conversions with source data and
            adds the mapping result to the given object.
            
            return: Given object updated with the conversion results
            """
        subset = self._filter_declaration_by_instance(obj)
        for k, dconv in subset.items():
            conv_result = dconv(source, obj)
            setattr(obj, k, conv_result) 
        return obj
    

__all__ = ['ConversionMapper', 'Conversion']
