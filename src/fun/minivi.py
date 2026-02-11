"""Main entry point for the mini-vi editor."""

from dataclasses import dataclass
from pathlib import Path
import sys

from .config import Config, Mode
from .editor import Editor, KeyHandlerRegistry, term
from .insert import char__insert  # also loads the file and registers the handlers


@dataclass
class LoadResult:
    """Result of loading file content."""

    success: bool
    message: str
    content: list[str]


def load() -> LoadResult:
    """Load file content if a filename is given as a command line argument, otherwise return empty content."""
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("--"):
            if sys.argv[1] == "--debug":
                print(KeyHandlerRegistry().handlers)
                input("Press Enter to start the editor...")
        else:
            filename = sys.argv[1]
            here = Path.cwd()
            file_path = here / filename
            try:
                with file_path.open("r") as f:
                    content = [line.rstrip("\n") for line in f]
                return LoadResult(success=True, message=filename, content=content)
            except Exception as ex:
                return LoadResult(success=False, message=f"Error opening file: {ex}", content=[])
    return LoadResult(success=True, message="new file", content=[""])


def vi() -> None:
    """Run main editor loop."""

    KeyHandlerRegistry().show_keybindings()

    lr = load()

    with term.fullscreen(), term.raw():
        e = Editor()
        e.alert(lr.message, color=Config().success if lr.success else Config().alert)
        e.lines = lr.content

        e.set_mode(Mode.insert)
        e.echo_lines_from(0)
        e.set_cursor()
        while True:
            key = term.inkey(timeout=0.35)
            if key is None or key == "":
                continue  # No key pressed, continue the loop

            # all thinggs KEY_...
            try:
                if key.name and KeyHandlerRegistry().execute_handler(key.name, e):
                    continue
            except KeyboardInterrupt:
                break  # Exit on Ctrl+C

            if key.is_sequence:
                e.alert(key.name)  # Show the key name as a quick message
            else:  # noqa: PLR5501
                if e.mode == Mode.insert:
                    char__insert(e, key)
                else:
                    e.alert(f"'{key}'")  # Show the character as a quick message
