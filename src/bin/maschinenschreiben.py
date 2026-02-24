"""A simple typing tutor using the Blessed library for terminal handling."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blessed.keyboard import Keystroke

from tipplib import term, Worditor, Config, TextSource, echo, beep


def char(e: Worditor, key: Keystroke | str) -> None:
    """Insert the character at the current position."""
    char_value = str(key)
    if term.length(char_value) > 1:  # avoid emojis and other weird stuff, but not Umlaute
        beep()
        e.alert(f"ignoring {char_value!r} (len={term.length(char_value)})")
        return
    e.word = e.word + char_value
    e.x += 1
    e.echo_word()
    e.set_cursor()


def backspace(e: Worditor) -> None:
    """Delete the character before the current position."""
    if e.x > e.x0:
        e.word = e.word[:-1]
        e.x -= 1
        e.echo_word()
        e.set_cursor()
    else:
        e.beep()  # Can't backspace, bell sound


class Trainer:
    """Main class for the typing tutor."""

    target_y0 = 10
    target_x0 = 4
    text_y0 = 12
    text_x0 = 4

    def __init__(self) -> None:
        """Initialize the trainer."""
        self.words = [w for w in TextSource().get_line().split() if w]
        self.word_no = 0
        self.next_word()
        self.e = Worditor(self.text_y0, self.text_x0, self.on_space, self.word, self.target_y0, self.target_x0)
        self.e.alert("Moin.", color=Config().dim)
        self.e.set_cursor()

        while True:
            key = term.inkey(timeout=0.35)
            if key is None or key == "":
                # TODO manage resizing
                continue  # No key pressed, continue the loop

            # all thinggs KEY_...
            if key.name:
                if key.name in ("KEY_CTRL_C", "KEY_ESCAPE"):
                    break  # Exit on Ctrl+C or Escape

                if key.name == "KEY_BACKSPACE":
                    backspace(self.e)
                    continue

                self.e.alert(f"n:{key.name}")  # Show the key name as a quick message
                continue

            if key.is_sequence:
                self.e.alert(f"sq:{key.name}")  # Show the key name as a quick message
                continue

            if key == " ":
                self.on_space()
                continue

            char(self.e, key)

    def next_word(self) -> bool:
        """Move to the next word.

        Returns True if a new line was loaded, False if just the next word in the current line.
        """
        self.word_no += 1
        if self.word_no < len(self.words):
            self.word = self.words[self.word_no]
            return False
        self.words = TextSource().get_next_words()
        self.word_no = 0
        self.word = self.words[self.word_no] if self.words else "wtf?"  # No more words
        return True

    def on_space(self) -> None:
        """Handle space key press."""
        # gracefully ignore extra spaces
        if self.e.word.strip() == "":
            beep()
            return
        char(self.e, " ")
        self.e.echo_word()
        self.e.alert(f"word! {self.e.word}")
        if self.next_word():
            self.e.alert("new line!")
            y0, x0, ty0, tx0 = self.text_y0, self.text_x0, self.target_y0, self.target_x0
        else:
            y0, x0, ty0, tx0 = self.e.y0, self.e.x, self.e.ty0, self.e.tx0 + len(self.e.target) + 1
        self.e.reset(y0, x0, self.on_space, self.word, ty0, tx0)


def main() -> None:
    """Run the typing tutor."""

    with term.fullscreen(), term.raw():
        Trainer()

