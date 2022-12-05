from __future__ import annotations

import builtins
import inspect
import io
import itertools
import operator
from collections import defaultdict
from functools import reduce
from queue import Queue
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    Mapping,
    MutableSequence,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    overload,
)

import more_itertools
from typing_extensions import Unpack

from cbtoolz.callables import identity
from cbtoolz.streams import StreamIterable

from cbtoolz.types import T0, T1, T2, T3, Out, T, U

Predicate = Callable[[T], bool]


def empty() -> Iter[None]:
    return Iter(iter(()))


def count(start: int = 0, step: int = 1):
    return Iter(itertools.count(start, step))


def repeat(elem: T, times: Optional[int] = None) -> Iter[T]:
    it = itertools.repeat(elem) if times is None else itertools.repeat(elem, times=times)
    return Iter(it)


def sliced(seq: Sequence[T], n: int) -> Iter[Sequence[T]]:
    return Iter(more_itertools.sliced(seq, n))


def repeatfunc(func: Callable[..., T], *args: Any, times: Optional[int] = None) -> Iter[T]:
    return Iter(more_itertools.repeatfunc(func, times, *args))


def from_queue(q: Queue[T], timeout: Optional[int] = None, sentinel: object = None) -> Iter[T]:
    return repeatfunc(q.get, timeout).takewhile(lambda v: v is not sentinel)


def chained(*iterables: Iterable[Out]) -> Iter[Out]:
    return Iter(itertools.chain(*iterables))


def concat(left: Iterable[T0], right: Iterable[T1]) -> Iter[T0 | T1]:
    return Iter(itertools.chain(left, right))


def map(fn: Callable[[T], T0], it: Iterable[T]) -> Iter[T0]:
    return Iter(builtins.map(fn, it))


def starmap(it: Iterable[Iterable], fn: Callable[..., T]) -> Iter[T]:
    return Iter(fn(*a) for a in zip(*it))


def unzip(it: Iterable[Sequence[Any]]) -> Tuple[Iter[Any]]:
    return tuple(Iter(x) for x in more_itertools.unzip(it))


@overload
def range(stop: int, /) -> Iter[int]:
    ...


@overload
def range(start: int, stop: int, step: int = 1, /) -> Iter[int]:
    ...


def range(start_or_stop: int, stop: Optional[int] = None, step: int = 1, /) -> Iter[int]:
    return Iter(builtins.range(start_or_stop, stop, step) if stop is not None else builtins.range(start_or_stop))


def flatmap(fn: Callable[[T], Iterable[Out]], itr: Iterable[T]) -> Iter[Out]:
    return Iter(value for item in iter(itr) for value in fn(item))


class Iter(Iterator[Out], Generic[Out]):
    it: Iterator[Out]

    def __init__(self, it: Iterable[Out]) -> None:
        if isinstance(it, Iter):
            self.it = it.it
        else:
            self.it = iter(it)

    def __next__(self) -> Out:
        return next(self.it)

    def __iter__(self) -> Iter[Out]:
        return self

    def skip(self, n: int) -> Iter[Out]:
        more_itertools.consume(self, n=n)
        return self

    def drain(self) -> None:
        more_itertools.consume(self)

    def queue(self, q: Queue[Out]) -> None:
        self.each(q.put)

    def each(self, fn: Callable[[Out], Any]) -> None:
        for v in self:
            fn(v)

    def eachstar(self: Iter[Tuple[Unpack[U]]], fn: Callable[[Unpack[U]], Any]) -> None:
        for v in self:
            fn(*v)

    def sink(self, g: Generator[None, Out, Any], close_when_done: bool = False) -> None:
        if inspect.getgeneratorstate(g) == "GEN_CREATED":
            next(g)

        for v in self:
            g.send(v)

        if close_when_done:
            g.close()

    def pluck(self, kind: Type[T0], attr: str) -> Iter[T0]:
        return self.map(operator.attrgetter[T0](attr))

    @overload
    def zip(
        self: Iter[T], __it1: Iterable[T0], __it2: Iterable[T1], __it3: Iterable[T2], __it4: Iterable[T3]
    ) -> Iter[Tuple[T, T0, T1, T2, T3]]:
        ...

    @overload
    def zip(self: Iter[T], __it1: Iterable[T0], __it2: Iterable[T1], __it3: Iterable[T2]) -> Iter[Tuple[T, T0, T1, T2]]:
        ...

    @overload
    def zip(self: Iter[T], __it1: Iterable[T0], __it2: Iterable[T1]) -> Iter[Tuple[T, T0, T1]]:
        ...

    @overload
    def zip(self: Iter[T], __it1: Iterable[T0]) -> Iter[Tuple[T, T0]]:
        ...

    def zip(self: Iter[Any], *iterables: Iterable[Any]) -> Iter[Tuple[Any, ...]]:
        return Iter(tuple(x) for x in zip(self, *iterables))

    def collect_into(self, seq: MutableSequence[Out]) -> None:
        seq.extend(self)

    def to_list(self) -> List[Out]:
        return list(self)

    def to_tuple(self) -> Tuple[Out, ...]:
        return tuple(self)

    def to_set(self) -> Set[Out]:
        return set(self)

    def to_dict(self: Iter[Tuple[T0, T1]]) -> Dict[T0, T1]:
        return dict(self)

    def enumerate(self) -> Iter[Tuple[int, Out]]:
        return Iter((k, v) for k, v in enumerate(self.it))

    def map(self, fn: Callable[[Out], T]) -> Iter[T]:
        return map(fn, self)

    def filter(self, fn: Predicate[T0], transform: Callable[[Out], T0] = identity) -> Iter[T0]:
        return Iter(x for x in self if fn(transform(x)))

    def prepend(self, it: Iterable[T0]) -> Iter[T0 | Out]:
        return concat(it, self)

    def starfilter(self: Iter[Tuple[Unpack[U]]], fn: Callable[[Unpack[U]], bool]):
        return Iter((v for v in self if fn(*v)))

    def reduce(self, func: Callable[[T0, Out], T0], args: T0):
        return reduce(func, self, *args)

    def cycle(self) -> Iter[Out]:
        return Iter(itertools.cycle(self))

    def accumulate(self, func=None, *, initial=None):
        return Iter(itertools.accumulate(self, func, initial=initial))

    def concat(self, *iterables: Iterable[Out]):
        return Iter(itertools.chain(self, *iterables))

    def flatten(self: Iter[Iterable[T]]) -> Iter[T]:
        return Iter(itertools.chain.from_iterable(self))

    def compress(self, selectors) -> Iter[Out]:
        return Iter(itertools.compress(self, selectors))

    def dropwhile(self, pred) -> Iter[Out]:
        return Iter(itertools.dropwhile(pred, self))

    def filterfalse(self, pred: Callable[[Out], bool]):
        return Iter(itertools.filterfalse(pred, self))

    def grouped(self, fn: Callable[[Out], T0]) -> defaultdict[T0, List[Out]]:
        groups: defaultdict[T0, List[Out]] = defaultdict(list)
        for x in self:
            groups[fn(x)].append(x)
        return groups

    def groupby(self, key: Callable[[Out], T0]) -> Iter[Tuple[T0, Iter[Out]]]:
        return starmap(itertools.groupby(self, key), lambda k, g: (k, Iter(g)))

    def take(self, n: int) -> Iter[Out]:
        return Iter(itertools.islice(self, n))

    def values(self: Iter[Tuple[Any, T1]]) -> Iter[T1]:
        return self.map(operator.itemgetter(1))

    def keys(self: Iter[Tuple[T0, Any]]) -> Iter[T0]:
        return self.map(operator.itemgetter(0))

    @overload
    def elem(self: Iter[Tuple[T0, Unpack[Tuple[Any, ...]]]], n: Literal[0]) -> Iter[T0]:
        ...

    @overload
    def elem(self: Iter[Tuple[Any, T0, Unpack[Tuple[Any, ...]]]], n: Literal[1]) -> Iter[T0]:
        ...

    @overload
    def elem(self: Iter[Tuple[Any, Any, T0, Unpack[Tuple[Any, ...]]]], n: Literal[2]) -> Iter[T0]:
        ...

    @overload
    def elem(self: Iter[Tuple[Any, Any, Any, T0, Unpack[Tuple[Any, ...]]]], n: Literal[3]) -> Iter[T0]:
        ...

    @overload
    def elem(self: Iter[Tuple[Any, Any, Any, Any, T0, Unpack[Tuple[Any, ...]]]], n: Literal[4]) -> Iter[T0]:
        ...

    def elem(self: Iter[Tuple[Any, ...]], n: int) -> Iter[Any]:
        return self.map(operator.itemgetter(n))

    def items(self: Iter[Mapping[T0, T1]]) -> Iter[Tuple[T0, T1]]:
        return Iter((k, v) for o in self for k, v in o.items())

    def starmap(self: Iter[Tuple[Unpack[U]]], func: Callable[[Unpack[U]], T]) -> Iter[T]:
        return Iter(itertools.starmap(func, self))

    def takewhile(self, pred: Callable[[Out], bool]) -> Iter[Out]:
        return Iter(itertools.takewhile(pred, self))

    def fanout(self, n: int):
        return Iter(Iter(x) for x in itertools.tee(self, n))

    def chunked(self, n: int):
        return Iter(more_itertools.chunked(self, n))

    def ichunked(self, n: int):
        return Iter(Iter(x) for x in more_itertools.ichunked(self, n))

    def distribute(self, n: int):
        return Iter(Iter(x) for x in more_itertools.distribute(n, self))

    def divide(self, n: int):
        return Iter(Iter(x) for x in more_itertools.divide(n, self))

    def grouper(self, n: int, fillvalue: T) -> Iter[Tuple[Out | T, ...]]:
        return Iter(more_itertools.grouper(self, n, fillvalue=fillvalue))

    def ipartition(self, pred: Callable[[Out], bool]) -> Iter[Iter[Out]]:
        return Iter(self.partition(pred))

    def pairwise(self) -> Iter[Tuple[Out, Out]]:
        return Iter(more_itertools.pairwise(self))

    def count_cycle(self, n: int | None = None) -> Iter[Tuple[int, Out]]:
        return Iter(more_itertools.count_cycle(self, n=n))

    def intersperse(self, e: T0, n: int = 1) -> Iter[Out | T0]:
        return Iter(more_itertools.intersperse(e, self, n=n))

    def then(self, fn: Callable[[], Any]):
        def _handler():
            try:
                yield from self
            finally:
                fn()

        return Iter(_handler())

    def side_effect(
        self,
        func: Callable[[Out], object],
        *args: Any,
        chunk_size: Optional[int] = None,
        before: Optional[Callable[[], Any]] = None,
        after: Optional[Callable[[], Any]] = None,
    ) -> Iter[Out]:
        def _fn(*value: Any):
            return func(*value, *args)

        return Iter(more_itertools.side_effect(_fn, self, chunk_size=chunk_size, before=before, after=after))

    def print(self, template: str = "{i}: {v}") -> Iter[Out]:
        def _print(elem):
            i, v = elem
            print(template.format(**locals()))

        return self.enumerate().side_effect(_print).values()

    def send_also(self, chan: Generator[None, Out, Any]):
        if inspect.getgeneratorstate(chan) == inspect.GEN_CREATED:
            next(chan)

        def writer(value):
            chan.send(value)

        return self.side_effect(writer)

    def as_buffered_reader(self: Iter[bytes], buffer_size: int = io.DEFAULT_BUFFER_SIZE) -> io.BufferedReader:
        return io.BufferedReader(StreamIterable(self), buffer_size=buffer_size)

    @overload
    def partition(self, pred: Callable[[Out], bool]) -> Tuple[Iter[Out], Iter[Out]]:
        ...

    @overload
    def partition(self, pred: Callable[[Out], bool], into: MutableSequence[Out]) -> Iter[Out]:
        ...

    def partition(self, pred: Callable[[Out], bool], into: Optional[MutableSequence[Out]] = None):
        falsey, truthy = more_itertools.partition(pred, self)
        if into is not None:
            into.extend(truthy)
            return Iter(falsey)
        return (Iter(falsey), Iter(truthy))

    @overload
    def unzip(self: Iter[Tuple[T0, T1]]) -> Tuple[Iter[T0], Iter[T1]]:
        ...

    @overload
    def unzip(self: Iter[Tuple[T0, T1, T2]]) -> Tuple[Iter[T0], Iter[T1], Iter[T2]]:
        ...

    @overload
    def unzip(self: Iter[Tuple[T0, T1, T2, T3]]) -> Tuple[Iter[T0], Iter[T1], Iter[T2], Iter[T3]]:
        ...

    @overload
    def unzip(self: Iter[Tuple[Any, ...]]) -> Tuple[Iter[Any], ...]:
        ...

    def unzip(self: Iter[Tuple[Any, ...]]) -> Tuple[Iter[Any], ...]:
        return unzip(self)

    @overload
    def tee(self, n: Literal[5]) -> Tuple[Iter[Out], Iter[Out], Iter[Out], Iter[Out], Iter[Out]]:
        ...

    @overload
    def tee(self, n: Literal[4]) -> Tuple[Iter[Out], Iter[Out], Iter[Out], Iter[Out]]:
        ...

    @overload
    def tee(self, n: Literal[3]) -> Tuple[Iter[Out], Iter[Out], Iter[Out]]:
        ...

    @overload
    def tee(self, n: Literal[2]) -> Tuple[Iter[Out], Iter[Out]]:
        ...

    @overload
    def tee(self) -> Tuple[Iter[Out], Iter[Out]]:
        ...

    @overload
    def tee(self, n: int) -> Tuple[Iter[Out], ...]:
        ...

    def tee(self, n=2):
        return tuple(Iter(x) for x in itertools.tee(self, n))
