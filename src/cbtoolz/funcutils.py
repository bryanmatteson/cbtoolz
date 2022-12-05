from __future__ import annotations

import functools
from typing import Any, Callable, Coroutine, Tuple, TypeVar, cast, overload

from typing_extensions import Concatenate, Unpack

from cbtoolz.types import P, R, T, U


def apartial(
    coro: Callable[..., Coroutine[Any, Any, R]], *args: Any, **kwargs: Any,
) -> Callable[..., Coroutine[Any, Any, R]]:
    @functools.wraps(coro)
    async def wrapped(*cargs, **ckwargs):
        return await coro(*args, *cargs, **kwargs, **ckwargs)

    return wrapped


def func_partial(func: Callable[..., R], *args: Any, **kwargs: Any) -> Callable[..., R]:
    @functools.wraps(func)
    def _partial(*a: Any, **kw: Any) -> R:
        return func(*(args + a), **dict(kwargs, **kw))

    return cast(Callable[Concatenate[Unpack[U], P], R], _partial)


def func_rpartial(func: Callable[P, R], *args: Any, **kwargs: Any) -> Callable[..., R]:
    @functools.wraps(func)
    def _rpartial(*a: Any, **kw: Any) -> R:
        return func(*(a + args), **dict(kwargs, **kw))  # type: ignore

    return _rpartial


_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
_F = TypeVar("_F")
_G = TypeVar("_G")
_H = TypeVar("_H")
_T = TypeVar("_T")
_J = TypeVar("_J")


@overload
def compose() -> Callable[[_A], _A]:
    ...


@overload
def compose(__fn1: Callable[P, _B]) -> Callable[P, _B]:
    ...


@overload
def compose(__fn1: Callable[P, _B], __fn2: Callable[[_B], _C]) -> Callable[P, _C]:
    ...


@overload
def compose(__fn1: Callable[P, _B], __fn2: Callable[[_B], _C], __fn3: Callable[[_C], _D]) -> Callable[P, _D]:
    ...


@overload
def compose(
    __fn1: Callable[P, _B], __fn2: Callable[[_B], _C], __fn3: Callable[[_C], _D], __fn4: Callable[[_D], _E],
) -> Callable[P, _E]:
    ...


@overload
def compose(
    __fn1: Callable[P, _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
) -> Callable[P, _F]:
    ...


@overload
def compose(
    __fn1: Callable[P, _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
) -> Callable[P, _G]:
    ...


@overload
def compose(
    __fn1: Callable[P, _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
    __fn7: Callable[[_G], _H],
) -> Callable[P, _H]:
    ...


@overload
def compose(
    __fn1: Callable[P, _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
    __fn7: Callable[[_G], _H],
    __fn8: Callable[[_H], _T],
) -> Callable[P, _T]:
    ...


@overload
def compose(
    __fn1: Callable[P, _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
    __fn7: Callable[[_G], _H],
    __fn8: Callable[[_H], _T],
    __fn9: Callable[[_T], _J],
) -> Callable[P, _J]:
    ...


@overload
def compose(
    __fn1: Callable[P, Any], *__fns: Unpack[Tuple[Unpack[Tuple[Callable, ...]], Callable[..., T]]],
) -> Callable[P, T]:
    ...


def compose(*fns: Callable) -> Callable:
    def _compose(src: Any) -> Any:
        return functools.reduce(lambda acc, f: f(acc), fns, src)

    return _compose


@overload
def rcompose() -> Callable[[_A], _A]:
    ...


@overload
def rcompose(__fn1: Callable[P, _B]) -> Callable[P, _B]:
    ...


@overload
def rcompose(__fn1: Callable[[_B], _C], __fn2: Callable[P, _B]) -> Callable[P, _C]:
    ...


@overload
def rcompose(__fn1: Callable[[_C], _D], __fn2: Callable[[_B], _C], __fn3: Callable[P, _B]) -> Callable[P, _D]:
    ...


@overload
def rcompose(
    __fn1: Callable[[_D], _E], __fn2: Callable[[_C], _D], __fn3: Callable[[_B], _C], __fn4: Callable[P, _B],
) -> Callable[P, _E]:
    ...


@overload
def rcompose(
    __fn1: Callable[[_E], _F],
    __fn2: Callable[[_D], _E],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_B], _C],
    __fn5: Callable[P, _B],
) -> Callable[P, _F]:
    ...


@overload
def rcompose(
    __fn1: Callable[[_F], _G],
    __fn2: Callable[[_E], _F],
    __fn3: Callable[[_D], _E],
    __fn4: Callable[[_C], _D],
    __fn5: Callable[[_B], _C],
    __fn6: Callable[P, _B],
) -> Callable[P, _G]:
    ...


@overload
def rcompose(
    __fn1: Callable[[_G], _H],
    __fn2: Callable[[_F], _G],
    __fn3: Callable[[_E], _F],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_C], _D],
    __fn6: Callable[[_B], _C],
    __fn7: Callable[P, _B],
) -> Callable[P, _H]:
    ...


@overload
def rcompose(
    __fn1: Callable[[_H], _T],
    __fn2: Callable[[_G], _H],
    __fn3: Callable[[_F], _G],
    __fn4: Callable[[_E], _F],
    __fn5: Callable[[_D], _E],
    __fn6: Callable[[_C], _D],
    __fn7: Callable[[_B], _C],
    __fn8: Callable[P, _B],
) -> Callable[P, _T]:
    ...


@overload
def rcompose(
    __fn1: Callable[[_T], _J],
    __fn2: Callable[[_H], _T],
    __fn3: Callable[[_G], _H],
    __fn4: Callable[[_F], _G],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_D], _E],
    __fn7: Callable[[_C], _D],
    __fn8: Callable[[_B], _C],
    __fn9: Callable[P, _B],
) -> Callable[P, _J]:
    ...


def rcompose(*fs: Callable) -> Callable:
    return compose(*reversed(fs))
