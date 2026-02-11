import unittest
from fun.editor import KeyHandlerRegistry, key_handler, Editor, INSERT

class TestKeyHandlerRegistry(unittest.TestCase):
    def setUp(self):
        # Reset singleton to ensure clean state
        KeyHandlerRegistry._instance = None
        self.registry = KeyHandlerRegistry()
        self.editor = Editor()
        # Mocking methods to avoid terminal output during tests if needed
        self.editor.echo = lambda *args: None
        self.editor.set_cursor = lambda: None

    def test_basic_registration(self):
        @key_handler
        def key_test_basic(e: Editor) -> None:
            e.x = 100

        self.editor.mode = INSERT
        # Function name in upper case is used as key
        self.assertTrue(self.registry.execute_handler("KEY_TEST_BASIC", self.editor))
        self.assertEqual(self.editor.x, 100)

    def test_mode_registration(self):
        @key_handler
        def key_test_mode__testmode(e: Editor) -> None:
            e.x = 200

        self.editor.mode = "TESTMODE"
        self.assertTrue(self.registry.execute_handler("KEY_TEST_MODE", self.editor))
        self.assertEqual(self.editor.x, 200)
        
        # Should not execute in wrong mode if no fallback
        self.editor.mode = "OTHERMODE"
        # Since we only registered for TESTMODE, and there is no global handler for KEY_TEST_MODE,
        # it should return False
        self.assertFalse(self.registry.execute_handler("KEY_TEST_MODE", self.editor))

    def test_mode_fallback(self):
        @key_handler
        def key_fallback(e: Editor) -> None:
            e.x = 300
        
        self.editor.mode = "OTHERMODE"
        self.assertTrue(self.registry.execute_handler("KEY_FALLBACK", self.editor))
        self.assertEqual(self.editor.x, 300)

    def test_mode_preference(self):
        # Register global
        @key_handler
        def key_pref_common(e: Editor) -> None:
            e.x = 1
        
        # Override for SPECIAL mode
        @key_handler
        def key_pref_common__special(e: Editor) -> None:
            e.x = 2

        self.editor.mode = "NORMAL"
        self.registry.execute_handler("KEY_PREF_COMMON", self.editor)
        self.assertEqual(self.editor.x, 1)

        self.editor.mode = "SPECIAL"
        self.registry.execute_handler("KEY_PREF_COMMON", self.editor)
        self.assertEqual(self.editor.x, 2)
