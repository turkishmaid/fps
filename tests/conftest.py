"""Pytest configuration and fixtures."""

import pytest
from collections.abc import Generator
from fun import have_fun


@pytest.fixture(scope="package")
def some_fun() -> Generator[str]:
    """Provide a one-time fun message."""
    print("\n🔴 Have fun!")
    yield "fun"
    print("\n🟢 No fun any more :(")

