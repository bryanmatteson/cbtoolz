from contextvars import ContextVar, Token
from typing import Optional, Type

from pydantic import BaseModel, Extra, PrivateAttr
from typing_extensions import Self

from .decorators import cached_classproperty
from .stringutils import camel_to_snake


class ContextModel(BaseModel):
    """A base model for context data that forbids mutation and extra data while providing a context manager"""

    @cached_classproperty
    def __var__(cls: Type[Self]) -> ContextVar[Self]:  # type: ignore
        return ContextVar(camel_to_snake(cls.__name__).lower())

    _token: Optional[Token] = PrivateAttr(None)

    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
        extra = Extra.forbid

    def __enter__(self):
        if self._token is not None:
            raise RuntimeError("Context already entered. Context enter calls cannot be nested.")
        self._token = self.__var__.set(self)
        return self

    def __exit__(self, *_):
        if not self._token:
            raise RuntimeError("Asymmetric use of context. Context exit called without an enter.")
        self.__var__.reset(self._token)
        self._token = None

    @classmethod
    def get(cls) -> Optional[Self]:
        return cls.__var__.get(None)

    @classmethod
    def must(cls) -> Self:
        return cls.__var__.get(None) or cls()

    def copy(self, **kwargs):
        # Remove the token on copy to avoid re-entrance errors
        new = super().copy(**kwargs)
        new._token = None
        return new
