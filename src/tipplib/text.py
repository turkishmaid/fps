"""Provide sample Text for Tippse."""

from __future__ import annotations

import random

from .util import get_reporoot

# file should have max. 70 long lines, and be UTF-8 encoded. Empty lines will be ignored.
DATAFILE = get_reporoot() / "local" / "werther.md"


class TextSource:
    """Provide text for Tippse.

    A Singleton that loads the text from a file and provides it to Tippse.
    """

    _instance: TextSource | None = None

    def __new__(cls) -> TextSource:
        """Create or return the existing singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # type: ignore[attr-defined]
        return cls._instance

    def __init__(self) -> None:
        """Initialize the text source by loading the file."""
        if getattr(self, "_initialized", False):
            return

        self._lines: list[str] = []
        self._current_index: int = -1  # Indicates no line selected yet
        self._load_from_file()
        self._initialized = True

    def _load_from_file(self) -> None:
        """Load lines from DATAFILE, filtering out empty ones."""
        try:
            if DATAFILE.exists():
                text = DATAFILE.read_text(encoding="utf-8")
                # Filter out pure whitespace lines and strip them
                self._lines = [line.strip() for line in text.splitlines() if line.strip()]

            if not self._lines:
                self._lines = ["Dies ist ein Platzhaltertext.", "Die Datei konnte nicht geladen werden."]

        except Exception as e:
            # Robust error handling as requested
            self._lines = [f"Error loading file: {e}", "Please check the configuration."]

    def get_line(self) -> str:
        """Get a random, non-empty line from the text."""
        if not self._lines:
            return ""

        self._current_index = random.randint(0, len(self._lines) - 1)
        return self._lines[self._current_index]

    def get_next_line(self) -> str:
        """Get the next (non-empty) line from the text, cycling back to the beginning if necessary."""
        if not self._lines:
            return "wtf?"

        if self._current_index == -1:
            return self.get_line()

        self._current_index = (self._current_index + 1) % len(self._lines)
        return self._lines[self._current_index]

    def get_next_words(self) -> list[str]:
        """Get the word from the next line."""
        line = self.get_next_line()
        return [w for w in line.split() if w]
