"""TextPacker for text completion APIs (Llama, GPT-3, etc.)."""

import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

from .base import (
    ROLE_ASSISTANT,
    ROLE_CONTEXT,
    ROLE_QUERY,
    ROLE_SYSTEM,
    ROLE_USER,
    BasePacker,
    PackableItem,
)

logger = logging.getLogger(__name__)


class TextFormat(str, Enum):
    """
    Text formatting strategies for completion API output.

    Attributes:
        RAW: No delimiters, backward compatible (default)
        MARKDOWN: Grouped sections (INSTRUCTIONS, CONTEXT, CONVERSATION, INPUT)
                  optimized for base models to reduce token overhead
        XML: Use <role>content</role> tags (Anthropic best practice)
    """

    RAW = "raw"
    MARKDOWN = "markdown"
    XML = "xml"


class TextPacker(BasePacker):
    """
    Packer for text completion APIs.

    Designed for:
    - Base models (Llama-2-base, GPT-3, etc.)
    - Completion endpoints (not chat)
    - Custom prompt templates

    Returns: str (formatted text ready for completion API)

    Supports multiple text formatting strategies to prevent instruction drifting:
    - RAW: Simple concatenation with separators
    - MARKDOWN: Grouped sections (INSTRUCTIONS, CONTEXT, CONVERSATION, INPUT)
    - XML: Semantic <role>content</role> tags

    Example:
        >>> from prompt_refiner import TextPacker, TextFormat, PRIORITY_SYSTEM, PRIORITY_HIGH
        >>> # With token budget
        >>> packer = TextPacker(max_tokens=1000, text_format=TextFormat.MARKDOWN)
        >>> packer.add("You are helpful.", role="system", priority=PRIORITY_SYSTEM)
        >>> packer.add("Context document", priority=PRIORITY_HIGH)
        >>> prompt = packer.pack()
        >>> # Use directly: completion.create(prompt=prompt)
        >>>
        >>> # Without token budget (unlimited mode)
        >>> packer = TextPacker()  # All items included
        >>> packer.add("System prompt", role="system", priority=PRIORITY_SYSTEM)
        >>> prompt = packer.pack()
    """

    def __init__(
        self,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        text_format: TextFormat = TextFormat.RAW,
        separator: Optional[str] = None,
        track_savings: bool = False,
        system: Optional[Union[str, Tuple[str, List]]] = None,
        context: Optional[Union[List[str], Tuple[List[str], List]]] = None,
        history: Optional[Union[List[Dict[str, str]], Tuple[List[Dict[str, str]], List]]] = None,
        query: Optional[Union[str, Tuple[str, List]]] = None,
    ):
        """
        Initialize text packer.

        Args:
            max_tokens: Maximum token budget. If None, includes all items without limit.
            model: Optional model name for precise token counting
            text_format: Text formatting strategy (RAW, MARKDOWN, XML)
            separator: String to join items (default: "\\n\\n" for clarity)
            track_savings: Enable automatic token savings tracking for refine_with
                operations (default: False)
            system: System message. Can be:
                - str: "You are helpful"
                - Tuple[str, List]: ("You are helpful", [StripHTML()])
            context: Context documents. Can be:
                - List[str]: ["doc1", "doc2"]
                - Tuple[List[str], List]: (["doc1", "doc2"], [StripHTML()])
            history: Conversation history. Can be:
                - List[Dict]: [{"role": "user", "content": "Hi"}]
                - Tuple[List[Dict], List]: ([{"role": "user", "content": "Hi"}],
                    [NormalizeWhitespace()])
            query: Current query. Can be:
                - str: "What's the weather?"
                - Tuple[str, List]: ("What's the weather?", [StripHTML()])

        Example (Simple - no refiners):
            >>> packer = TextPacker(
            ...     model="llama-2-70b",
            ...     text_format=TextFormat.MARKDOWN,
            ...     system="You are helpful.",
            ...     context=["Doc 1", "Doc 2"],
            ...     query="What's the weather?"
            ... )
            >>> prompt = packer.pack()

        Example (With refiners - tuple syntax):
            >>> from prompt_refiner import TextPacker, StripHTML
            >>> packer = TextPacker(
            ...     text_format=TextFormat.MARKDOWN,
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>"], [StripHTML()]),
            ...     query="What's the weather?"
            ... )
            >>> prompt = packer.pack()
        """
        super().__init__(max_tokens, model, track_savings)
        self.text_format = text_format
        self.separator = separator if separator is not None else "\n\n"

        # For MARKDOWN grouped format: Pre-deduct fixed header costs ("entrance fee")
        # This prevents overestimating overhead for each item
        if self.text_format == TextFormat.MARKDOWN and self.effective_max_tokens is not None:
            self._reserve_fixed_headers()

        logger.debug(
            f"TextPacker initialized with format={text_format.value}, "
            f"separator={repr(self.separator)}, "
            f"unlimited={self.effective_max_tokens is None}"
        )

        # Auto-add items if provided (convenient API)
        # Extract content and refiner from tuple if provided
        if system is not None:
            system_content, system_refiner = self._extract_field(system)
            self.add(system_content, role="system", refine_with=system_refiner)

        if context is not None:
            context_docs, context_refiner = self._extract_field(context)
            for doc in context_docs:
                self.add(doc, role="context", refine_with=context_refiner)

        if history is not None:
            history_msgs, history_refiner = self._extract_field(history)
            for msg in history_msgs:
                self.add(msg["content"], role=msg["role"], refine_with=history_refiner)

        if query is not None:
            query_content, query_refiner = self._extract_field(query)
            self.add(query_content, role="query", refine_with=query_refiner)

    @staticmethod
    def _extract_field(field: Union[any, Tuple[any, List]]) -> Tuple[any, Optional[List]]:
        """
        Extract content and refiner from a field.

        Args:
            field: Either raw content or (content, refiner) tuple

        Returns:
            Tuple of (content, refiner)
        """
        if isinstance(field, tuple) and len(field) == 2:
            content, refiner = field
            return content, refiner
        else:
            return field, None

    @classmethod
    def quick_pack(
        cls,
        system: Optional[Union[str, Tuple[str, List]]] = None,
        context: Optional[Union[List[str], Tuple[List[str], List]]] = None,
        history: Optional[Union[List[Dict[str, str]], Tuple[List[Dict[str, str]], List]]] = None,
        query: Optional[Union[str, Tuple[str, List]]] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        text_format: TextFormat = TextFormat.RAW,
        separator: Optional[str] = None,
        track_savings: bool = False,
    ) -> str:
        """
        One-liner to create packer and pack text immediately.

        Args:
            system: System message (str or (str, refiner_list) tuple)
            context: Context documents (list or (list, refiner_list) tuple)
            history: Conversation history (list or (list, refiner_list) tuple)
            query: Current query (str or (str, refiner_list) tuple)
            model: Optional model name for precise token counting
            max_tokens: Optional token budget
            text_format: Text formatting strategy (RAW, MARKDOWN, XML)
            separator: String to join items
            track_savings: Enable token savings tracking

        Returns:
            Packed text ready for completion API

        Example (Simple):
            >>> prompt = TextPacker.quick_pack(
            ...     text_format=TextFormat.MARKDOWN,
            ...     system="You are helpful.",
            ...     context=["Doc 1", "Doc 2"],
            ...     query="What's the weather?"
            ... )

        Example (With refiners):
            >>> from prompt_refiner import TextPacker, StripHTML, TextFormat
            >>> prompt = TextPacker.quick_pack(
            ...     text_format=TextFormat.MARKDOWN,
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>"], [StripHTML()]),
            ...     query="What's the weather?"
            ... )
        """
        packer = cls(
            max_tokens=max_tokens,
            model=model,
            text_format=text_format,
            separator=separator,
            track_savings=track_savings,
            system=system,
            context=context,
            history=history,
            query=query,
        )
        return packer.pack()

    def _reserve_fixed_headers(self) -> None:
        """
        Pre-deduct fixed header costs for MARKDOWN grouped format.

        Section headers (INSTRUCTIONS, CONTEXT, CONVERSATION, INPUT) are fixed costs
        that don't scale with number of items. We reserve tokens upfront to prevent
        overestimating per-item overhead.

        Estimated costs:
        - "### INSTRUCTIONS:\n" ≈ 4 tokens
        - "### CONTEXT:\n" ≈ 3 tokens
        - "### CONVERSATION:\n" ≈ 4 tokens
        - "### INPUT:\n" ≈ 3 tokens
        - Section separators "\n\n" ≈ 2 tokens × 3 = 6 tokens
        Total ≈ 20 tokens (reserve 30 for safety)
        """
        fixed_cost = 30
        self.effective_max_tokens -= fixed_cost
        logger.debug(
            f"Reserved {fixed_cost} tokens for MARKDOWN headers, "
            f"effective budget: {self.effective_max_tokens}"
        )

    def _calculate_overhead(self, item: PackableItem) -> int:
        """
        Calculate text formatting overhead.

        Overhead depends on text_format:
        - RAW: Only separator tokens
        - MARKDOWN: Marginal costs (bullet points, newlines) - headers pre-reserved
        - XML: Separator + "<role>\\n" + "\\n</role>" tokens

        Args:
            item: Item to calculate overhead for

        Returns:
            Number of overhead tokens
        """
        overhead = 0

        # Format-specific overhead
        if self.text_format == TextFormat.RAW:
            # Separator overhead (applied between items)
            if self.separator:
                overhead += self._count_tokens(self.separator)

        elif self.text_format == TextFormat.MARKDOWN:
            # Marginal cost only (headers are pre-reserved in __init__)
            # Calculate cost of list bullets or conversation prefixes
            if item.role == "system":
                # System items concatenated directly, minimal overhead
                overhead = 0
            elif item.role is None:
                # RAG documents become "- Content\n\n"
                # Overhead: "\n\n- " ≈ 3 tokens
                overhead = 3
            elif item.role in ["user", "assistant"]:
                # Conversation becomes "User: Content\n" or "Assistant: Content\n"
                # Overhead: "\nUser: " or "\nAssistant: " ≈ 3-4 tokens
                overhead = 4
            else:
                overhead = 3  # Default fallback

        elif self.text_format == TextFormat.XML:
            # Separator + XML tags
            if self.separator:
                overhead += self._count_tokens(self.separator)
            role_label = item.role or "context"
            opening = f"<{role_label}>\n"
            closing = f"\n</{role_label}>"
            overhead += self._count_tokens(opening) + self._count_tokens(closing)

        return overhead

    def _format_item(self, item: PackableItem) -> str:
        """
        Format an item according to text_format.

        Args:
            item: Item to format

        Returns:
            Formatted text string
        """
        if self.text_format == TextFormat.RAW:
            return item.content

        role_label = item.role or "context"

        if self.text_format == TextFormat.MARKDOWN:
            return f"### {role_label.upper()}:\n{item.content}"

        elif self.text_format == TextFormat.XML:
            return f"<{role_label}>\n{item.content}\n</{role_label}>"

        return item.content

    def pack(self) -> str:
        """
        Pack items into formatted text for completion APIs.

        MARKDOWN format uses grouped sections to reduce token overhead:
        - INSTRUCTIONS: System prompts (ROLE_SYSTEM)
        - CONTEXT: RAG documents (ROLE_CONTEXT)
        - CONVERSATION: User/assistant history (ROLE_USER, ROLE_ASSISTANT)
        - INPUT: Current user query (ROLE_QUERY)

        Returns:
            Formatted text string ready for completion API

        Example:
            >>> prompt = packer.pack()
            >>> response = completion.create(model="llama-2-70b", prompt=prompt)
        """
        selected_items = self._greedy_select()

        if not selected_items:
            logger.warning("No items selected, returning empty string")
            return ""

        # MARKDOWN format: Use grouped sections (saves tokens)
        if self.text_format == TextFormat.MARKDOWN:
            result = self._pack_markdown_grouped(selected_items)
        else:
            # RAW and XML: Use item-by-item formatting
            parts = []
            for item in selected_items:
                formatted = self._format_item(item)
                parts.append(formatted)
            result = self.separator.join(parts)

        logger.info(
            f"Packed {len(selected_items)} items into "
            f"{self._count_tokens(result)} token text "
            f"(format={self.text_format.value})"
        )
        return result

    def _pack_markdown_grouped(self, selected_items: list) -> str:
        """
        Pack items using grouped MARKDOWN sections.

        This format is optimized for base models to reduce token overhead
        and improve semantic coherence.

        Args:
            selected_items: Items to pack (already in insertion order)

        Returns:
            Formatted text with grouped sections
        """
        # Group items by semantic role
        system_items = []
        context_items = []
        conversation_items = []
        query_items = []

        for item in selected_items:
            if item.role == ROLE_SYSTEM:
                # System instructions → INSTRUCTIONS section
                system_items.append(item.content)
            elif item.role == ROLE_CONTEXT:
                # RAG documents → CONTEXT section
                context_items.append(item.content)
            elif item.role == ROLE_QUERY:
                # Current query → INPUT section
                query_items.append(item.content)
            elif item.role in (ROLE_USER, ROLE_ASSISTANT):
                # Conversation history → CONVERSATION section
                conversation_items.append((item.role, item.content))

        # Build sections
        sections = []

        # 1. INSTRUCTIONS section (system prompts)
        if system_items:
            instructions = "\n\n".join(system_items)
            sections.append(f"### INSTRUCTIONS:\n{instructions}")

        # 2. CONTEXT section (RAG documents)
        if context_items:
            # Use bullet points for multiple documents
            if len(context_items) == 1:
                context_text = context_items[0]
            else:
                context_text = "\n\n".join(f"- {doc}" for doc in context_items)
            sections.append(f"### CONTEXT:\n{context_text}")

        # 3. CONVERSATION section (history)
        if conversation_items:
            conv_lines = [f"{role.capitalize()}: {content}" for role, content in conversation_items]
            sections.append("### CONVERSATION:\n" + "\n".join(conv_lines))

        # 4. INPUT section (current query)
        if query_items:
            # Multiple queries combined (rare but possible)
            query_text = "\n\n".join(query_items)
            sections.append(f"### INPUT:\n{query_text}")

        return "\n\n".join(sections)
