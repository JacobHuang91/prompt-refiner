"""Tool schema compression for reducing LLM token usage."""

import copy
import re
from typing import Any, Dict

from ..refiner import Refiner

JSON = Dict[str, Any]


class SchemaCompressor(Refiner):
    """
    Compress tool schemas to save tokens while preserving functionality.

    This operation compresses tool schema definitions (e.g., OpenAI function calling schemas)
    by removing documentation overhead while keeping all protocol-level fields intact.

    **What is modified:**
    - description fields (truncated and cleaned)
    - title fields (removed if configured)
    - examples fields (removed if configured)
    - markdown formatting (removed if configured)
    - excessive whitespace

    **What is never modified:**
    - name
    - type
    - properties
    - required
    - enum
    - Any other protocol-level fields

    Args:
        drop_examples: Remove examples fields (default: True)
        drop_titles: Remove title fields (default: True)
        drop_markdown_formatting: Remove markdown formatting (default: True)

    Example:
        >>> from prompt_refiner import SchemaCompressor
        >>>
        >>> tools = [{
        ...     "type": "function",
        ...     "function": {
        ...         "name": "search_flights",
        ...         "description": "Search for available flights between two airports. "
        ...                        "This is a very long description with examples...",
        ...         "parameters": {
        ...             "type": "object",
        ...             "properties": {
        ...                 "origin": {
        ...                     "type": "string",
        ...                     "description": "Origin airport IATA code, like `LAX`"
        ...                 }
        ...             }
        ...         }
        ...     }
        ... }]
        >>>
        >>> compressor = SchemaCompressor(drop_markdown_formatting=True)
        >>> compressed = compressor.process(tools)
        >>> # Markdown removed, tokens saved!

    Use Cases:
        - **Function Calling**: Reduce token usage in OpenAI/Anthropic function schemas
        - **Agent Systems**: Optimize tool definitions in agent prompts
        - **Cost Reduction**: Save 20-60% tokens on verbose tool schemas
        - **Context Management**: Fit more tools within token budget
    """

    def __init__(
        self,
        drop_examples: bool = True,
        drop_titles: bool = True,
        drop_markdown_formatting: bool = True,
    ):
        """
        Initialize schema compressor.

        Args:
            drop_examples: Remove examples fields (default: True)
            drop_titles: Remove title fields (default: True)
            drop_markdown_formatting: Remove markdown formatting (default: True)
        """
        self.drop_examples = drop_examples
        self.drop_titles = drop_titles
        self.drop_markdown_formatting = drop_markdown_formatting

    def process(self, tool: JSON) -> JSON:
        """
        Process a single tool schema and return compressed JSON.

        Args:
            tool: Tool schema dictionary (e.g., OpenAI function calling schema)

        Returns:
            Compressed tool schema dictionary

        Example:
            >>> tool = {
            ...     "type": "function",
            ...     "function": {
            ...         "name": "search",
            ...         "description": "Search for items...",
            ...         "parameters": {...}
            ...     }
            ... }
            >>> compressor = SchemaCompressor()
            >>> compressed = compressor.process(tool)
        """
        # Compress the tool
        return self._compress_single_tool(tool)

    def _compress_single_tool(self, tool: JSON) -> JSON:
        """
        Compress a single tool schema.

        Typical OpenAI structure:
        {
            "type": "function",
            "function": {
                "name": "...",
                "description": "...",
                "parameters": {...}
            }
        }

        Args:
            tool: Tool schema dictionary

        Returns:
            Compressed tool schema
        """
        # Deep copy to avoid modifying user's object
        tool_copy: JSON = copy.deepcopy(tool)

        # Compress function block if present (OpenAI style)
        fn = tool_copy.get("function")
        if isinstance(fn, dict):
            self._compress_function_block(fn)

        return tool_copy

    def _compress_function_block(self, fn: JSON) -> None:
        """
        Compress the function block of a tool schema.

        Args:
            fn: Function dictionary to compress in-place
        """
        # 1. Compress function-level description (hardcoded to 256 chars)
        if "description" in fn and isinstance(fn["description"], str):
            fn["description"] = self._compress_description(
                fn["description"],
                max_len=256,
                drop_markdown=self.drop_markdown_formatting,
            )

        # 2. Optional: remove title
        if self.drop_titles and "title" in fn:
            fn.pop("title", None)

        # 3. Compress parameters JSON Schema
        params = fn.get("parameters")
        if isinstance(params, dict):
            self._compress_json_schema(params, depth=0)

    def _compress_json_schema(self, schema: JSON, depth: int = 0) -> None:
        """
        Recursively compress a JSON Schema.

        Removes:
        - title / examples
        - Compresses description

        Never modifies:
        - type
        - properties
        - required
        - enum

        Args:
            schema: JSON Schema dictionary to compress in-place
            depth: Current recursion depth (0 = root)
        """
        # Remove title (documentation field)
        if self.drop_titles and "title" in schema:
            schema.pop("title", None)

        # Remove examples (usually verbose, limited value for tool calling)
        if self.drop_examples and "examples" in schema:
            schema.pop("examples", None)

        # Compress current level description (hardcoded to 160 chars for params, 256 for root)
        if "description" in schema and isinstance(schema["description"], str):
            max_len = 160 if depth > 0 else 256
            schema["description"] = self._compress_description(
                schema["description"],
                max_len=max_len,
                drop_markdown=self.drop_markdown_formatting,
            )

        # If object type, recurse into properties
        if schema.get("type") == "object":
            props = schema.get("properties")
            if isinstance(props, dict):
                for sub_schema in props.values():
                    if isinstance(sub_schema, dict):
                        self._compress_json_schema(sub_schema, depth=depth + 1)

        # If array type, recurse into items
        if schema.get("type") == "array":
            items = schema.get("items")
            if isinstance(items, dict):
                self._compress_json_schema(items, depth=depth + 1)

        # Other types (string/number/boolean/enum):
        # No structure to recurse, description/title/examples already handled above

    def _compress_description(
        self,
        text: str,
        max_len: int,
        drop_markdown: bool = True,
    ) -> str:
        """
        Compress description text.

        Steps:
        - Strip leading/trailing whitespace
        - Merge excessive whitespace/newlines
        - Optional: remove simple markdown (```code```, `inline`)
        - Truncate to max_len, preferably at sentence boundary

        Args:
            text: Description text to compress
            max_len: Maximum length
            drop_markdown: Whether to remove markdown formatting

        Returns:
            Compressed description text
        """
        # 1. Strip leading/trailing whitespace
        text = text.strip()

        # 2. Merge excessive whitespace and newlines
        text = re.sub(r"\s+", " ", text)

        # 3. Optional: remove simple markdown
        if drop_markdown:
            # Remove ```code``` blocks
            text = re.sub(r"`{3}.*?`{3}", "", text, flags=re.DOTALL)
            # `inline` → inline
            text = re.sub(r"`([^`]+)`", r"\1", text)
            text = text.strip()
            # Compress whitespace again
            text = re.sub(r"\s+", " ", text)

        # 4. Truncate to max_len
        if len(text) <= max_len:
            return text

        # Try to find sentence boundary near max_len
        window = text[: max_len + 40]  # Look a bit ahead for punctuation
        # Common sentence terminators (English and Chinese)
        m = re.search(r"[。．.！!？?]", window)
        if m and m.start() >= int(max_len * 0.5):
            # Found good break point
            text = window[: m.start() + 1]
        else:
            # Hard truncate
            text = text[:max_len]

        return text.strip()
