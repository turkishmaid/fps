"""Tests for the fun module using pytest framework.

Run using this command:
    uv run pytest -v -s

Enjoy.
"""  # noqa: INP001

import pytest
from fun import have_fun


class TestHaveFun:
    """Test the have_fun function."""

    def test_have_fun(self, some_fun: str) -> None:
        """Test the have_fun function."""
        print(f"\n👍 Using fixture value: {some_fun}")
        assert have_fun(3) == "Have fun! Have fun! Have fun!"
        assert have_fun(0) == "no fun."
        assert have_fun(1) == "Have fun!"

    def test_1_plus_1(self, some_fun: str) -> None:
        """A simple test to verify that 1 + 1 equals 2."""
        print(f"\n👍 Using fixture value: {some_fun}")
        with pytest.raises(AssertionError):
            assert 1 + 1 == 3  # noqa: PLR2004


def test_have_fun(some_fun: str) -> None:
    """Test the have_fun function."""
    print(f"\n👍 Using fixture value: {some_fun}")
    assert have_fun(3) == "Have fun! Have fun! Have fun!"
    assert have_fun(0) == "no fun."
    assert have_fun(1) == "Have fun!"


def test_1_plus_1(some_fun: str) -> None:
    """A simple test to verify that 1 + 1 equals 2."""
    print(f"\n👍 Using fixture value: {some_fun}")
    with pytest.raises(AssertionError):
        assert 1 + 1 == 3  # noqa: PLR2004
