from enum import IntEnum, Enum


# Base Enum class for integer-based configuration values
class IntConfigEnum(IntEnum):
    """Base class for integer-based configuration enums."""

    @classmethod
    def from_str[T: IntConfigEnum](cls: type[T], name: str) -> T:
        """Convert a string to an enum value."""
        try:
            return cls[name.upper()]
        except KeyError as e:
            raise ValueError(f"Invalid config value: {name}") from e

    @classmethod
    def from_value(cls, value: int):
        """Convert an integer to an enum value."""
        try:
            return cls(value)
        except ValueError as e:
            raise ValueError(f"Invalid config value: {value}") from e

    def __str__(self):
        return self.name

    def __eq__(self, value):
        if isinstance(value, str):
            return self.name.lower() == value.lower()
        if isinstance(value, int):
            return self.value == value
        return super().__eq__(value)

    def __hash__(self):
        return hash(self.name)


# Base Enum class for string-based configuration values
class StringConfigEnum(Enum):
    """Base class for string-based configuration enums."""

    @classmethod
    def from_str(cls, name: str):
        """Convert a string to an enum value."""
        if name is None:
            return None
        try:
            return cls[name.upper()]
        except KeyError as e:
            raise ValueError(f"Invalid config value: {name}") from e

    def __str__(self):
        return self.name

    def __eq__(self, value):
        if isinstance(value, str):
            return self.name.lower() == value.lower()
        return super().__eq__(value)

    def __hash__(self):
        return hash(self.name)


# Enums for valid app-level configuration values
class RunMode(IntConfigEnum):
    PREPROCESS = 1
    EXPORT_PREPRO = 2
    SIMULATE = 3
    POSTPROCESS = 4
    EXPORT = 5


class StrataOrigin(IntConfigEnum):
    INVENTORY = 1
    COMPUTED = 2
    FORECASTED = 3


class FormationStrategy(StringConfigEnum):
    PARTIAL = 'partial'
    FULL = 'full'


class EvaluationStrategy(StringConfigEnum):
    DEPTH = 'depth'
    CHAINS = 'chains'


class StateFormat(StringConfigEnum):
    FDM = 'fdm'
    VMI12 = 'vmi12'
    VMI13 = 'vmi13'
    XML = 'xml'
    GPKG = 'gpkg'


class StateInputFormat(StringConfigEnum):
    PICKLE = 'pickle'
    JSON = 'json'
    CSV = 'csv'


class StateOutputFormat(StringConfigEnum):
    PICKLE = 'pickle'
    JSON = 'json'
    CSV = 'csv'


class DerivedDataOutputFormat(StringConfigEnum):
    PICKLE = 'pickle'
    JSON = 'json'


# Expose public API
__all__ = [
    "RunMode",
    "StrataOrigin",
    "FormationStrategy",
    "EvaluationStrategy",
    "StateFormat",
    "StateInputFormat",
    "StateOutputFormat",
    "DerivedDataOutputFormat",
]
