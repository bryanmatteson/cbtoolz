from dataclasses import dataclass

import pydantic
import pytest

from cbtoolz.collections import dict_to_flatdict, flatdict_to_dict, visit_collection


class TestFlatDict:
    @pytest.fixture
    def nested_dict(self):
        return {1: 2, 2: {1: 2, 3: 4}, 3: {1: 2, 3: {4: 5, 6: {7: 8}}}}

    def test_dict_to_flatdict(self, nested_dict):
        assert dict_to_flatdict(nested_dict) == {
            (1,): 2,
            (2, 1): 2,
            (2, 3): 4,
            (3, 1): 2,
            (3, 3, 4): 5,
            (3, 3, 6, 7): 8,
        }

    def test_flatdict_to_dict(self, nested_dict):
        assert flatdict_to_dict(dict_to_flatdict(nested_dict)) == nested_dict


def negative_even_numbers(x):
    if isinstance(x, int) and x % 2 == 0:
        return -x
    return x


EVEN = set()


def visit_even_numbers(x):
    if isinstance(x, int) and x % 2 == 0:
        EVEN.add(x)


@pytest.fixture(autouse=True)
def clear_even_set():
    EVEN.clear()


@dataclass
class SimpleDataclass:
    x: int
    y: int


class SimplePydantic(pydantic.BaseModel):
    x: int
    y: int


class TestVisitCollection:
    @pytest.mark.parametrize(
        "inp,expected",
        [
            (3, 3),
            (4, -4),
            ([3, 4], [3, -4]),
            ((3, 4), (3, -4)),
            ([3, 4, [5, [6]]], [3, -4, [5, [-6]]]),
            ({3: 4, 6: 7}, {3: -4, -6: 7}),
            ({3: [4, {6: 7}]}, {3: [-4, {-6: 7}]}),
            ({3, 4, 5}, {3, -4, 5}),
            (SimpleDataclass(x=1, y=2), SimpleDataclass(x=1, y=-2)),
            (SimplePydantic(x=1, y=2), SimplePydantic(x=1, y=-2)),
        ],
    )
    def test_visit_collection_and_transform_data(self, inp, expected):
        result = visit_collection(inp, visit=negative_even_numbers, collect=True)
        assert result == expected

    @pytest.mark.parametrize(
        "inp,expected",
        [
            (3, set()),
            (4, {4}),
            ([3, 4], {4}),
            ((3, 4), {4}),
            ([3, 4, [5, [6]]], {4, 6}),
            ({3: 4, 6: 7}, {4, 6}),
            ({3: [4, {6: 7}]}, {4, 6}),
            ({3, 4, 5}, {4}),
            (SimpleDataclass(x=1, y=2), {2}),
            (SimplePydantic(x=1, y=2), {2}),
        ],
    )
    def test_visit_collection(self, inp, expected):
        result = visit_collection(inp, visit=visit_even_numbers, collect=False)
        assert result is None
        assert EVEN == expected
