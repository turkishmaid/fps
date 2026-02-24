"""Unit tests for tipplib."""

import unittest
from unittest.mock import MagicMock, patch
from tipplib.text import TextSource


class TestTextSource(unittest.TestCase):
    """Test the TextSource singleton class."""

    def setUp(self) -> None:
        """Reset the singleton before each test."""
        TextSource._instance = None

    def tearDown(self) -> None:
        """Reset the singleton after each test."""
        TextSource._instance = None

    @patch("tipplib.text.DATAFILE")
    def test_singleton_behavior(self, mock_datafile: MagicMock) -> None:
        """Test that TextSource is a singleton."""
        mock_datafile.exists.return_value = True
        mock_datafile.read_text.return_value = "Line 1"

        ts1 = TextSource()
        ts2 = TextSource()

        self.assertIs(ts1, ts2)
        self.assertTrue(ts1._initialized)
        # Ensure __init__ logic ran only once (loading file)
        # _load_from_file calls read_text. Check call count?
        # But mocking DATAFILE for both instances means we can check calls against the mock.
        # Since _initialized prevents re-running __init__, we expect 1 call to read_text if both are initialized sequentially.
        mock_datafile.read_text.assert_called_once()

    @patch("tipplib.text.DATAFILE")
    def test_load_success(self, mock_datafile: MagicMock) -> None:
        """Test loading lines from a file successfully."""
        mock_datafile.exists.return_value = True
        mock_datafile.read_text.return_value = "  Line 1  \n\nLine 2\n"

        ts = TextSource()
        self.assertEqual(ts._lines, ["Line 1", "Line 2"])

    @patch("tipplib.text.DATAFILE")
    def test_load_file_missing(self, mock_datafile: MagicMock) -> None:
        """Test fallback when file is missing."""
        mock_datafile.exists.return_value = False

        ts = TextSource()
        self.assertEqual(ts._lines, ["Dies ist ein Platzhaltertext.", "Die Datei konnte nicht geladen werden."])

    @patch("tipplib.text.DATAFILE")
    def test_load_error(self, mock_datafile: MagicMock) -> None:
        """Test error handling during file load."""
        mock_datafile.exists.return_value = True
        mock_datafile.read_text.side_effect = Exception("Disk error")

        ts = TextSource()
        self.assertTrue(ts._lines[0].startswith("Error loading file"))

    @patch("tipplib.text.DATAFILE")
    def test_get_line(self, mock_datafile: MagicMock) -> None:
        """Test getting a random line."""
        mock_datafile.exists.return_value = True
        mock_datafile.read_text.return_value = "Line 1\nLine 2"

        ts = TextSource()
        line = ts.get_line()
        self.assertIn(line, ["Line 1", "Line 2"])
        # Check that index was updated
        self.assertNotEqual(ts._current_index, -1)

    @patch("tipplib.text.DATAFILE")
    def test_get_next_line_cycling(self, mock_datafile: MagicMock) -> None:
        """Test cycling through lines with get_next_line."""
        mock_datafile.exists.return_value = True
        mock_datafile.read_text.return_value = "Line 1\nLine 2"

        ts = TextSource()

        # Manually set index to verify sequence from a known state
        # Or just rely on get_line initializing it

        # 1. First call initializes strictly via get_line (random start)
        first = ts.get_next_line()
        self.assertIn(first, ["Line 1", "Line 2"])

        # 2. Sequential calls
        # Let's force a specific index to test deterministic behavior
        ts._lines = ["A", "B", "C"]
        ts._current_index = 0  # "A"

        self.assertEqual(ts.get_next_line(), "B")
        self.assertEqual(ts.get_next_line(), "C")
        self.assertEqual(ts.get_next_line(), "A")  # Wraps around
