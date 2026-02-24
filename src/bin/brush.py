"""Pre-process Project Gutenberg Werther for use in Tippse."""

import re
import textwrap

from tipplib.util import get_reporoot


# https://projekt-gutenberg.org/authors/johann-wolfgang-von-goethe/books/die-leiden-des-jungen-werther/chapter/1/
INFILE = get_reporoot() / "local" / "werther.txt"
OUTFILE = get_reporoot() / "local" / "werther.md"


def normalize_dashes(text: str) -> str:
    """Replace various dash characters with a standard hyphen."""
    dash_map = {
        ord("\u2010"): "-", # Hyphen
        ord("\u2011"): "-", # Non-breaking hyphen
        ord("\u2012"): "-", # Figure dash
        ord("\u2013"): "-", # En dash (dein Zeichen aus dem hexdump)
        ord("\u2014"): "-", # Em dash
        ord("\u2015"): "-", # Horizontal bar
        ord("\u2212"): "-", # Minus sign
    }
    return text.translate(dash_map)


def main() -> None:
    """Read INFILE, double all single newlines, wrap to 70 chars, and write to OUTFILE."""

    content = INFILE.read_text(encoding="utf-8")
    content = normalize_dashes(content)

    # Replace typographic quotes with standard quotes
    content = content.replace("»", '"').replace("«", '"')

    # Replace single newline with double newline.
    # ... (existing comments) ...
    # ...
    # [^\n] ensures we are not at the start of a multi-newline sequence.
    # (?=[^\n]) ensures we are not at the start of a multi-newline sequence that continues.

    pattern = r"([^\n])(\n[ \t\r\f\v]*)(?=[^\n])"
    new_content = re.sub(pattern, r"\1\n\n", content)

    # Wrap each paragraph to max 70 chars
    paragraphs = new_content.split("\n\n")
    wrapped_paragraphs = [textwrap.fill(p, width=70) for p in paragraphs]
    final_content = "\n\n".join(wrapped_paragraphs)

    OUTFILE.write_text(final_content, encoding="utf-8")
    print(f"Processed {INFILE} -> {OUTFILE}")


if __name__ == "__main__":
    main()
