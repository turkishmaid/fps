"""A word editor for the terminal."""

from __future__ import annotations
from time import time
from typing import TYPE_CHECKING, NamedTuple

from blessed import Terminal

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Self
    from blessed.keyboard import Keystroke


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


class WorditorResult(NamedTuple):
    """Result of a Worditor.run() session."""

    # the target word that was supposed to be typed
    target: str
    # what was actually typed, without the trailing space
    typed: str
    # True if the user typed the target word correctly
    success: bool
    # True if the user exited (with Ctrl+C or Escape)
    # False if they completed the word by typing a space after it
    leave: bool


class Worditor:
    """Hold and manage the state of an editor for one word."""

    def __init__(self, y0: int, x0: int, target: str, ty0: int, tx0: int) -> None:  # noqa: PLR0913
        """Initialize the editor state."""
        # initial position, where the word begins
        self.y0: int = y0
        self.x0: int = x0
        self.ty0: int = ty0
        self.tx0: int = tx0

        # position relative to the visible area -> y=y0, x>=x0
        self.x: int = x0

        # approach: edit each line individually and track edits in the line
        self.current: str = ""
        self.target: str = target

        # callback for when space is pressed, to trigger the next word

        # dirty message from last  time must be preserved across resets, so we can still revoke it after the timeout
        if not hasattr(self, "alert_since"):
            self.alert_since: float = -1.0
            self.alert_length: int = 0
            self.alert_timeout: float = 2.0

        # show the target word at the beginning
        echo(f"{term.move_yx(ty0, tx0)}{target}" + term.clear_eol())
        echo(f"{term.move_yx(y0, x0)}" + term.clear_eol())
        self.set_cursor()

    def reset(self, y0: int, x0: int, target: str, ty0: int, tx0: int) -> None:  # noqa: PLR0913
        """Reset the editor to a new initial state."""
        self.__init__(y0, x0, target, ty0, tx0)

    def run(self) -> WorditorResult:
        """Run the main loop for the word editor."""
        while True:
            key = term.inkey(timeout=0.35)
            if key is None or key == "":
                # alert should disappear after its timeout even if the user doesn't type
                self.revoke_alert()
                # TODO manage resizing
                continue  # No key pressed, continue the loop

            if key.name:
                if key.name in ("KEY_CTRL_C", "KEY_ESCAPE"):
                    return WorditorResult(
                        target=self.target,
                        typed=self.current.strip(),
                        success=self.current.strip() == self.target,
                        leave=True,
                    )

                if key.name == "KEY_BACKSPACE":
                    self.backspace()
                    continue

            if key.is_sequence:
                self.alert(f"? {key.name}")  # Show the key name as a quick message
                continue

            if key == " ":
                if self.current.strip() == "":
                    beep()
                    continue
                self.char(key)
                self.echo_word()
                return WorditorResult(
                    target=self.target,
                    typed=self.current.strip(),
                    success=self.current.strip() == self.target,
                    leave=False,
                )

            self.char(key)
            continue

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
        if self.current.endswith(" "):
            # done with that word
            if self.current.strip() == self.target:  # noqa: SIM108
                use_color = Config().success
            else:
                use_color = Config().alert
            # also echo the target word again, so the user can see what it was in case of an error
            echo(f"{term.move_yx(self.ty0, self.tx0)}{use_color}{self.target}{term.normal}" + term.clear_eol())
        elif self.target.startswith(self.current.strip()):
            # not done: check if correct so far
            use_color = Config().success
        else:
            # not done, but already wrong
            use_color = Config().alert
        echo(f"{term.move_yx(self.y0, self.x0)}{use_color}{self.current}{term.normal}" + term.clear_eol())

    def char(self, key: Keystroke | str) -> None:
        """Insert the character at the current position."""
        self.alert("k: " + str(key))
        char_value = str(key)
        if term.length(char_value) > 1:  # avoid emojis and other weird stuff, but not Umlaute
            beep()
            self.alert(f"ignoring {char_value!r} (len={term.length(char_value)})")
            return
        self.current = self.current + char_value
        self.x += 1
        self.echo_word()
        self.set_cursor()

    def backspace(self) -> None:
        """Delete the character before the current position."""
        if self.x > self.x0:
            self.current = self.current[:-1]
            self.x -= 1
            self.echo_word()
            self.set_cursor()
        else:
            self.beep()  # Can't backspace, bell sound

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
