"""Some utility functions for the project."""

from pathlib import Path
import functools


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
