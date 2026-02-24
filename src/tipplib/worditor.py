"""A word editor for the terminal."""

from __future__ import annotations
from time import time
from typing import TYPE_CHECKING, NamedTuple

from blessed import Terminal

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Self

term = Terminal()


def echo(*args) -> None:  # noqa: ANN002
    """Print all arguments with no separator and flush the result."""
    output = "".join(str(arg) for arg in args)
    print(output, end="", flush=True)


def beep() -> None:
    """Make a beep sound."""
    echo("\a")


class Config:
    """Configuration singleton for the word editor."""

    _instance = None

    def __new__(cls) -> Self:
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the configuration with default values."""
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        # consider moving these to a separate theme or style class later
        self.dim = term.color_hex("#888888")
        self.bold = term.bright_cyan
        self.alert = term.color_hex("#880000")
        self.success = term.color_hex("#008800")


ALERT_X = 20


class Worditor:
    """Hold and manage the state of an editor for one word."""

    def __init__(self, y0: int, x0: int, on_space: Callable, target: str, ty0: int, tx0: int) -> None:  # noqa: PLR0913
        """Initialize the editor state."""
        # initial position, where the word begins
        self.y0: int = y0
        self.x0: int = x0
        self.ty0: int = ty0
        self.tx0: int = tx0

        # position relative to the visible area -> y=y0, x>=x0
        self.x: int = x0

        # approach: edit each line individually and track edits in the line
        self.word: str = ""
        self.target: str = target

        # callback for when space is pressed, to trigger the next word
        self.on_space: Callable = on_space

        # dirty message from last  time must be preserved across resets, so we can still revoke it after the timeout
        if not hasattr(self, "alert_since"):
            self.alert_since: float = -1.0
            self.alert_length: int = 0
            self.alert_timeout: float = 2.0

        # show the target word at the beginning
        echo(f"{term.move_yx(ty0, tx0)}{target}" + term.clear_eol())
        echo(f"{term.move_yx(y0, x0)}" + term.clear_eol())
        self.set_cursor()

    def reset(self, y0: int, x0: int, on_space: Callable, target: str, ty0: int, tx0: int) -> None:  # noqa: PLR0913
        """Reset the editor to a new initial state."""
        self.__init__(y0, x0, on_space, target, ty0, tx0)

    @staticmethod
    def beep() -> None:
        """Make a beep sound."""
        echo("\a")

    @property
    def max_x(self) -> int:
        """Return the maximum x valid for cursor position."""
        return term.width - 2

    @property
    def in_last_col(self) -> bool:
        """Return True if the cursor is in the last column of the text area."""
        return self.x == self.max_x

    def echo_word(self) -> None:
        """Show the current word at the correct position."""
        if self.target.startswith(self.word.strip()):  # noqa: SIM108
            use_color = Config().success
        else:
            use_color = Config().alert
        echo(f"{term.move_yx(self.y0, self.x0)}{use_color}{self.word}{term.normal}" + term.clear_eol())

    def set_cursor(self) -> None:
        """Move the cursor to the current position, cleaning possible alert."""
        self.revoke_alert()
        self._set_cursor()

    def _set_cursor(self) -> None:
        """Move cursor w/o cleaning alert. ONLY for set_cursor & alert/revoke_alert."""
        echo(term.move_yx(self.y0, self.x))

    def alert(self, message: str | None, color: str = Config().alert) -> None:
        """Show a quick message at the bottom of the terminal, col 20."""
        self.revoke_alert(force=True)
        if message is None:
            return
        echo(term.move_yx(term.height - 1, ALERT_X))
        echo(color + message + term.normal)
        self._set_cursor()  # move back to the current position
        self.alert_since = time()
        self.alert_length = len(message)

    def revoke_alert(self, *, force: bool = False) -> None:
        """Clear the quick message if it has been more than 2 seconds since it was shown."""
        if self.alert_since > 0 and (force or (time() - self.alert_since > self.alert_timeout)):
            echo(term.move_yx(term.height - 1, ALERT_X) + (" " * self.alert_length))
            self._set_cursor()  # move back to the current position
            self.alert_since = -1.0
            self.alert_length = 0
