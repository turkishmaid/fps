"""A simple typing tutor using the Blessed library for terminal handling."""

from __future__ import annotations
from time import time

from tipplib import term, Worditor, WorditorResult, Config, TextSource, beep, echo


INFO_X = 40


class Monitor:
    """Monitoring the Trainer."""

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
        self.elapsed_time: float = -1.0
        self.start_time: float = -1.0

    def start_timer(self) -> None:
        """Start the timer for the typing session."""
        if self.start_time < 0:
            self.start_time = time()
            self.elapsed_time = -1.0

    def stop_timer(self) -> None:
        """Stop the timer and calculate elapsed time."""
        assert self.start_time >= 0, "Timer was not started."
        self.elapsed_time = time() - self.start_time
        self.start_time = -1.0

    def log_word(self, result: WorditorResult) -> None:
        """Log a WorditorResult."""
        self.result.append(result)

    def info(self) -> None:
        """Display current info at the bottom of the terminal."""
        num_good = sum(1 for r in self.result if r.success)
        num_bad = len(self.result) - num_good
        y, x = term.get_location()
        good = Config().success + str(num_good) + term.normal if num_good > 0 else ""
        bad = Config().alert + str(num_bad) + term.normal if num_bad > 0 else ""
        mess = f"{good} {bad}".ljust(10)
        echo(f"{term.move_yx(term.height - 1, INFO_X)}{mess}{term.move_yx(y, x)}")

    def render(self) -> None:
        """Dump the current log to the terminal (after the typing session)."""
        if self.result:
            time_base = self.result[0].log[0][0]
            for r in self.result:
                r.render(time_base)


class Trainer:
    """Main class for the typing tutor."""


    def __init__(self) -> None:
        """Initialize the trainer."""

        # Vorgabe startet hier
        self.target_y0, self.target_x0  = 5, 4
        # Eingetipptes startet hier
        self.text_y0, self.text_x0 = 12, 4

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
        


def main() -> None:
    """Run the typing tutor."""

    with term.fullscreen(), term.raw():
        Trainer()

    Monitor().render()
