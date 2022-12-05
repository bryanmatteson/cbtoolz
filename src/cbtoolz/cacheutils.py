from datetime import datetime, timedelta
from typing import Callable, Generic, Optional, Tuple, Union, cast, overload

from cbtoolz.funcutils import func_partial
from cbtoolz.types import UNSET, P, T, Unset


class Result(Generic[T]):
    ttl: Optional[int]
    value: T


GetterResult = Union[Tuple[T, Union[datetime, int, None]], Result[T], T]


class Cached(Generic[T]):
    _fn: Callable[[], GetterResult[T]]
    _value: Union[Optional[T], Unset]
    _expires: Optional[datetime]
    _ttl: Optional[int] = None
    _name: str

    def __init__(
        self, fn: Callable[[], GetterResult[T]], *, name: Optional[str] = None, ttl: Optional[int] = None
    ) -> None:
        self._fn = fn
        self._value = UNSET
        self._ttl = ttl
        self._expires = datetime.utcnow() + timedelta(seconds=ttl) if ttl else None
        self._name = name or fn.__name__

    @property
    def expiration(self) -> Optional[datetime]:
        return self._expires

    @property
    def value(self) -> T:
        return self()

    @property
    def name(self) -> str:
        return self._name

    @property
    def ttl(self) -> Optional[int]:
        return int((self.expiration - datetime.utcnow()).total_seconds()) if self.expiration is not None else None

    def __call__(self) -> T:
        if self._value is UNSET or (self._expires is not None and self._expires < datetime.now()):
            result = self._fn()
            if isinstance(result, tuple):
                if len(result) == 2 and (isinstance(result[1], int) or result[1] is None):
                    value = cast(T, result[0])
                    ttl = cast(Optional[int], result[1])
                    expiration = datetime.now() + timedelta(seconds=ttl) if ttl else None
                elif isinstance(result[1], datetime):
                    value = result[0]
                    expiration = cast(datetime, result[1])
                else:
                    value, expiration = result, None
            elif isinstance(result, Result):
                value, expiration = result.value, datetime.now() + timedelta(seconds=result.ttl) if result.ttl else None
            else:
                value, expiration = result, None

            if expiration is None and self._ttl is not None:
                expiration = datetime.now() + timedelta(seconds=self._ttl)

            self._value = value
            self._expires = expiration

        return cast(T, self._value)

    def __repr__(self) -> str:
        expiration = f"expires {self._expires.isoformat()}" if self._expires is not None else "non-expiring"
        return f"<Cached {self.name!r}={self._value!r}, {expiration}>"


def cache(fn: Callable[P, GetterResult[T]], *args: P.args, **kwargs: P.kwargs) -> Cached[T]:
    return Cached(func_partial(fn, *args, **kwargs))


@overload
def cached(getter: Callable[P, GetterResult[T]], /) -> Callable[P, Cached[T]]:
    ...


@overload
def cached(*, ttl: Optional[int] = None) -> Callable[[Callable[P, T]], Callable[P, Cached[T]]]:
    ...


def cached(
    getter: Optional[Callable[P, GetterResult[T]]] = None, *, ttl: Optional[int] = None
) -> Union[Callable[[Callable[P, T]], Callable[P, Cached[T]]], Callable[P, Cached[T]]]:
    def decorator(fn: Callable[P, GetterResult[T]]) -> Callable[P, Cached[T]]:
        def _cached_getter(*args: P.args, **kwargs: P.kwargs) -> Cached[T]:
            return Cached(func_partial(fn, *args, **kwargs), ttl=ttl)

        return _cached_getter

    return decorator(getter) if getter is not None else decorator
