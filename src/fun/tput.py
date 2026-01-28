""""Measure FPS using random colored terminal output."""

import random
from collections.abc import Callable
from time import perf_counter
import blessed

term = blessed.Terminal()
ALL_CHARS = "".join([chr(i) for i in range(32, 127)])
patterns: list[str] = None  # pyright: ignore[reportAssignmentType] # initialized in recalc_patterns
last_size: tuple[int, int] = None # pyright: ignore[reportAssignmentType]
recalculated = -1  # first time is not a RE-calculation :3
recalc_time = 0.0


def read_terminal_dimensions() -> tuple[int, int]:
    """Return height and width of current terminal window."""
    return term.height, term.width


def clear_terminal() -> None:
    """Clear the terminal screen."""
    print(term.clear(), end="")


def create_random_pattern(height: int, width: int, chars: str = ALL_CHARS) -> str:
    """Create a random pattern of given height and width using specified characters.

    Each character should have a random color, set using ANSI escape codes.
    """
    height, width = read_terminal_dimensions()
    pattern_lines = []
    for i in range(height):
        line = "".join(f"{term.color(random.randint(1, 255))}{random.choice(chars)}" for _ in range(width)) # pyright: ignore[reportArgumentType]
        if i == 0:
            line = term.move_yx(0, 0) + line
        if i == height - 1:
            line += term.normal
        pattern_lines.append(line)
    return "\n".join(pattern_lines)


# fmt: off
FUNNY_WORDS = [
    "Humbug", "Quatsch", "Schnickschnack", "Kram", "Zeugs", "Krimskrams", "Firlefanz", "Blödsinn",
    "Käse", "Mumpitz", "Kokolores", "Larifari", "Pipifax", "Tinnef", "Gedöns", "Klimbim", "Zinnober",
    "Unfug", "Schabernack", "Schmu", "Flachsinn", "Dönekes", "Wischiwaschi", "Tüdelkram",
]
# fmt: on


def create_word_pattern(height: int, width: int, color_percent: float = 20.0) -> str:
    """Create a pattern using funny words with a percentage of them colored.

    Args:
        height: Terminal height
        width: Terminal width
        color_percent: Percentage of words that should be colored (0-100)

    Returns:
        The pattern as a string with ANSI escape codes
    """
    pattern_lines = []

    for i in range(height):
        line_parts = []
        current_width = 0

        while current_width < width:
            word = random.choice(FUNNY_WORDS)
            # Add space after word
            word_with_space = word + " "

            # Check if word fits
            if current_width + len(word_with_space) > width:
                # Fill remaining space with spaces
                remaining = width - current_width
                line_parts.append(" " * remaining)
                current_width = width
                break

            # Decide if this word should be colored
            should_color = (random.random() * 100) < color_percent

            if should_color:
                colored_word = f"{term.color(random.randint(1, 255))}{word_with_space}{term.normal}"  # pyright: ignore[reportArgumentType]
                line_parts.append(colored_word)
            else:
                line_parts.append(word_with_space)

            current_width += len(word_with_space)

        line = "".join(line_parts)

        if i == 0:
            line = term.move_yx(0, 0) + line

        pattern_lines.append(line)

    return "\n".join(pattern_lines)


def _recalc_patterns(height: int, width: int, /) -> list[str]:
    """Default helper to recalculate patterns."""
    return [create_word_pattern(height, width, 20.0) for _ in range(10)]


def set_recalc_function(func: Callable[[int, int], list[str]]) -> None:
    """Set an alternative function to recalculate patterns."""
    global _recalc_patterns  # noqa: PLW0603
    _recalc_patterns = func


def recalc_patterns() -> None:
    """Recalculate patterns based on current terminal size."""
    global patterns, last_size, recalculated, recalc_time  # noqa: PLW0603
    t0 = perf_counter()
    current_size = read_terminal_dimensions()
    if not patterns or current_size != last_size:
        last_size = current_size
        patterns = _recalc_patterns(*current_size)
        recalculated += 1
    dt = perf_counter() - t0
    recalc_time += dt


def print_random_pattern() -> None:
    """Print the given pattern to the terminal."""
    print(patterns[random.randint(0, len(patterns) - 1)])


iterations = []


def iterate_pattern() -> None:
    """Continuously print random patterns to the terminal."""
    # avoid Kitty scrollback
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        # iterate random choice from the list of prepared patterns
        t0o = perf_counter()
        try:
            while True:
                recalc_patterns()  # on 80x24, this produces 5% overhead added here, just for checking :D
                t0i = perf_counter()
                print_random_pattern()
                iterations.append(perf_counter() - t0i)
        except KeyboardInterrupt:
            clear_terminal()
        elapsed = perf_counter() - t0o
    # determine average of the iterations list
    avg = sum(iterations) / len(iterations) if iterations else 0

    # fmt: off
    print(f"Average time per pattern: {avg * 1000:.1f} ms ({1 / avg:.1f} fps) from {len(iterations)} iterations, {recalculated} recalcs.")
    # fmt: on

    # compare with measured time
    rendering = sum(iterations)
    percentage = (rendering / elapsed) * 100
    print(f"Rendering: {rendering:.2f} seconds.")
    print(f"Elapsed {elapsed:.2f} seconds (iterations represent {percentage:.1f}% of that).")
    print(f"Recalculation time (total): {recalc_time:.2f} seconds.")
