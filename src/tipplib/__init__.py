"""Kram für einen Schreibmaschinen-Trainer, wie ich als Ü60 ihn mir vorstelle."""


from .worditor import Worditor, WorditorResult, echo, beep, term, Config
from .util import get_reporoot
from .text import TextSource

__all__ = ["Config", "TextSource", "Worditor", "WorditorResult", "beep", "echo", "get_reporoot", "term"]

