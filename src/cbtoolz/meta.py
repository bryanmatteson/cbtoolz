from typing import Any, ClassVar, Dict, Type

from typing_extensions import Self


class Singleton(type):
    __instances__: ClassVar[Dict[Type, Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Self:
        if cls not in cls.__instances__:
            cls.__instances__[cls] = super().__call__(*args, **kwargs)
        return cls.__instances__[cls]
