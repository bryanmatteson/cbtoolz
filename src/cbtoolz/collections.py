"""
Utilities for complex operations on Python collections
"""
import copy
from collections import OrderedDict, deque
from collections.abc import Sequence, Set
from dataclasses import fields, is_dataclass
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)
from unittest.mock import Mock

import dpath.util
from pydantic import BaseModel

from cbtoolz.callables import identity

from cbtoolz.types import KT, VT, T


def dict_to_flatdict(
    dct: Dict[KT, Union[Any, Dict[KT, Any]]], _parent: Tuple[KT, ...] = ()
) -> Dict[Tuple[KT, ...], Any]:
    typ = cast(Type[Dict[Tuple[KT, ...], Any]], type(dct))
    items: List[Tuple[Tuple[KT, ...], Any]] = []
    parent = _parent or tuple()

    for k, v in dct.items():
        k_parent = tuple(parent + (k,))
        if isinstance(v, dict):
            items.extend(dict_to_flatdict(v, _parent=k_parent).items())
        else:
            items.append((k_parent, v))
    return typ(items)


def flatdict_to_dict(dct: Dict[Tuple[KT, ...], VT]) -> Dict[KT, Union[VT, Dict[KT, VT]]]:
    typ = cast(Type[Dict[KT, VT]], type(dct))
    result = cast(Dict[KT, Union[VT, Dict[KT, VT]]], typ())
    for key_tuple, value in dct.items():
        current_dict: Dict[KT, Union[VT, Dict[KT, VT]]] = result
        for prefix_key in key_tuple[:-1]:
            current_dict = cast(Dict[KT, Union[VT, Dict[KT, VT]]], current_dict.setdefault(prefix_key, typ()))
        current_dict[key_tuple[-1]] = value

    return result


def ensure_iterable(obj: Union[T, Iterable[T]]) -> Iterable[T]:
    if isinstance(obj, Sequence) or isinstance(obj, Set):
        return obj
    return [cast(T, obj)]


def listrepr(objs: Iterable, sep=" ") -> str:
    return sep.join(repr(obj) for obj in objs)


_T = TypeVar("_T", bound=Union[Mapping[Any, Any], Iterable[Any]])


def remove_nones(args: Union[_T, Any]) -> Union[_T, Any]:
    if isinstance(args, Mapping):
        return cast(_T, {k: v for k, v in args.items() if v})

    if isinstance(args, Iterator):
        return cast(_T, filter(None, args))

    if isinstance(args, (tuple, list, set, frozenset, deque)):
        return type(args)(filter(None, args))

    raise TypeError(f"{type(args)} is not a collection")


def filter_values(args: Union[_T, Any], predicate: Optional[Callable[[Any], bool]] = None) -> Union[_T, Any]:
    if predicate is None:
        predicate = identity

    if isinstance(args, Mapping):
        return cast(_T, {k: v for k, v in args.items() if predicate(v)})

    if isinstance(args, Iterator):
        return cast(_T, filter(predicate, args))

    if isinstance(args, (tuple, list, set, frozenset, deque)):
        return type(args)(filter(predicate, args))

    raise TypeError(f"{type(args)} is not a collection")


_DV = TypeVar("_DV", Dict, Any)


def merge_dicts(d1: Mapping[KT, VT], d2: Mapping[KT, _DV]) -> Dict[KT, Union[VT, _DV]]:
    new_dict: Dict[KT, Union[VT, _DV, Dict[KT, Union[VT, _DV]]]] = dict(copy.copy(d1))
    for k, v in d2.items():
        if isinstance(new_dict.get(k), Mapping) and isinstance(v, Mapping):
            new_dict[k] = merge_dicts(cast(Mapping[KT, VT], new_dict[k]), cast(Mapping[KT, _DV], v))
        else:
            new_dict[k] = v
    return cast(Dict[KT, Union[VT, _DV]], new_dict)


def query_dict(obj: Dict[str, Any], glob: str, separator: str = "/", default: Optional[T] = None) -> Optional[T]:
    return dpath.util.get(obj, glob, separator=separator, default=default)


@overload
def visit_collection(expr: Any, visit: Callable[[Any], Any], collect: Literal[False] = False) -> None:
    ...


@overload
def visit_collection(expr: T, visit: Callable[[Any], Any], collect: Literal[True] = True) -> T:
    ...


@overload
def visit_collection(expr: T, visit: Callable[[Any], Any], collect: bool = False) -> Optional[T]:
    ...


def visit_collection(
    expr: T, visit: Callable[[Any], Any], collect: bool = False, no_visit_types: Tuple[Type[Any], ...] = ()
) -> Optional[T]:
    visit_nested = partial(visit_collection, visit=visit, collect=collect)

    # Get the expression type; treat iterators like lists
    typ = cast(type, list if isinstance(expr, Iterator) else expr.__class__)

    # do not visit mock objects
    if isinstance(expr, Mock):
        return expr if collect else None

    elif isinstance(expr, no_visit_types):
        result = visit(expr)
        return result if collect else None

    elif isinstance(expr, (list, tuple, set, Iterator)):
        result = [visit_nested(o) for o in expr]
        return typ(result) if collect else None

    elif isinstance(expr, (dict, OrderedDict)):
        keys, values = zip(*expr.items()) if expr else ([], [])
        keys = [visit_nested(k) for k in keys]
        values = [visit_nested(v) for v in values]
        return typ(zip(keys, values)) if collect else None

    elif is_dataclass(expr) and not isinstance(expr, type):
        values = [visit_nested(getattr(expr, f.name)) for f in fields(expr)]
        result = {field.name: value for field, value in zip(fields(expr), values)}
        return typ(**result) if collect else None

    elif isinstance(expr, BaseModel):
        values = [visit_nested(getattr(expr, field)) for field in expr.__fields__]
        result = {field: value for field, value in zip(expr.__fields__, values)}
        return typ(**result) if collect else None

    else:
        result = visit(expr)
        return result if collect else None
