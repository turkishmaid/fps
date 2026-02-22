# from __future__ import annotations
# from time import time
# from typing import Self, TYPE_CHECKING

# from blessed import Terminal

# from .config import Config, Mode

# if TYPE_CHECKING:
#     from collections.abc import Callable

# term = Terminal()




# def tippse() -> None:
#     """Run main editor loop."""

#     # KeyHandlerRegistry().show_keybindings()

#     lr = load()

#     with term.fullscreen(), term.raw():
#         e = Editor()
#         e.alert(lr.message, color=Config().success if lr.success else Config().alert)
#         e.lines = lr.content

#         e.set_mode(Mode.insert)
#         e.echo_lines_from(0)
#         e.set_cursor()
#         while True:
#             key = term.inkey(timeout=0.35)
#             if key is None or key == "":
#                 continue  # No key pressed, continue the loop

#             # all thinggs KEY_...
#             try:
#                 if key.name and KeyHandlerRegistry().execute_handler(key.name, e):
#                     continue
#             except KeyboardInterrupt:
#                 break  # Exit on Ctrl+C

#             if key.is_sequence:
#                 e.alert(key.name)  # Show the key name as a quick message
#             else:  # noqa: PLR5501
#                 if e.mode == Mode.insert:
#                     char__insert(e, key)
#                 else:
#                     e.alert(f"'{key}'")  # Show the character as a quick message

def main() -> None:
    """Run the tippse."""
    raise NotImplementedError("The tippse is not implemented yet.")
