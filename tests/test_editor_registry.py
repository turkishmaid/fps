"""Unit tests for the KeyHandlerRegistry and key_handler decorator in the pyvilib.editor module."""  # noqa: INP001

import unittest
from enum import Enum
from pyvilib.config import Mode
from pyvilib.editor import KeyHandlerRegistry, key_handler, Editor


class MockMode(Enum):
    """Mock modes for testing."""

    TESTMODE = "TESTMODE"
    OTHERMODE = "OTHERMODE"
    NORMAL = "NORMAL"
    SPECIAL = "SPECIAL"


class TestKeyHandlerRegistry(unittest.TestCase):
    """Unit tests for the KeyHandlerRegistry and key_handler decorator."""

    def setUp(self) -> None:
        """Set up a fresh KeyHandlerRegistry and Editor for each test."""
        # Reset singleton to ensure clean state
        KeyHandlerRegistry._instance = None  # noqa: SLF001
        self.registry = KeyHandlerRegistry()
        # Initialize internal state if needed (like handlers dict)
        if not hasattr(self.registry, "handlers"):
            self.registry.handlers = {}
        # Clear handlers for clean test environment
        self.registry.handlers.clear()

        self.editor = Editor()
        # Mocking methods to avoid terminal output during tests if needed
        self.editor.echo = lambda *args: None  # noqa: ARG005
        self.editor.set_cursor = lambda: None

    def test_basic_registration(self) -> None:
        """Test that a basic key handler can be registered and executed."""

        @key_handler
        def key_test_basic(e: Editor) -> None:
            e.x = 100

        self.editor.mode = Mode.insert
        # Function name in upper case is used as key
        self.assertTrue(self.registry.execute_handler("KEY_TEST_BASIC", self.editor))
        self.assertEqual(self.editor.x, 100)

    def test_mode_registration(self) -> None:
        """Test that a key handler can be registered for a specific mode."""

        @key_handler
        def key_test_mode__testmode(e: Editor) -> None:
            e.x = 200

        self.editor.mode = MockMode.TESTMODE  # type: ignore  # noqa: PGH003
        self.assertTrue(self.registry.execute_handler("KEY_TEST_MODE", self.editor))
        self.assertEqual(self.editor.x, 200)

        # Should not execute in wrong mode if no fallback
        self.editor.mode = MockMode.OTHERMODE  # type: ignore  # noqa: PGH003
        # Since we only registered for TESTMODE, and there is no global handler for KEY_TEST_MODE,
        # it should return False
        self.assertFalse(self.registry.execute_handler("KEY_TEST_MODE", self.editor))

    def test_mode_fallback(self) -> None:
        """Test that a global handler is executed if no mode-specific handler is found."""

        @key_handler
        def key_fallback(e: Editor) -> None:
            e.x = 300

        self.editor.mode = MockMode.OTHERMODE  # type: ignore  # noqa: PGH003
        self.assertTrue(self.registry.execute_handler("KEY_FALLBACK", self.editor))
        self.assertEqual(self.editor.x, 300)

    def test_mode_preference(self) -> None:
        """Test that a mode-specific handler takes precedence over a global handler."""

        # Register global
        @key_handler
        def key_pref_common(e: Editor) -> None:
            e.x = 1

        # Override for SPECIAL mode
        @key_handler
        def key_pref_common__special(e: Editor) -> None:
            e.x = 2

        self.editor.mode = MockMode.NORMAL  # type: ignore  # noqa: PGH003
        self.registry.execute_handler("KEY_PREF_COMMON", self.editor)
        self.assertEqual(self.editor.x, 1)

        self.editor.mode = MockMode.SPECIAL  # type: ignore  # noqa: PGH003
        self.registry.execute_handler("KEY_PREF_COMMON", self.editor)
        self.assertEqual(self.editor.x, 2)
