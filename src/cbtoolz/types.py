from __future__ import annotations

from typing import Any, Callable, Dict, MutableMapping, TypeVar, Union
from urllib.parse import parse_qs, urlencode

from typing_extensions import ParamSpec, TypeVarTuple

T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
C = TypeVar("C", bound=Callable)

P = ParamSpec("P")
P1 = ParamSpec("P1")
R = TypeVar("R")
T = TypeVar("T")
U = TypeVarTuple("U")
N = TypeVar("N", int, float)
KT = TypeVar("KT")
VT = TypeVar("VT")
Exc = TypeVar("Exc", bound=BaseException)

T0 = TypeVar("T0")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
T9 = TypeVar("T9")


Out = TypeVar("Out", covariant=True)
In = TypeVar("In", contravariant=True)
Ret = TypeVar("Ret", covariant=True)


class Unset:
    def __eq__(self, other):
        return isinstance(other, Unset)

    def __bool__(self) -> bool:
        return False

    def __copy__(self) -> Unset:
        return self

    def __deepcopy__(self) -> "Unset":
        return self

    def __str__(self) -> str:
        return "<UNSET>"

    def __repr__(self) -> str:
        return "<UNSET>"

    def __hash__(self) -> int:
        return hash(str(self))


UNSET = Unset()


class Params(MutableMapping[str, Any]):
    _params: Dict[str, Any]
    _separator: str

    def __init__(self, value: Union[str, Dict[str, Any]] = {}, *, separator: str = ","):
        self._separator = separator
        if isinstance(value, str):
            self._params = parse_qs(value, separator=separator)
        else:
            self._params = value

    def __getitem__(self, key: str):
        return self._params[key]

    def __setitem__(self, key: str, item: Any):
        self._params[key] = item

    def __delitem__(self, key: str):
        del self._params[key]

    def __iter__(self):
        return iter(self._params)

    def __len__(self):
        return len(self._params)

    def __str__(self) -> str:
        return urlencode(self._params, doseq=True).replace("&", self._separator)
