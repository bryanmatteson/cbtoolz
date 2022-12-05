import pytest

from cbtoolz.context import ContextModel


class ExampleContext(ContextModel):
    x: int


def test_context_enforces_types():
    with pytest.raises(ValueError):
        ExampleContext(x="hello")  # type: ignore


def test_context_get_outside_context_is_null():
    assert ExampleContext.get() is None


def test_single_context_object_cannot_be_entered_multiple_times():
    context = ExampleContext(x=1)
    with context:
        with pytest.raises(RuntimeError, match="Context already entered"):
            with context:
                pass


def test_copied_context_object_can_be_reentered():
    with ExampleContext(x=1) as context:
        with context.copy():
            assert ExampleContext.must().x == 1


def test_exiting_a_context_more_than_entering_raises():
    context = ExampleContext(x=1)

    with pytest.raises(RuntimeError, match="Asymmetric use of context"):
        with context:
            context.__exit__()


def test_context_exit_restores_previous_context():
    with ExampleContext(x=1):
        with ExampleContext(x=2):
            with ExampleContext(x=3):
                assert ExampleContext.must().x == 3
            assert ExampleContext.must().x == 2
        assert ExampleContext.must().x == 1
    assert ExampleContext.get() is None
