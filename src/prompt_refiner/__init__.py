"""Prompt Refiner - A lightweight library for optimizing LLM inputs."""

__version__ = "0.1.5"

from .analyzer import CountTokens

# Import all operations for convenience
from .cleaner import FixUnicode, JsonCleaner, NormalizeWhitespace, StripHTML
from .compressor import Deduplicate, TruncateTokens
from .packer import (
    PER_MESSAGE_OVERHEAD,
    PER_REQUEST_OVERHEAD,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_QUERY,
    PRIORITY_SYSTEM,
    ROLE_ASSISTANT,
    ROLE_CONTEXT,
    ROLE_QUERY,
    ROLE_SYSTEM,
    ROLE_USER,
    BasePacker,
    MessagesPacker,
    PackableItem,
    TextFormat,
    TextPacker,
)
from .refiner import Refiner
from .scrubber import RedactPII
from .strategy import AggressiveStrategy, MinimalStrategy, StandardStrategy
from .tools import SchemaCompressor

__all__ = [
    "Refiner",
    # Cleaner operations
    "StripHTML",
    "NormalizeWhitespace",
    "FixUnicode",
    "JsonCleaner",
    # Compressor operations
    "TruncateTokens",
    "Deduplicate",
    # Scrubber operations
    "RedactPII",
    # Analyzer operations
    "CountTokens",
    # Tools operations
    "SchemaCompressor",
    # Packer operations
    "MessagesPacker",
    "TextPacker",
    "TextFormat",
    "BasePacker",
    "PackableItem",
    # Priority constants
    "PRIORITY_SYSTEM",
    "PRIORITY_QUERY",
    "PRIORITY_HIGH",
    "PRIORITY_MEDIUM",
    "PRIORITY_LOW",
    # Role constants
    "ROLE_SYSTEM",
    "ROLE_QUERY",
    "ROLE_CONTEXT",
    "ROLE_USER",
    "ROLE_ASSISTANT",
    # Overhead constants
    "PER_MESSAGE_OVERHEAD",
    "PER_REQUEST_OVERHEAD",
    # Preset strategies
    "MinimalStrategy",
    "StandardStrategy",
    "AggressiveStrategy",
]
