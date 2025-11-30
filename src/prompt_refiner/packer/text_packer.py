"""TextPacker for text completion APIs (Llama, GPT-3, etc.)."""

import logging
from enum import Enum
from typing import Optional

from .base import BasePacker, PackableItem

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
        >>> packer = TextPacker(max_tokens=1000, text_format=TextFormat.MARKDOWN)
        >>> packer.add("You are helpful.", role="system", priority=PRIORITY_SYSTEM)
        >>> packer.add("Context document", priority=PRIORITY_HIGH)
        >>> prompt = packer.pack()
        >>> # prompt = "### INSTRUCTIONS:\\nYou are helpful.\\n\\n### CONTEXT:\\nContext document"
        >>> # Use directly: completion.create(prompt=prompt)
    """

    def __init__(
        self,
        max_tokens: int,
        model: Optional[str] = None,
        text_format: TextFormat = TextFormat.RAW,
        separator: Optional[str] = None,
    ):
        """
        Initialize text packer.

        Args:
            max_tokens: Maximum token budget
            model: Optional model name for precise token counting
            text_format: Text formatting strategy (RAW, MARKDOWN, XML)
            separator: String to join items (default: "\\n\\n" for clarity)
        """
        super().__init__(max_tokens, model)
        self.text_format = text_format
        self.separator = separator if separator is not None else "\n\n"

        # For MARKDOWN grouped format: Pre-deduct fixed header costs ("entrance fee")
        # This prevents overestimating overhead for each item
        if self.text_format == TextFormat.MARKDOWN:
            self._reserve_fixed_headers()

        logger.debug(
            f"TextPacker initialized with format={text_format.value}, "
            f"separator={repr(self.separator)}"
        )

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
        - INSTRUCTIONS: System prompts
        - CONTEXT: RAG documents (items without role)
        - CONVERSATION: User/assistant history
        - INPUT: Final user query

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
        # Group items by role/type
        system_items = []
        context_items = []
        conversation_items = []

        for item in selected_items:
            if item.role == "system":
                system_items.append(item.content)
            elif item.role is None:
                # No role = RAG documents -> CONTEXT section
                context_items.append(item.content)
            elif item.role in ["user", "assistant"]:
                # Conversation history
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
            # Separate last user query from history
            if conversation_items[-1][0] == "user":
                history = conversation_items[:-1]
                final_query = conversation_items[-1][1]
            else:
                history = conversation_items
                final_query = None

            # Format conversation history
            if history:
                conv_lines = [f"{role.capitalize()}: {content}" for role, content in history]
                sections.append("### CONVERSATION:\n" + "\n".join(conv_lines))

            # Final user query as INPUT
            if final_query:
                sections.append(f"### INPUT:\n{final_query}")

        return "\n\n".join(sections)
