"""Reusable functions for various tasks."""

def have_fun(n:int) -> str:
    """Return a fun message n times."""
    if n == 0:
        return "no fun."
    return " ".join("Have fun!" for _ in range(n))
