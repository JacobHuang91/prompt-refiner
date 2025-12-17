"""Prompt Refiner - A lightweight library for optimizing LLM inputs."""

__version__ = "0.2.3"

# Import all operations for convenience
from .analyzer import (
    TokenTracker,
    character_based_counter,
    create_tiktoken_counter,
    word_based_counter,
)
from .cleaner import FixUnicode, JsonCleaner, NormalizeWhitespace, StripHTML
from .compressor import Deduplicate, TruncateTokens
from .packer import (
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
    RoleType,
    TextFormat,
    TextPacker,
)
from .pipeline import Pipeline
from .refiner import Refiner
from .scrubber import RedactPII
from .strategy import AggressiveStrategy, MinimalStrategy, StandardStrategy
from .tools import ResponseCompressor, SchemaCompressor

__all__ = [
    "Refiner",
    "Pipeline",
    # Analyzer operations
    "TokenTracker",
    "character_based_counter",
    "word_based_counter",
    "create_tiktoken_counter",
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
    # Tools operations
    "SchemaCompressor",
    "ResponseCompressor",
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
    "RoleType",
    # Overhead constants
    "PER_MESSAGE_OVERHEAD",
    "PER_REQUEST_OVERHEAD",
    # Preset strategies
    "MinimalStrategy",
    "StandardStrategy",
    "AggressiveStrategy",
]
