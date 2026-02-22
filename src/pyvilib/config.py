"""Configuration and constants for the mini-vi editor."""

from __future__ import annotations
from enum import Enum
from typing import Self

from blessed import Terminal

term = Terminal()

# make it an enum for modes


class Mode(Enum):
    """Editor modes."""

    insert = "INSERT"
    command = "COMMAND"


class Config:
    """Configuration singleton for the mini-vi editor."""

    _instance = None

    def __new__(cls) -> Self:
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the configuration with default values."""

        # consider moving these to a separate theme or style class later
        self.dim = term.color_hex("#888888")
        self.bold = term.bright_cyan
        self.alert = term.color_hex("#880000")
        self.success = term.color_hex("#008800")
