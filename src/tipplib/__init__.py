"""Kram für einen Schreibmaschinen-Trainer, wie ich als Ü60 ihn mir vorstelle."""


from .worditor import Worditor, echo, beep, term, Config
from .util import get_reporoot
from .text import TextSource

__all__ = ["Config", "TextSource", "Worditor", "beep", "echo", "get_reporoot", "term"]

