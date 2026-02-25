"""Mini-Benchmark: Dauer der Bildschirmgrößen-Abfrage mit Blessed messen.

Häufigkeitsverteilung (µs):
[   4.79,   23.49) | ######################################## (392)
[  23.49,   42.20) | #######                                  (70)
[  42.20,   60.90) | ###                                      (33)
[  60.90,   79.60) | #                                        (2)
[  79.60,   98.30) | #                                        (1)
[  98.30,  117.00) | #                                        (1)
[ 117.00,  135.71) |                                          (0)
[ 135.71,  154.41) |                                          (0)
[ 154.41,  173.11) |                                          (0)
[ 173.11,  191.81) |                                          (0)
[ 191.81,  210.51) |                                          (0)
[ 210.51,  229.22) |                                          (0)
[ 229.22,  247.92) |                                          (0)
[ 247.92,  266.62) |                                          (0)
[ 266.62,  285.32) |                                          (0)
[ 285.32,  304.02) |                                          (0)
[ 304.02,  322.73) |                                          (0)
[ 322.73,  341.43) |                                          (0)
[ 341.43,  360.13) |                                          (0)
[ 360.13,  378.83) | #                                        (1)

Max < 0,4 ms => kein Problem, nach jedem Tastendruck die Bildschirmgröße zu checken.
"""

from __future__ import annotations

from statistics import mean, median
from time import perf_counter_ns, sleep

from blessed import Terminal


def percentile(values: list[float], q: float) -> float:
    """Return the q-quantile using linear interpolation (q in [0.0, 1.0])."""
    if not values:
        raise ValueError("values must not be empty")
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must be between 0.0 and 1.0")

    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]

    index = q * (len(sorted_values) - 1)
    lower_index = int(index)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    fraction = index - lower_index
    lower = sorted_values[lower_index]
    upper = sorted_values[upper_index]
    return lower + (upper - lower) * fraction


def build_histogram(values: list[float], bins: int = 20, bar_width: int = 40) -> list[str]:
    """Build an ASCII histogram as a list of printable lines."""
    if not values:
        return []
    if bins < 1:
        raise ValueError("bins must be >= 1")
    if bar_width < 1:
        raise ValueError("bar_width must be >= 1")

    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        label = f"[{minimum:7.2f}, {maximum:7.2f}]"
        return [f"{label} | {'#' * bar_width} ({len(values)})"]

    width = (maximum - minimum) / bins
    counts = [0] * bins
    for value in values:
        index = int((value - minimum) / width)
        if index == bins:
            index -= 1
        counts[index] += 1

    peak = max(counts)
    lines: list[str] = []
    for i, count in enumerate(counts):
        low = minimum + i * width
        high = low + width
        if count == 0:
            bar = ""
        else:
            length = max(1, round((count / peak) * bar_width))
            bar = "#" * length
        lines.append(f"[{low:7.2f}, {high:7.2f}) | {bar:<{bar_width}} ({count})")
    return lines


def measure_terminal_size(term: Terminal) -> int:
    """Measure one `term.width`/`term.height` query in nanoseconds."""
    t0 = perf_counter_ns()
    _ = term.width, term.height
    return perf_counter_ns() - t0


def draw_change(term: Terminal, i: int, samples: int) -> None:
    """Draw a visible change so the screen updates between measurements."""
    spinner = "◐◓◑◒"
    glyph = spinner[i % len(spinner)]
    color = term.cyan if i % 2 == 0 else term.yellow
    bar_len = (i % 40) + 1
    bar = "=" * bar_len

    print(f"{term.move_yx(0, 0)}{color}{glyph} Messung {i + 1}/{samples}{term.normal}{term.clear_eol()}", end="")
    print(f"{term.move_yx(1, 0)}{bar}{term.clear_eol()}", end="", flush=True)


def run_benchmark(samples: int = 200, delay_seconds: float = 0.01) -> list[int]:
    """Run repeated measurements and return elapsed times in nanoseconds."""
    term = Terminal()
    elapsed_ns: list[int] = []
    measure_terminal_size(term)  # warm up, not measured

    with term.fullscreen(), term.hidden_cursor():
        print(term.home + term.clear, end="", flush=True)
        for i in range(samples):
            draw_change(term, i, samples)
            elapsed = measure_terminal_size(term)
            elapsed_ns.append(elapsed)
            print(
                f"{term.move_yx(3, 0)}Letzte Messung: {elapsed / 1_000:.2f} µs{term.clear_eol()}",
                end="",
                flush=True,
            )
            sleep(delay_seconds)

    return elapsed_ns


def main() -> None:
    """Run benchmark and print summary statistics."""
    elapsed_ns = run_benchmark(samples=500, delay_seconds=0.01)
    elapsed_us = [value / 1_000 for value in elapsed_ns]
    p99_us = percentile(elapsed_us, 0.99)
    histogram_lines = build_histogram(elapsed_us, bins=20, bar_width=40)

    print("\nBenchmark abgeschlossen")
    print(f"Messungen: {len(elapsed_us)}")
    print(f"Min:      {min(elapsed_us):8.2f} µs")
    print(f"Median:   {median(elapsed_us):8.2f} µs")
    print(f"p99:      {p99_us:8.2f} µs")
    print(f"Mittel:   {mean(elapsed_us):8.2f} µs")
    print(f"Max:      {max(elapsed_us):8.2f} µs")
    print("\nHäufigkeitsverteilung (µs):")
    for line in histogram_lines:
        print(line)


if __name__ == "__main__":
    main()
