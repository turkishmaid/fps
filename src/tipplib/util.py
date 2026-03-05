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

def hr_time(dt: float) -> str:
    """Compute human readable time. E.g., 1.2s, 4m02s, 1h03m04s."""
    hours, remainder = divmod(int(dt), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h{minutes:02}m{seconds:02}s"
    if minutes > 0:
        return f"{minutes}m{seconds:02}s"
    return f"{dt:.1f}s"
