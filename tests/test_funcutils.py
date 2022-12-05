import operator
from typing import Callable

from cbtoolz.funcutils import compose, func_rpartial, rcompose


def add(x: int) -> Callable[[int], int]:
    return func_rpartial(operator.add, x)


def sub(x: int) -> Callable[[int], int]:
    return func_rpartial(operator.sub, x)


def mul(x: int) -> Callable[[int], int]:
    return func_rpartial(operator.mul, x)


def test_compose():
    assert compose(add(3), mul(2), sub(5))(2) == 5
    assert compose(add(10), mul(4), sub(5), add(-10))(5) == 45


def test_rcompose():
    assert rcompose(add(3), mul(2), sub(5))(2) == -3
    assert rcompose(add(10), mul(4), sub(5), add(-10))(5) == -30
