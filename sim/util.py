from typing import Optional, Any


def get_or_default(maybe_value: Optional[Any], default: Any) -> Any:
    return default if maybe_value is None else maybe_value


def dict_value(source: dict, key: str) -> Optional[Any]:
    try:
        return source[key]
    except:
        return None
