"""Tests for the fun module using pytest framework.

Run using this command:
    uv run pytest -v -s

Enjoy.
"""  # noqa: INP001

import unittest
from fun import have_fun

class TestHaveFun(unittest.TestCase):
    """Test the have_fun function."""

    def test_have_fun(self) -> None:
        """Test have_fun function."""
        self.assertEqual(have_fun(3), "Have fun! Have fun! Have fun!")
        self.assertEqual(have_fun(0), "no fun.")
        self.assertEqual(have_fun(1), "Have fun!")

if __name__ == "__main__":
    unittest.main(verbosity=2)
