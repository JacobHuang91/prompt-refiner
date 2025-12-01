"""Packer module for managing context budgets and token allocation."""

# New architecture (v0.1.3+)
from .base import (
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
    PackableItem,
)
from .messages_packer import PER_MESSAGE_OVERHEAD, PER_REQUEST_OVERHEAD, MessagesPacker
from .text_packer import TextFormat, TextPacker

__all__ = [
    # New architecture (recommended)
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
    # Message overhead constants
    "PER_MESSAGE_OVERHEAD",
    "PER_REQUEST_OVERHEAD",
]
