from __future__ import annotations

from typing import AsyncIterator, Awaitable, Callable, Iterator, Protocol, TypeVar, runtime_checkable

from typing_extensions import Concatenate

from cbtoolz.types import P


@runtime_checkable
class PageableRequest(Protocol):
    page_size: int
    page_token: str


@runtime_checkable
class PageableResponse(Protocol):
    next_page_token: str


GrpcRequest = TypeVar("GrpcRequest", bound=PageableRequest)
GrpcResponse = TypeVar("GrpcResponse", bound=PageableResponse)


async def async_pager(
    fn: Callable[Concatenate[GrpcRequest, P], Awaitable[GrpcResponse]],
    request: GrpcRequest,
    *args: P.args,
    **kwargs: P.kwargs,
) -> AsyncIterator[GrpcResponse]:
    completed = False
    while not completed:
        response = await fn(request, *args, **kwargs)
        request.page_token = response.next_page_token
        completed = not response.next_page_token
        yield response


def pager(
    fn: Callable[Concatenate[GrpcRequest, P], GrpcResponse], request: GrpcRequest, *args: P.args, **kwargs: P.kwargs,
) -> Iterator[GrpcResponse]:
    completed = False
    while not completed:
        response = fn(request, *args, **kwargs)
        request.page_token = response.next_page_token
        completed = not response.next_page_token
        yield response
