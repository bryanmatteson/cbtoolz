import functools
import threading
from collections import defaultdict
from typing import Any, Callable, Coroutine, Dict, Generic, Optional, Type, cast

from cbtoolz.types import UNSET, P, R, T


def copy_param_signature(src: Callable[P, R]) -> Callable[[Callable[..., R]], Callable[P, R]]:
    def _inner(target: Callable[..., R]) -> Callable[P, R]:
        return cast(Callable[P, R], target)

    return _inner


def once(func: Callable[P, T]) -> Callable[P, T]:
    lock = threading.Lock()

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if wrapper.__value is not UNSET:
            return wrapper.__value

        with lock:
            wrapper.__value = func(*args, **kwargs)

        return wrapper.__value

    wrapper.__value = UNSET
    return wrapper


class classproperty(Generic[R]):
    def __init__(self: "classproperty[R]", fn: Callable[..., R]) -> None:
        self.fn = fn

    def __get__(self, instance: T, owner: Type[T]) -> R:
        return self.fn(owner)


class cached_classproperty(Generic[R]):
    def __init__(self: "cached_classproperty[R]", fn: Callable[..., R]) -> None:
        self.fn = fn
        self.attrname = None
        self.__doc__ = fn.__doc__
        self.lock = threading.RLock()
        self.cache: Dict[str, R] = {}

    def __set_name__(self, owner: Type[Any], name: str):
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(
                "Cannot assign the same cached_property to two different names " f"({self.attrname!r} and {name!r})."
            )

    def __get__(self, instance: T, owner: Type[T]) -> R:
        if self.attrname is None:
            raise TypeError("Cannot use cached_property instance without calling __set_name__ on it.")

        val = self.cache.get(self.attrname, UNSET)
        if val is UNSET:
            with self.lock:
                val = self.cache.get(self.attrname, UNSET)
                if val is UNSET:
                    val = self.fn(owner)
                    self.cache[self.attrname] = val
        return cast(R, val)


def reentrant(cls: Type[T]) -> Type[T]:
    """
    Modifies a class so that its ``__enter__`` / ``__exit__`` (or ``__aenter__`` / ``__aexit__``)
    methods track the number of times it has been entered and exited and only actually invoke
    the ``__enter__()`` method on the first entry and ``__exit__()`` on the last exit.
    """

    loans: Dict[T, int] = defaultdict(lambda: 0)
    previous_enter: Optional[Callable[[T], T]] = getattr(cls, "__enter__", None)
    previous_exit: Optional[Callable[[T, Any, Any, Any], None]] = getattr(cls, "__exit__", None)
    previous_aenter: Optional[Callable[[T], Coroutine[Any, Any, T]]] = getattr(cls, "__aenter__", None)
    previous_aexit: Optional[Callable[[T, Any, Any, Any], Coroutine[Any, Any, None]]] = getattr(cls, "__aexit__", None)

    def __enter__(self: T) -> T:
        loans[self] += 1
        if loans[self] == 1 and callable(previous_enter):
            previous_enter(self)

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        assert loans[self]
        loans[self] -= 1
        if loans[self] == 0 and callable(previous_exit):
            return previous_exit(self, exc_type, exc_val, exc_tb)

    async def __aenter__(self: T) -> T:
        loans[self] += 1
        if loans[self] == 1 and callable(previous_aenter):
            await previous_aenter(self)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        assert loans[self]
        loans[self] -= 1
        if loans[self] == 0:
            del loans[self]
            if callable(previous_aexit):
                return await previous_aexit(self, exc_type, exc_val, exc_tb)

    if previous_enter and previous_exit:
        setattr(cls, "__enter__", __enter__)
        setattr(cls, "__exit__", __exit__)
    elif previous_aenter and previous_aexit:
        setattr(cls, "__aenter__", __aenter__)
        setattr(cls, "__aexit__", __aexit__)

    return cls
