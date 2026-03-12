"""A simple typing tutor using the Blessed library for terminal handling."""

from __future__ import annotations
from time import time

from tipplib import term, Worditor, Monitor, Config, TextSource, echo


class Trainer:
    """Main class for the typing tutor."""

    def __init__(self) -> None:
        """Initialize the trainer."""

        c = Config()
        # Vorgabe startet hier
        self.target_y0, self.target_x0 = c.target_y0, c.target_x0
        # Eingetipptes startet hier
        self.text_y0, self.text_x0 = c.text_y0, c.text_x0

        self.words = [w for w in TextSource().get_line().split() if w]
        self.word_no = 0
        self.next_word()
        self.e = Worditor(self.text_y0, self.text_x0, self.word, self.target_y0, self.target_x0)
        self.e.alert("Moin.", color=Config().dim)
        self.e.set_cursor()
        while True:
            wr = self.e.run()
            Monitor().log_word(wr)
            if wr.leave:
                break  # Exit on Ctrl+C or Escape
            if self.next_word():
                self.e.alert("new line!")
                self.target_y0 += 1
                self.text_y0 += 1
                y0, x0, ty0, tx0 = self.text_y0, self.text_x0, self.target_y0, self.target_x0
            else:
                y0, x0, ty0, tx0 = self.e.y0, self.e.x, self.e.ty0, self.e.tx0 + len(self.e.target) + 1
            self.e.reset(y0, x0, self.word, ty0, tx0)
            Monitor().info()

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

    def layout(self) -> None:
        """Compute the current target layout for the trainer."""
        h, w = term.width, term.height
        # ???


def paint_frame(x0: int, y0: int, width: int, height: int) -> None:
    """Zeichne einen Rahmen um den angegebenen Bereich im Terminal."""
    if width < 2 or height < 2:
        return  # Zu klein für einen Rahmen
    current_y, current_x = term.get_location()
    # Rahmen in einem Durchgang zeichnen
    output = ""
    output += term.move_yx(y0, x0) + "┌" + "─" * (width - 2) + "┐"
    for i in range(1, height - 1):
        output += term.move_yx(y0 + i, x0) + "│"
        output += term.move_yx(y0 + i, x0 + width - 1) + "│"
    output += term.move_yx(y0 + height - 1, x0) + "└" + "─" * (width - 2) + "┘"
    echo(output)
    # Cursor zurücksetzen
    echo(term.move_yx(current_y, current_x))


def main() -> None:
    """Run the typing tutor."""

    with term.fullscreen(), term.raw():
        c = Config()
        paint_frame(c.target_x0 - 2, c.target_y0 - 1, c.target_width + 4, c.target_height + 2)  # x,y terminology m(
        Trainer()

    # Monitor().render()
    Monitor().rating()
