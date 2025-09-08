from typing import Optional, Any


def get_or_default(maybe_value: Optional[Any], default: Any) -> Any:
    return default if maybe_value is None else maybe_value
