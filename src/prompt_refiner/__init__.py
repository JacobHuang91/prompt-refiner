"""Prompt Refiner - A lightweight library for optimizing LLM inputs."""

__version__ = "0.1.3"

from .analyzer import CountTokens

# Import all operations for convenience
from .cleaner import FixUnicode, NormalizeWhitespace, StripHTML
from .compressor import Deduplicate, TruncateTokens
from .packer import (
    PER_MESSAGE_OVERHEAD,
    PER_REQUEST_OVERHEAD,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    BasePacker,
    MessagesPacker,
    PackableItem,
    TextFormat,
    TextPacker,
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
    "MessagesPacker",
    "TextPacker",
    "TextFormat",
    "BasePacker",
    "PackableItem",
    # Priority constants
    "PRIORITY_SYSTEM",
    "PRIORITY_USER",
    "PRIORITY_HIGH",
    "PRIORITY_MEDIUM",
    "PRIORITY_LOW",
    "PER_MESSAGE_OVERHEAD",
    "PER_REQUEST_OVERHEAD",
]
