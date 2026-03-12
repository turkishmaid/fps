"""A word editor for the terminal."""

from __future__ import annotations
from time import time
from typing import TYPE_CHECKING, NamedTuple
from dataclasses import dataclass, field

from blessed import Terminal

from .util import hr_time

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Self
    from blessed.keyboard import Keystroke


term = Terminal()


def echo(*args) -> None:  # noqa: ANN002
    """Print all arguments with no separator and flush the result."""
    output = "".join(str(arg) for arg in args)
    print(output, end="", flush=True)


def echo_at(y: int, x: int, *args: str) -> None:
    """Print all arguments at a specific position with no separator and flush the result."""
    output = "".join(str(arg) for arg in args)
    y0, x0 = term.get_location()
    print(f"{term.move_yx(y, x)}{output}{term.move_yx(y0, x0)}", end="", flush=True)


def beep() -> None:
    """Make a beep sound."""
    echo("\a")


def shorten(word: str, target: str) -> str:
    """Shorten the word to fit the target length, keeping trailing space."""
    assert word.endswith(" ")
    word = word[:-1]
    # won't matter whether len() or term.length() b/c we only use single-width chars in the target
    max_length = len(target)
    if len(word) <= max_length:
        return f"{word} "  # word is short enough, just add the space back
    # shorten the word and add an ellipsis
    return f"{word[:max_length - 1]}… "


class Config:
    """Configuration singleton for the word editor."""

    _instance = None

    def __new__(cls) -> Config:
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


@dataclass
class WorditorResult:
    """Result of a Worditor.run() session."""

    # the target word that was supposed to be typed
    target: str
    # what was actually typed, without the trailing space
    typed: str = ""
    # True if the user typed the target word correctly
    success: bool = False
    # True if the user exited (with Ctrl+C or Escape)
    # False if they completed the word by typing a space after it
    leave: bool = False
    # very precise typing log
    log: list[tuple[float, str]] = field(default_factory=list)

    def log_key(self, key: Keystroke) -> None:
        """Log a character with the current timestamp."""
        if key is None or key == "":
            return  # No key pressed, don't log
        char: str = key.name if hasattr(key, "name") and key.name else str(key)
        if char == " ":
            char = "SPACE"
        self.log.append((time(), char))

    def log_done(self, typed: str) -> None:
        """Mark the log as done by adding a final entry with an empty char."""
        self.typed = typed.strip()
        self.success = self.typed == self.target
        self.leave = self.log[-1][1] in ("KEY_CTRL_C", "KEY_ESCAPE")

    def render(self, time_base: float) -> None:
        """Render the result as a string for display."""
        c = Config()  # LOLcode incoming
        dim, bold, bad, good, nn = (c.dim, c.bold, c.alert, c.success, term.normal)
        target = f"{dim}{self.target}{nn}"
        bunt = good if self.success else bad
        typed = f"{bunt}{self.typed}{nn}"
        left = f"{bad}{bold}LEFT{nn}" if self.leave else ""
        print(f"{target} {typed} {left}")
        t0 = time_base
        mess = "  ".join(f"{dim}{t - t0:.2f}{nn} {c}" for t, c in self.log)
        print("    ", mess)


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
        echo(f"{term.move_yx(ty0, tx0)}{target}")
        echo(f"{term.move_yx(y0, x0)}")
        self.set_cursor()

        self.result = WorditorResult(target=target)

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

            self.result.log_key(key)

            if key.name:
                if key.name in ("KEY_CTRL_C", "KEY_ESCAPE"):
                    self.result.log_done(self.current.strip())
                    return self.result

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
                # TODO was tun. wenn das Wort zu lang wird? Dann kann die ganze Zeile aus dem rechten Rand laufen
                #      -> 🔳 bis zum Ende der Zeile erlauben, dann mit Beep stoppen.
                #         ✅ bei Wortwechsel mit Space Überlängen mit Ellipsis wegkürzen: sonderbahr -> sonderba…
                #         term.length("…") == 1 und die Tastenfolge steht ja weiterhin im Monitor-Log für Analysen.
                self.char(key)
                self.echo_word()
                self.result.log_done(self.current.strip())
                return self.result

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
        display = self.current
        if self.current.endswith(" "):
            # done with that word
            if self.current.strip() == self.target:  # noqa: SIM108
                use_color = Config().success
            else:
                use_color = Config().alert
            # also echo the target word again, this time in proper color
            echo(f"{term.move_yx(self.ty0, self.tx0)}{use_color}{self.target}{term.normal}")
            if len(display) > len(self.target) + 1:
                # cut overlength when done to avoid overflow
                display = shorten(self.current, self.target)
                self.x = self.x0 + term.length(display)
                # add enough spaces to clear the rest of the word if it was too long before
                display += " " * (term.length(self.current) - term.length(display))
        elif self.target.startswith(self.current.strip()):
            # not done: check if correct so far
            use_color = Config().success
        else:
            # not done, but already wrong
            use_color = Config().alert
        echo(f"{term.move_yx(self.y0, self.x0)}{use_color}{display}{term.normal}")

    def char(self, key: Keystroke | str) -> None:
        """Insert the character at the current position."""
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
            # delete the char on screen, else backspaced stuff survives, which is more confusing than funny
            echo(" ")
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


MONITOR_X = 40


class Monitor:
    """Monitoring the training process."""

    _instance = None

    def __new__(cls) -> Monitor:
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
        self.result: list[WorditorResult] = []

    def log_word(self, result: WorditorResult) -> None:
        """Log a WorditorResult."""
        self.result.append(result)

    def info(self) -> None:
        """Display current info at the bottom of the terminal."""
        num_good = sum(1 for r in self.result if r.success)
        num_bad = len(self.result) - num_good
        good = Config().success + str(num_good) + term.normal if num_good > 0 else ""
        bad = Config().alert + str(num_bad) + term.normal if num_bad > 0 else ""
        mess = f"{good} {bad}".ljust(10)
        echo_at(term.height - 1, MONITOR_X, mess)

    def render(self) -> None:
        """Dump the current log to the terminal (after the typing session)."""
        if self.result:
            time_base = self.result[0].log[0][0]
            for r in self.result:
                r.render(time_base)

    def rating(self) -> None:
        """Compute and display a rating based on the logged results."""
        # may be regular end or user break
        relevant = [r for r in self.result if not r.leave]
        assert relevant, "No words typed, cannot compute rating."
        elapsed_time = relevant[-1].log[-1][0] - relevant[0].log[0][0]

        char_count = sum(len(r.target) for r in relevant)
        cpm = round(char_count / elapsed_time * 60)

        word_count = len(relevant)
        num_good = sum(1 for r in relevant if r.success)
        num_bad = word_count - num_good
        wpm = round(num_good / elapsed_time * 60)

        # ignore backspaces for the moment
        accuracy = num_good / len(relevant) * 100 if relevant else 0

        print(
            f"{wpm} WPM, {cpm} CPM",
            f"- accuracy {accuracy:.1f}% ({num_good} good, {num_bad} bad)",
            f"- survived for {hr_time(elapsed_time)}.",
        )
