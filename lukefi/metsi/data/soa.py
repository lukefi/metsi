from enum import Enum
from functools import reduce
from typing import Optional, Sequence, TypeVar, Generic, Hashable, ClassVar


T = TypeVar("T", bound=Hashable)


class Soa(Generic[T]):
    props: dict[str, list]
    objects: dict[T, int]
    """
    This class implements a Struct of Arrays data structure for a list of objects T.
    The rationale is to provide a memory-contiguous and thus better performing storage for maintaining state changes for
    an Array of Structs kind of collection, such as a list of objects. Data classes may implement this as an alternative
    for their native dict based property maps or as partial overlays for subsets of properties.
    """

    def __init__(self, old: 'Soa' = None, object_list: list[T] = None, initial_property_names: list[str] = None):
        """
        Constructs a Soa instance, optionally populating it as a copy of given old Soa instance, or with given
        object data and property names.
        """
        self.props = {}
        self.objects = {}

        if old:
            for k, v in old.props.items():
                self.props[k] = v.copy()
            self.objects = old.objects.copy()
        else:
            if object_list:
                for i, o in enumerate(object_list):
                    self.objects[o] = i
            if initial_property_names:
                for name in initial_property_names:
                    self.props[name] = [o.__dict__[name] for o in self.objects]



    def has_property(self, prop_name: str) -> bool:
        """Truth value for a property name being represented in the dataframe."""
        return prop_name in self.props

    def has_object(self, object_reference: T) -> bool:
        """Truth value for object being represented in the dataframe."""
        return object_reference in self.objects

    def get_property_values(self, prop_name: str) -> Optional[list]:
        """Find the list of values for an existing property or None"""
        return self.props.get(prop_name)

    def get_object_properties(self, object_reference: T) -> list[tuple]:
        """
        Find existing property-value pairs for given object or empty list for unknown object or no properties recorded.
        """
        if self.has_object(object_reference):
            i = self.objects[object_reference]
            return [(prop_name, self.props[prop_name][i]) for prop_name in self.props.keys()]
        else:
            return list()

    def get_object_property(self, prop_name: str, object_reference: T) -> Optional:
        """Find existing property value or None for unknown object or property."""
        return self.props[prop_name][self.objects[object_reference]] if self.has_property(prop_name) and self.has_object(object_reference) else None

    def upsert_property_value(self, object_reference: T, prop_name: str, value):
        """
        Set a single property value for the given object. Adds the column for the object and adds the index row if they
        are not yet represented in the dataframe.
        """
        if not self.has_object(object_reference):
            self.upsert_objects([object_reference])
        if not self.has_property(prop_name):
            values = [value if obj == object_reference else obj.__dict__.get(prop_name) for obj in self.objects]
            self.upsert_property_values(prop_name, values)
        else:
            i = self.objects[object_reference]
            self.props[prop_name][i] = value

    def upsert_property_values(self, prop_name: str, values: Sequence):
        """
        Insert or update the values for a given property. Raises ValueError if values length doesn't match dataframe
        dimensions. This function has to blindly trust that given values match the objects/columns they are intended
        for.
        """
        if len(values) != len(self.objects):
            raise ValueError(f"Attempting to insert {len(values)} values into container of {len(self.objects)} values")
        self.props[prop_name] = list(values)


    def upsert_objects(self, object_references: list[T]):
        """
        Insert or update the columns for given objects with values from the objects' properties.
        """
        def split_accumulator(acc: tuple, cur):
            if cur in self.objects:
                acc[0].append(cur)
            else:
                acc[1].append(cur)
            return acc

        old, new = reduce(split_accumulator, object_references, ([], []))

        for obj in old:
            i = self.objects[obj]
            for o, n in zip(self.props.values(), [obj.__dict__.get(prop_name) for prop_name in self.props]):
                o[i] = n
        for obj in new:
            i = len(self.objects)
            self.objects[obj] = i
            values = [obj.__dict__.get(prop_name) for prop_name in self.props]
            for o, n in zip(self.props.values(), values):
                o.append(n)

    def del_objects(self, object_references: list[T]):
        """Drop from dataframe those columns which exist for the given objects."""
        removables = set(object_references) & set(self.objects)
        for rm in removables:
            removed_index = self.objects[rm]
            for k, other_index in self.objects.items():
                if other_index > removed_index:
                    self.objects[k] = other_index - 1
            for prop_values in self.props.values():
                prop_values[removed_index] = None
            self.objects.pop(rm)
        for prop_values in self.props.values():
            prop_values.remove(None)

    def fixate(self):
        for object_reference in self.objects:
            for property in self.props:
                object_reference.__dict__[property] = self.get_object_property(property, object_reference)
        self.props = {}
        self.objects = {}


class Soable:
    """This class implements access-by-precedence to Soa values via object properties."""
    _overlay = ClassVar[Soa]

    def __getattribute__(self, item):
        """Return property from overlay if the overlay exists and the value is known for this object. Return default
        dict-value otherwise."""
        if item.startswith('__'):
            return object.__getattribute__(self, item)
        if isinstance(object.__getattribute__(self, '_overlay'), Soa):
            return object.__getattribute__(self, '_overlay').get_object_property(item, self) or object.__getattribute__(self, item)
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, prop_name: str, value):
        if isinstance(object.__getattribute__(self, '_overlay'), Soa) and type(value) in (int, float, str, tuple, Enum):
            object.__getattribute__(self, '_overlay').upsert_property_value(self, prop_name, value)
        else:
            object.__setattr__(self, prop_name, value)

    @classmethod
    def make_soa(cls, old: Soa = None, object_list: list[T] = None, initial_property_names: list[str] = None):
        """
        Initialize this class instance with a new Soa. Either make a copy from 'old', or initialize a new one with
        optional preallocated data from 'object_list', based on 'initial_property_names'.
        """
        cls._overlay = Soa(old=old, object_list=object_list, initial_property_names=initial_property_names)

    @classmethod
    def forget_soa(cls):
        cls._overlay = None
