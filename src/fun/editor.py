from __future__ import annotations
from collections.abc import Callable
from time import time
import sys
from pathlib import Path
from dataclasses import dataclass

from blessed import Terminal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blessed.keyboard import Keystroke

term = Terminal()

INSERT = "INSERT"
COMMAND = "COMMAND"

DIM = term.color_hex("#888888")
ALERT = term.color_hex("#880000")
SUCCESS = term.color_hex("#008800")


class Editor:
    """Hold and manage the state of the editor."""

    def __init__(self) -> None:
        """Initialize the editor state."""
        self.mode: str = INSERT
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
        return term.height - 2

    def set_mode(self, mode: str) -> None:
        """Set the current mode, and show it bottom left."""
        self.mode = mode
        self.echo(term.move_yx(term.height - 1, 0) + f"{DIM}-- {mode} --    {term.normal}")
        self.set_cursor()

    def echo_line(self, y: int = -1) -> None:
        """Show the given line at the correct position."""
        if y == -1:
            y = self.y
        y_eff = y + self.y_offset
        self.echo(f"{term.move_yx(y, 0)}{DIM}{y_eff + 1:3d} | {term.normal}" + self.lines[y_eff] + term.clear_eol())

    def echo_lines_from(self, y: int) -> None:
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

    def alert(self, message: str | None, color: str = ALERT) -> None:
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


key_handler_map: dict[str, Callable[[Editor], None]] = {}


class KeyHandlerRegistry:
    """Registry for key handlers."""

    _instance = None
    _initialized = False

    def __new__(cls) -> "KeyHandlerRegistry":
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the singleton instance if not already done."""
        if not self._initialized:
            self.handlers: dict[str, Callable[[Editor], None]] = {}
            self._initialized = True

    def register(self, func: Callable[[Editor], None]) -> Callable[[Editor], None]:
        """Register a function as a key handler."""
        self.handlers[func.__name__.upper()] = func
        return func

    def get_handler(self, key_name: str) -> Callable[[Editor], None] | None:
        """Get the handler for a given key name."""
        return self.handlers.get(key_name, None)

    def execute_handler(self, key_name: str, editor: Editor) -> bool:
        """Execute the handler for a given key name if it exists."""
        if handler := self.handlers.get(key_name, None):
            handler(editor)
            return True
        return False


def key_handler(func: Callable[[Editor], None]) -> Callable[[Editor], None]:
    """Register a function in the key_handler_map with its name in uppercase as key."""
    KeyHandlerRegistry().register(func)
    return func


def char(e: Editor, key: Keystroke) -> None:
    """Handle normal character input."""
    y_index = e.y + e.y_offset
    line = e.lines[y_index]
    if e.mode == INSERT:
        # insert the character at the current position
        e.lines[y_index] = line[: e.x] + key + line[e.x :]
        e.x += 1
        e.echo_line()
        e.set_cursor()
    else:
        e.beep()  # Not in insert mode, bell sound


@dataclass
class LoadResult:
    success: bool
    message: str
    content: list[str]


def load() -> LoadResult:
    if len(sys.argv) > 1:  # noqa: SIM102
        if sys.argv[1].startswith("--"):
            if sys.argv[1] == "--debug":
                print(KeyHandlerRegistry().handlers)
                input("Press Enter to start the editor...")
        else:
            filename = sys.argv[1]
            here = Path.cwd()
            file_path = here / filename
            try:
                with file_path.open("r") as f:
                    content = [line.rstrip("\n") for line in f]
                return LoadResult(success=True, message=filename, content=content)
            except Exception as ex:
                return LoadResult(success=False, message=f"Error opening file: {ex}", content=[])
    return LoadResult(success=True, message="new file", content=[""])


def vi() -> None:
    """Run main editor loop."""

    lr = load()

    with term.fullscreen(), term.raw():
        e = Editor()
        e.alert(lr.message, color=SUCCESS if lr.success else ALERT)
        e.lines = lr.content

        e.set_mode(INSERT)
        e.echo_lines_from(0)
        e.set_cursor()
        while True:
            key = term.inkey(timeout=0.35)
            if key is None or key == "":
                continue  # No key pressed, continue the loop

            # all thinggs KEY_...
            try:
                if key.name and KeyHandlerRegistry().execute_handler(key.name, e):
                    continue
            except KeyboardInterrupt:
                break  # Exit on Ctrl+C

            if key.is_sequence:
                e.alert(key.name)  # Show the key name as a quick message

                # if key.name == "KEY_BACKSPACE":
                #     # move cursor left and shift all further characters left
                #     # ???
                #     Editor.echo(term.move_yx(e.y, e.x - 1) + " " + term.move_yx(e.y, e.x - 1))
                #     e.x = max(0, e.x - 1)
                # elif key.name == "KEY_ENTER":
                #     Editor.echo(term.clear_eol())  # Move to the next line on Enter
                #     e.y = min(term.height - 1, e.y + 1)
                #     e.x = 0
                # else:
                #     Editor.echo(key.name)  # Print the key name directly
            else:
                char(e, key)
