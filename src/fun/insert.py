"""Handle key events in insert mode."""

from blessed.keyboard import Keystroke

from .config import Mode
from .editor import Editor, key_handler


def char__insert(e: Editor, key: Keystroke) -> None:
    """Handle normal character input."""
    y_index = e.y + e.y_offset
    line = e.lines[y_index]
    if e.mode == Mode.insert:
        # insert the character at the current position
        e.lines[y_index] = line[: e.x] + key + line[e.x :]
        e.x += 1
        e.echo_line()
        e.set_cursor()
    else:
        e.beep()  # Not in insert mode, bell sound


@key_handler
def key_ctrl_c(e: Editor) -> None:  # noqa: ARG001
    """Handle Ctrl+C key press until COMMAND mode is available."""
    raise KeyboardInterrupt


#
#       Cursor keys in all modes
#


@key_handler
def key_up(e: Editor) -> None:
    """Move the cursor up."""
    if e.y == 0:
        if e.y_offset > 0:
            e.y_offset -= 1
            e.echo_lines_from(0)
            e.set_cursor()
            return
        e.beep()  # Can't move up, bell sound
        return
    e.y -= 1
    e.set_cursor()


@key_handler
def key_down(e: Editor) -> None:
    """Move the cursor down."""
    if e.in_last_line:  # try to scroll
        if not e.has_more_lines:
            e.beep()
            return
        e.y_offset += 1
        e.echo_lines_from(0)
        e.set_cursor()
        return
    if e.has_more_lines:
        e.y += 1
        e.set_cursor()
    else:  # don't add lines implicitly
        e.beep()
        e.alert("use RETURN to add lines")
    e.set_cursor()


@key_handler
def key_left(e: Editor) -> None:
    """Move the cursor left."""
    if e.x == 0:
        e.beep()  # Can't move left, bell sound
        return
    e.x -= 1
    e.set_cursor()


@key_handler
def key_right(e: Editor) -> None:
    """Move the cursor right."""
    if e.x >= len(e.lines[e.y + e.y_offset]):
        e.beep()  # Can't move right, bell sound
        return
    e.x += 1
    e.set_cursor()


#
#       Delete forward and backward in INSERT mode
#

@key_handler
def key_backspace__insert(e: Editor) -> None:
    """Handle backspace key press in INSERT mode."""
    if e.x > 0:
        y_index = e.y + e.y_offset
        line = e.lines[y_index]
        # remove the character at the current position
        e.lines[y_index] = line[: e.x - 1] + line[e.x :]
        e.x -= 1
        e.echo_line()
        e.set_cursor()
    elif e.y + e.y_offset > 0:
        e.y -= 1  # move up
        y_above = e.y + e.y_offset
        e.x = len(e.lines[y_above])  # end of line above
        e.lines[y_above] += e.lines.pop(y_above + 1)
        if e.y < 0:  # scrolled up beyond visible area before
            e.y += 1
            e.y_offset -= 1
        e.echo_lines_from(e.y)
        e.set_cursor()  # position was set before
    else:
        e.beep()  # Can't backspace, bell sound


@key_handler
def key_delete__insert(e: Editor) -> None:
    """Handle delete key press."""
    y_index = e.y + e.y_offset
    line = e.lines[y_index]
    if e.x < len(line):
        # remove the character at the current position
        e.lines[y_index] = line[: e.x] + line[e.x + 1 :]
        e.echo_line()
        e.set_cursor()
    elif e.y + e.y_offset < len(e.lines) - 1:
        # join with next line
        e.lines[y_index] += e.lines.pop(y_index + 1)
        e.echo_lines_from(e.y)
        e.set_cursor()  # just where it is, now in the middle of the joinde line
    else:
        e.beep()  # Can't delete, bell sound


@key_handler
def key_enter__insert(e: Editor) -> None:
    """Enter in insert mode: Break line here."""
    y_index = e.y + e.y_offset
    line = e.lines[y_index]
    # split the line at the current position
    new_line = line[e.x :]
    e.lines[y_index] = line[: e.x]
    e.lines.insert(y_index + 1, new_line)
    if e.in_last_line:  # try to scroll
        e.y_offset += 1
        e.echo_lines_from(0)
    else:
        e.y += 1
        e.x = 0
        e.echo_lines_from(e.y - 1)
    e.set_cursor()


@key_handler
def key_backspace(e: Editor) -> None:
    """Backspace is like left when not in insert mode."""
    key_left(e)


@key_handler
def key_delete(e: Editor) -> None:
    """Delete is like right when not in insert mode."""
    key_right(e)


@key_handler
def key_enter(e: Editor) -> None:
    """Enter is like down when not in insert mode."""
    key_down(e)


@key_handler
def key_escape__insert(e: Editor) -> None:
    """Escape in insert mode: Switch to command mode."""
    e.set_mode(Mode.command)
