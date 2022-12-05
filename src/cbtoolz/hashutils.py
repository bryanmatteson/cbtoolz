import hashlib
import json
from pathlib import Path
from typing import Any, Optional, Union


def stable_hash(*args: Union[str, bytes, int]) -> str:
    h = hashlib.md5()
    for a in args:
        if isinstance(a, str):
            a = a.encode()
        elif isinstance(a, int):
            a = bytes(a)
        h.update(a)
    return h.hexdigest()


def file_hash(path: str) -> str:
    contents = Path(path).read_bytes()
    return stable_hash(contents)


def to_qualified_name(obj: Any) -> str:
    return obj.__module__ + "." + obj.__qualname__


def hash_objects(*args, **kwargs) -> Optional[str]:
    try:
        return stable_hash(json.dumps((args, kwargs), sort_keys=True))
    except Exception:
        pass

    return None
