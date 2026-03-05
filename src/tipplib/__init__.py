"""Kram für einen Schreibmaschinen-Trainer, wie ich als Ü60 ihn mir vorstelle."""


from .worditor import Worditor, WorditorResult, echo, echo_at, beep, term, Config, Monitor
from .util import get_reporoot, hr_time
from .text import TextSource

__all__ = ["Config", "Monitor", "TextSource", "Worditor", "WorditorResult", "beep", "echo", "echo_at", "get_reporoot", "hr_time", "term"]

