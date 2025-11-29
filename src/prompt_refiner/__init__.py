"""Prompt Refiner - A lightweight library for optimizing LLM inputs."""

__version__ = "0.1.1"

from .analyzer import CountTokens

# Import all operations for convenience
from .cleaner import FixUnicode, NormalizeWhitespace, StripHTML
from .compressor import Deduplicate, TruncateTokens
from .packer import (
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    ContextPacker,
)
from .refiner import Refiner
from .scrubber import RedactPII

__all__ = [
    "Refiner",
    # Cleaner operations
    "StripHTML",
    "NormalizeWhitespace",
    "FixUnicode",
    # Compressor operations
    "TruncateTokens",
    "Deduplicate",
    # Scrubber operations
    "RedactPII",
    # Analyzer operations
    "CountTokens",
    # Packer operations
    "ContextPacker",
    "PRIORITY_SYSTEM",
    "PRIORITY_USER",
    "PRIORITY_HIGH",
    "PRIORITY_MEDIUM",
    "PRIORITY_LOW",
]
