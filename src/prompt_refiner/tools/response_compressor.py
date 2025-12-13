"""Compress tool responses for LLM context."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence, Set

from ..refiner import Refiner

JSON = Dict[str, Any]
JSONLike = Any


class ResponseCompressor(Refiner):
    """
    Compress tool responses to reduce token usage before sending to LLM.

    This operation compresses JSON-like tool responses by removing verbose content
    while preserving essential information. Perfect for agent systems that need to
    fit tool outputs within LLM context windows.

    **What is modified:**
    - Long strings (truncated to 512 chars)
    - Long lists (truncated to 16 items)
    - Debug/trace/log fields (removed if in drop_keys)
    - Null values (removed if drop_null_fields=True)
    - Empty containers (removed if drop_empty_fields=True)
    - Deep nesting (truncated beyond max_depth)

    **What is preserved:**
    - Overall structure (dict keys, list order)
    - Essential data fields
    - Numbers and booleans (never modified)
    - Type information

    **IMPORTANT**: Use this ONLY for LLM-facing payloads. Do NOT use compressed
    output for business logic or APIs that expect complete data.

    Args:
        drop_keys: Field names to remove (default: debug, trace, logs, etc.)
        drop_null_fields: Remove fields with None values (default: True)
        drop_empty_fields: Remove empty strings/lists/dicts (default: True)
        max_depth: Maximum nesting depth before truncation (default: 8)
        add_truncation_marker: Add markers when truncating (default: True)
        truncation_suffix: Suffix for truncated content (default: "… (truncated)")

    Example:
        >>> from prompt_refiner import ResponseCompressor
        >>> # Compress API response before sending to LLM
        >>> compressor = ResponseCompressor()
        >>> response = {
        ...     "results": ["item1", "item2"] * 100,  # 200 items
        ...     "debug": {"trace": "..."},
        ...     "data": "x" * 1000
        ... }
        >>> compressed = compressor.process(response)
        >>> # Result: results limited to 16 items, debug removed, data truncated to 512 chars

    Use Cases:
        - **Agent Systems**: Compress verbose tool outputs before sending to LLM
        - **API Integration**: Reduce token usage from third-party API responses
        - **Cost Optimization**: Save 30-70% tokens on verbose tool responses
        - **Context Management**: Fit more tool results within token budget
    """

    def __init__(
        self,
        drop_keys: Set[str] | None = None,
        drop_null_fields: bool = True,
        drop_empty_fields: bool = True,
        max_depth: int = 8,
        add_truncation_marker: bool = True,
        truncation_suffix: str = "… (truncated)",
    ):
        """Initialize ResponseCompressor with compression settings."""
        # Hardcoded limits for simplicity
        self.max_string_chars = 512
        self.max_list_items = 16
        self.drop_keys = drop_keys or {
            "debug",
            "trace",
            "traces",
            "stack",
            "stacktrace",
            "logs",
            "logging",
        }
        self.drop_null_fields = drop_null_fields
        self.drop_empty_fields = drop_empty_fields
        self.max_depth = max_depth
        self.add_truncation_marker = add_truncation_marker
        self.truncation_suffix = truncation_suffix

    def process(self, response: JSON) -> JSON:
        """
        Compress tool response data.

        Args:
            response: Tool response as dict

        Returns:
            Compressed response as dict

        Example:
            >>> response = {
            ...     "results": [{"data": "x" * 1000}] * 100,
            ...     "debug": {"trace": "..."}
            ... }
            >>> compressor = ResponseCompressor()
            >>> compressed = compressor.process(response)
            >>> # Result: debug removed, results truncated, data shortened
        """
        # Compress the response
        return self._compress_any(response, depth=0)

    def _compress_any(self, value: JSONLike, depth: int) -> JSONLike:
        """Compress any JSON-like value recursively."""
        # Depth protection: stop recursion at max_depth
        if depth > self.max_depth:
            type_name = type(value).__name__
            return f"<{type_name} truncated at depth {self.max_depth}>"

        # None
        if value is None:
            return None

        # String: truncate
        if isinstance(value, str):
            return self._compress_string(value)

        # Numbers and booleans: pass through
        if isinstance(value, (int, float, bool)):
            return value

        # List/tuple: compress and truncate
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return self._compress_sequence(value, depth)

        # Dict/mapping: compress key-value pairs
        if isinstance(value, Mapping):
            return self._compress_mapping(value, depth)

        # Other types: convert to string and truncate
        text = str(value)
        return self._compress_string(text)

    def _compress_string(self, text: str) -> str:
        """Truncate string to max_string_chars."""
        if len(text) <= self.max_string_chars:
            return text

        # Truncate and optionally add marker
        truncated = text[: self.max_string_chars].rstrip()
        if self.add_truncation_marker and self.truncation_suffix:
            truncated = f"{truncated} {self.truncation_suffix}"
        return truncated

    def _compress_sequence(self, seq: Sequence[Any], depth: int) -> list[Any]:
        """Compress list/tuple: truncate length and compress elements."""
        # Truncate length first
        truncated = list(seq[: self.max_list_items])

        # Recursively compress each element
        compressed_items: list[Any] = []
        for item in truncated:
            compressed_items.append(self._compress_any(item, depth + 1))

        # Add truncation marker if list was shortened
        if self.add_truncation_marker and len(seq) > self.max_list_items:
            compressed_items.append(
                f"<list truncated from {len(seq)} to {self.max_list_items} items>"
            )

        return compressed_items

    def _compress_mapping(self, mapping: Mapping[str, Any], depth: int) -> Dict[str, Any]:
        """Compress dict: drop noise keys, compress values, filter empties."""
        result: Dict[str, Any] = {}

        for key, value in mapping.items():
            # Drop noise keys (case-insensitive)
            if key.lower() in self.drop_keys:
                continue

            # Recursively compress value
            compressed = self._compress_any(value, depth + 1)

            # Drop null fields if configured
            if compressed is None and self.drop_null_fields:
                continue

            # Drop empty fields if configured
            if self.drop_empty_fields and self._is_empty_value(compressed):
                continue

            result[key] = compressed

        return result

    def _is_empty_value(self, value: Any) -> bool:
        """Check if value is empty (empty string, empty container)."""
        # Empty string
        if value == "":
            return True
        # Empty container
        if isinstance(value, (Sequence, Mapping)) and not value:
            return True
        return False
