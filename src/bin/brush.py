from pathlib import Path
import functools
import re


@functools.cache
def get_reporoot() -> Path:
    """Get the root of the repository by looking for a .git directory."""
    here = Path(__file__).resolve().parent
    original_here = here
    while True:
        if (here / ".git").is_dir():
            return here
        assert here != here.parent, f".git/ not found from starting point {original_here}"
        here = here.parent


INFILE = get_reporoot() / "local" / "werther.txt"
OUTFILE = get_reporoot() / "local" / "werther.md"


def main() -> None:
    """Read INFILE, double all single newlines, wrap to 70 chars, and write to OUTFILE."""
    import textwrap

    content = INFILE.read_text(encoding="utf-8")

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
