# from __future__ import annotations

import inspect

# from types import GenericAlias
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Generic,
    Iterable,
    Literal,
    NamedTuple,
    Type,
    Union,
    get_args,
    get_origin,
    overload,
)

from typing_extensions import Concatenate, TypeGuard

from cbtoolz.types import P, T

AnyIterable = Union[Iterable[T], AsyncIterable[T]]
GenericAlias = type(Generic[T])


def is_optional(typ: Type) -> bool:
    if get_origin(typ) is Union:
        args = get_args(typ)
        return len(args) == 2 and None in args
    return False


def is_named_tuple(typ: Type[Any]) -> TypeGuard[Type[NamedTuple]]:
    return isinstance(typ, Type) and all((len(typ.__bases__) == 1, typ.__bases__[0] == tuple, hasattr(typ, "_fields")))


@overload
def get_callable_alias(func: Callable[Concatenate[Any, P], T], *, is_method: Literal[True]) -> Type[Callable[P, T]]:
    ...


@overload
def get_callable_alias(func: Callable[P, T], *, is_method: Literal[False]) -> Type[Callable[P, T]]:
    ...


def get_callable_alias(func: Callable, *, is_method: bool) -> Type[Callable]:
    sig = inspect.signature(func)
    annotations = [*(x.annotation for x in sig.parameters.values()), sig.return_annotation]
    args = [Any if x is inspect.Parameter.empty else x for x in annotations]
    if is_method:
        args = args[1:]
    return GenericAlias(Callable, tuple(args))  # type: ignore


class MethodMeta(type):
    def __getitem__(self, item: Type[Callable[Concatenate[Any, P], T]]) -> Type[Callable[P, T]]:
        return get_callable_alias(item, is_method=True)


class Method(metaclass=MethodMeta):
    ...


class FuncMeta(type):
    def __getitem__(self, item: Type[Callable[P, T]]) -> Type[Callable[P, T]]:
        return get_callable_alias(item, is_method=False)


class Func(metaclass=FuncMeta):
    ...
