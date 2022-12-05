import inspect
from typing import Any, Callable, Dict, OrderedDict, Tuple, Union

from cbtoolz.types import T


def get_call_parameters(fn: Callable, call_args: Tuple[Any, ...], call_kwargs: Dict[str, Any]) -> OrderedDict[str, Any]:
    bound_signature = inspect.signature(fn).bind(*call_args, **call_kwargs)
    bound_signature.apply_defaults()

    return bound_signature.arguments


def parameters_to_args_kwargs(
    fn: Callable, parameters: OrderedDict[str, Any]
) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
    bound_signature = inspect.signature(fn).bind_partial()
    bound_signature.arguments = parameters
    return bound_signature.args, bound_signature.kwargs


def call_with_parameters(fn: Callable, parameters: OrderedDict[str, Any]):
    args, kwargs = parameters_to_args_kwargs(fn, parameters)
    return fn(*args, **kwargs)


def identity(x: T) -> T:
    return x


def is_unbound_method(func: Union[Callable[..., Any], staticmethod, classmethod]) -> bool:
    if isinstance(func, staticmethod):
        return False

    if isinstance(func, classmethod):
        func = func.__func__

    return (
        func.__qualname__ != func.__name__  # not top level
        # not a bound method (self/cls already bound)
        and not inspect.ismethod(func)
        # not nested function
        and not func.__qualname__[: -len(func.__name__)].endswith("<locals>.")
    )
