"""Editor state management and key handler registry."""

from __future__ import annotations
from time import time
from typing import Self, TYPE_CHECKING

from blessed import Terminal

from .config import Config, Mode

if TYPE_CHECKING:
    from collections.abc import Callable

term = Terminal()


class Editor:
    """Hold and manage the state of the editor."""

    def __init__(self) -> None:
        """Initialize the editor state."""

        self.mode: Mode = Mode.insert
        self.command: str = ""

        # position relative to the visible area
        self.y: int = 0
        self.x: int = 0

        # line number will need some room
        self.line_start: int = 6

        # approach: edit each line individually and track edits in the line
        self.lines: list[str] = [""]
        self.y_offset: int = 0  # y + offset = lines index

        # dirty message in last,20
        self.alert_since: float = -1.0
        self.alert_length: int = 0
        self.alert_timeout: float = 2.0

    @staticmethod
    def echo(*args) -> None:  # noqa: ANN002
        """Print all arguments with no separator and flush the result."""
        output = "".join(str(arg) for arg in args)
        print(output, end="", flush=True)

    @staticmethod
    def beep() -> None:
        """Make a beep sound."""
        Editor.echo("\a")

    @property
    def max_y(self) -> int:
        """Return the maximum y valid for cursor position."""
        return term.height - 2

    def set_mode(self, mode: Mode) -> None:
        """Set the current mode, and show it bottom left."""
        self.mode = mode
        self.echo(term.move_yx(term.height - 1, 0) + f"{Config().dim}-- {mode.value} --    {term.normal}")
        self.set_cursor()

    def echo_line(self, y: int = -1) -> None:
        """Show the given line at the correct position."""
        if y == -1:
            y = self.y
        y_eff = y + self.y_offset
        self.echo(
            f"{term.move_yx(y, 0)}{Config().dim}{y_eff + 1:3d} | {term.normal}" + self.lines[y_eff] + term.clear_eol(),
        )

    def echo_lines_from(self, y: int) -> None:
        """Show all lines from the given y to the end of the edit area."""
        for y_ in range(y, self.max_y + 1):
            if y_ + self.y_offset >= len(self.lines):
                self.echo(term.move_yx(y_, 0) + term.clear_eol())
            else:
                self.echo_line(y_)

    def set_cursor(self) -> None:
        """Move the cursor to the current position, cleaning possible alert."""
        self.revoke_alert()  # clear any dirty message before moving the cursor
        self._set_cursor()

    def _set_cursor(self) -> None:
        """Move cursor w/o cleaning alert. ONLY for set_cursor & alert/revoke_alert."""
        line = self.lines[self.y + self.y_offset]
        self.x = min(self.x, len(line))
        self.echo(term.move_yx(self.y, self.x + self.line_start))

    def alert(self, message: str | None, color: str = Config().alert) -> None:
        """Show a quick message at the bottom of the terminal, col 20."""
        if message is None:
            return
        if self.alert_length > 0:
            # right pad with spaces to overwrite previous message
            message = message.ljust(self.alert_length)
        self.echo(term.move_yx(term.height - 1, 20))
        self.echo(color + message + term.normal)
        self._set_cursor()  # move back to the current position
        self.alert_since = time()
        self.alert_length = len(message)

    def revoke_alert(self) -> None:
        """Clear the quick message if it has been more than 2 seconds since it was shown."""
        if self.alert_since > 0 and time() - self.alert_since > self.alert_timeout:
            self.echo(term.move_yx(term.height - 1, 20) + " " * self.alert_length)
            self._set_cursor()  # move back to the current position
            self.alert_since = -1.0
            self.alert_length = 0


class KeyHandlerRegistry:
    """Registry for key handlers."""

    _instance = None
    _initialized = False

    def __new__(cls) -> Self:
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the singleton instance if not already done."""
        if not self._initialized:
            self.handlers: dict[str, dict[str | None, Callable[[Editor], None]]] = {}
            self._initialized = True

    def register(self, func: Callable[[Editor], None]) -> Callable[[Editor], None]:
        """Register a function as a key handler."""
        key_name = func.__name__.upper()
        mode = None

        if "__" in key_name:
            key_name, mode = key_name.rsplit("__", 1)

        if key_name not in self.handlers:
            self.handlers[key_name] = {}
        self.handlers[key_name][mode] = func
        return func

    def execute_handler(self, key_name: str, editor: Editor) -> bool:
        """Execute the handler for a given key name if it exists."""
        if mode_dict := self.handlers.get(key_name, None):
            # precedence: mode-specific handler
            if handler := mode_dict.get(editor.mode.value, None):
                handler(editor)
                return True
            # fallback to global handler if no mode-specific handler found
            if handler := mode_dict.get(None):
                handler(editor)
                return True
        return False

    def show_keybindings(self) -> None:
        """Show the registered keybindings."""
        for key in sorted(self.handlers.keys()):
            if None in self.handlers[key]:
                print(
                    f"{Config().dim}{key}:{term.normal}",
                    f"{Config().bold}{self.handlers[key][None].__name__}{term.normal}",
                )
            else:
                print(f"{Config().dim}{key}:{term.normal}")
            for mode, func in self.handlers[key].items():
                if mode is not None:
                    print(f"  {Config().dim}{mode}:{term.normal} {func.__name__}")
        input("Press Enter to start the editor...")


def key_handler(func: Callable[[Editor], None]) -> Callable[[Editor], None]:
    """Register a function in the key_handler_map with its name in uppercase as key."""
    KeyHandlerRegistry().register(func)
    return func
