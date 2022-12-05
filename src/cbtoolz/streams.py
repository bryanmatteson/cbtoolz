import io
from typing import Iterable, Iterator, Union


class StreamIterable(io.RawIOBase):
    _source: Iterator[bytes]
    _current: bytearray

    def __init__(self, source: Iterable[bytes]) -> None:
        self._source = iter(source)
        self._current = bytearray()

    def readable(self) -> bool:
        return True

    def readinto(self, target: Union[bytearray, memoryview]) -> int:
        requested = len(target)
        if not isinstance(target, memoryview):
            target = memoryview(target)

        target = target.cast("B")
        if target.nbytes == 0:
            return 0

        while len(self._current) < requested:
            chunk = next(self._source, b"")
            if not chunk:
                break
            self._current.extend(chunk)

        size = min(len(self._current), requested)
        target[:size] = self._current[:size]
        self._current = self._current[size:]
        return size
