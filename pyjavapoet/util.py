from typing import Any


def is_ascii_upper(s: str) -> bool:
    return s.isascii() and s.isupper()

def deep_copy(obj: Any) -> Any:
    if isinstance(obj, list):
        return [deep_copy(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: deep_copy(value) for key, value in obj.items()}
    elif hasattr(obj, "copy"):
        return obj.copy()
    else:
        return obj