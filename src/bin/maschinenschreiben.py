"""A simple typing tutor using the Blessed library for terminal handling."""

from __future__ import annotations

from tipplib import term, Worditor, WorditorResult, Config, TextSource, beep


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
        self.e = Worditor(self.text_y0, self.text_x0, self.word, self.target_y0, self.target_x0)
        self.e.alert("Moin.", color=Config().dim)
        self.e.set_cursor()
        while True:
            wr = self.e.run()
            if wr.leave:
                break  # Exit on Ctrl+C or Escape
            if self.next_word():
                self.e.alert("new line!")
                y0, x0, ty0, tx0 = self.text_y0, self.text_x0, self.target_y0, self.target_x0
            else:
                y0, x0, ty0, tx0 = self.e.y0, self.e.x, self.e.ty0, self.e.tx0 + len(self.e.target) + 1
            self.e.reset(y0, x0, self.word, ty0, tx0)

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


def main() -> None:
    """Run the typing tutor."""

    with term.fullscreen(), term.raw():
        Trainer()
