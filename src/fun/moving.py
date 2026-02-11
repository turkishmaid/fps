"""Handle cursor movement and related key events in the editor."""

from fun.editor import Editor, INSERT, key_handler, term


@key_handler
def key_ctrl_c(e: Editor) -> None:
    """Handle Ctrl+C key press."""
    raise KeyboardInterrupt


@key_handler
def key_up(e: Editor) -> None:
    """Move the cursor up."""
    if e.y == 0:
        e.beep()  # Can't move up, bell sound
        return
    e.y -= 1
    e.set_cursor()


@key_handler
def key_down(e: Editor) -> None:
    """Move the cursor down."""
    if e.y >= term.height - 2:
        e.beep()  # no scroll yet
        return
    e.y += 1
    if e.mode == INSERT and e.y + e.y_offset == len(e.lines):
        # extend line buffer
        e.lines.append("")
        e.echo_line()
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


@key_handler
def key_backspace(e: Editor) -> None:
    """Handle backspace key press."""
    if e.mode != INSERT:
        key_right(e)
        return
    if e.x > 0:
        y_index = e.y + e.y_offset
        line = e.lines[y_index]
        # remove the character at the current position
        e.lines[y_index] = line[: e.x - 1] + line[e.x :]
        e.x -= 1
        e.echo_line()
    else:  # x == 0
        if e.y == 0:  # no-scrolling yet
            return
        if e.y + e.y_offset > 0:  # the real stuff
            e.y -= 1  # move up
            y_above = e.y + e.y_offset
            e.x = len(e.lines[y_above])  # end of line above
            e.lines[y_above] += e.lines.pop(y_above + 1)
            e.echo_lines_from(e.y)
            e.set_cursor()  # position was set before


@key_handler
def key_delete(e: Editor) -> None:
    """Handle delete key press."""
    if e.mode != INSERT:
        key_right(e)
        return
    y_index = e.y + e.y_offset
    line = e.lines[y_index]
    if e.x < len(line):
        # remove the character at the current position
        e.lines[y_index] = line[: e.x] + line[e.x + 1 :]
        e.echo_line()
    else:  # x at end of line
        if e.y == e.max_y:  # no-scrolling yet
            return
        if e.y + e.y_offset < len(e.lines) - 1:
            # join with next line
            e.lines[y_index] += e.lines.pop(y_index + 1)
            e.echo_lines_from(e.y)
            e.set_cursor()  # just where it is, now in the middle of the joinde line


@key_handler
def key_enter(e: Editor) -> None:
    """Handle enter key press."""
    if e.mode != INSERT:
        return
    y_index = e.y + e.y_offset
    line = e.lines[y_index]
    # split the line at the current position
    new_line = line[e.x :]
    e.lines[y_index] = line[: e.x]
    e.lines.insert(y_index + 1, new_line)
    e.y += 1
    e.x = 0
    e.echo_lines_from(e.y - 1)
    e.set_cursor()
