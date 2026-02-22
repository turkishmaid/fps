"""A simple typing tutor using the Blessed library for terminal handling."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blessed.keyboard import Keystroke

from tipplib import term, Worditor, Config


def char(e: Worditor, key: Keystroke | str) -> None:
    """Insert the character at the current position."""
    e.word = e.word + str(key)
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


def on_space(e: Worditor) -> None:
    """Handle space key press."""
    # For now, just print the word and clear it
    e.alert(f"word! {e.word}")
    e.reset(e.y0, e.x, e.on_space)


def main() -> None:
    """Run the typing tutor."""

    with term.fullscreen(), term.raw():
        e = Worditor(17, 4, on_space)
        e.alert("Moin.", color=Config().dim)

        e.set_cursor()
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
                    backspace(e)
                    continue

                e.alert(f"n:{key.name}")  # Show the key name as a quick message
                continue

            if key.is_sequence:
                e.alert(f"sq:{key.name}")  # Show the key name as a quick message
                continue

            if key == " ":
                char(e, key)
                on_space(e)
                continue

            char(e, key)
