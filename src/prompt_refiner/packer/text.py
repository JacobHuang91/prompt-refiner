"""TextPacker for text completion APIs (Llama, GPT-3, etc.)."""

import logging
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, Union

from ..refiner import Refiner

# Import default strategies for auto-refinement
from ..strategy import MinimalStrategy, StandardStrategy
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
        >>> from prompt_refiner import TextPacker, TextFormat
        >>> # Basic usage with automatic refining
        >>> packer = TextPacker(
        ...     text_format=TextFormat.MARKDOWN,
        ...     system="You are helpful.",
        ...     context=["<div>Doc 1</div>", "<div>Doc 2</div>"],
        ...     query="What's the weather?"
        ... )
        >>> prompt = packer.pack()
        >>> # Use directly: completion.create(prompt=prompt)
        >>>
        >>> # Traditional API still supported
        >>> packer = TextPacker()
        >>> packer.add("System prompt", role="system")
        >>> prompt = packer.pack()
    """

    def __init__(
        self,
        track_tokens: bool = False,
        token_counter: Optional[Callable[[str], int]] = None,
        text_format: TextFormat = TextFormat.RAW,
        separator: Optional[str] = None,
        system: Optional[Union[str, Tuple[str, Refiner]]] = None,
        context: Optional[Union[List[str], Tuple[List[str], Refiner]]] = None,
        history: Optional[
            Union[
                List[Dict[str, str]],
                Tuple[List[Dict[str, str]], Refiner],
            ]
        ] = None,
        query: Optional[Union[str, Tuple[str, Refiner]]] = None,
    ):
        """
        Initialize text packer.

        **Default Refining Strategies**:
        When no explicit refiner is provided, automatic refining strategies are applied:
        - system/query: MinimalStrategy (StripHTML + NormalizeWhitespace)
        - context/history: StandardStrategy (StripHTML + NormalizeWhitespace + Deduplicate)

        To override defaults, provide explicit refiner tuple: (content, refiner).
        For raw content with no refinement, use .add() method with refine_with=None.

        Args:
            track_tokens: Enable token tracking to measure refinement effectiveness
            token_counter: Function to count tokens (required if track_tokens=True)
            text_format: Text formatting strategy (RAW, MARKDOWN, XML)
            separator: String to join items (default: "\\n\\n" for clarity)
            system: System message. Can be:
                - str: "You are helpful"
                - Tuple[str, Refiner]: ("You are helpful", StripHTML())
                - Tuple[str, Pipeline]: ("You are helpful", StripHTML() | NormalizeWhitespace())
            context: Context documents. Can be:
                - List[str]: ["doc1", "doc2"]
                - Tuple[List[str], Refiner]: (["doc1", "doc2"], StripHTML())
                - Tuple[List[str], Pipeline]: (["doc1", "doc2"],
                    StripHTML() | NormalizeWhitespace())
            history: Conversation history. Can be:
                - List[Dict]: [{"role": "user", "content": "Hi"}]
                - Tuple[List[Dict], Refiner]: ([{"role": "user", "content": "Hi"}], StripHTML())
                - Tuple[List[Dict], Pipeline]: ([{"role": "user", "content": "Hi"}],
                    StripHTML() | NormalizeWhitespace())
            query: Current query. Can be:
                - str: "What's the weather?"
                - Tuple[str, Refiner]: ("What's the weather?", StripHTML())
                - Tuple[str, Pipeline]: ("What's the weather?", StripHTML() | NormalizeWhitespace())

        Example (Simple - no refiners):
            >>> packer = TextPacker(
            ...     text_format=TextFormat.MARKDOWN,
            ...     system="You are helpful.",
            ...     context=["Doc 1", "Doc 2"],
            ...     query="What's the weather?"
            ... )
            >>> prompt = packer.pack()

        Example (With single Refiner):
            >>> from prompt_refiner import TextPacker, StripHTML
            >>> packer = TextPacker(
            ...     text_format=TextFormat.MARKDOWN,
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>"], StripHTML()),
            ...     query="What's the weather?"
            ... )
            >>> prompt = packer.pack()

        Example (With Pipeline - multiple refiners):
            >>> from prompt_refiner import TextPacker, StripHTML, NormalizeWhitespace, Pipeline
            >>> cleaner = StripHTML() | NormalizeWhitespace()
            >>> # Or: cleaner = Pipeline([StripHTML(), NormalizeWhitespace()])
            >>> packer = TextPacker(
            ...     text_format=TextFormat.MARKDOWN,
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>"], cleaner),
            ...     query="What's the weather?"
            ... )
            >>> prompt = packer.pack()
        """
        super().__init__(track_tokens, token_counter)
        self.text_format = text_format
        self.separator = separator if separator is not None else "\n\n"

        logger.debug(
            f"TextPacker initialized with format={text_format.value}, "
            f"separator={repr(self.separator)}"
        )

        # Auto-add items if provided (convenient API)
        # Extract content and refiner from tuple if provided
        # Apply default strategies when no explicit refiner provided
        if system is not None:
            system_content, system_refiner = self._extract_field(system)
            # Apply MinimalStrategy to system if no explicit refiner
            if system_refiner is None:
                system_refiner = MinimalStrategy()
            self.add(system_content, role="system", refine_with=system_refiner)

        if context is not None:
            context_docs, context_refiner = self._extract_field(context)
            # Apply StandardStrategy to context if no explicit refiner
            if context_refiner is None:
                context_refiner = StandardStrategy()
            for doc in context_docs:
                self.add(doc, role="context", refine_with=context_refiner)

        if history is not None:
            history_msgs, history_refiner = self._extract_field(history)
            # Apply StandardStrategy to history if no explicit refiner
            if history_refiner is None:
                history_refiner = StandardStrategy()
            for msg in history_msgs:
                self.add(msg["content"], role=msg["role"], refine_with=history_refiner)

        if query is not None:
            query_content, query_refiner = self._extract_field(query)
            # Apply MinimalStrategy to query if no explicit refiner
            if query_refiner is None:
                query_refiner = MinimalStrategy()
            self.add(query_content, role="query", refine_with=query_refiner)

    @staticmethod
    def _extract_field(
        field: Union[any, Tuple[any, Refiner]],
    ) -> Tuple[any, Optional[Refiner]]:
        """
        Extract content and refiner/pipeline from a field.

        Args:
            field: Either raw content or (content, refiner/pipeline) tuple.
                Can be a Refiner or Pipeline.

        Returns:
            Tuple of (content, refiner/pipeline) where the second element can be
            None, Refiner, or Pipeline.
        """
        if isinstance(field, tuple) and len(field) == 2:
            content, refiner = field
            return content, refiner
        else:
            return field, None

    @classmethod
    def quick_pack(
        cls,
        system: Optional[Union[str, Tuple[str, Refiner]]] = None,
        context: Optional[Union[List[str], Tuple[List[str], Refiner]]] = None,
        history: Optional[
            Union[
                List[Dict[str, str]],
                Tuple[List[Dict[str, str]], Refiner],
            ]
        ] = None,
        query: Optional[Union[str, Tuple[str, Refiner]]] = None,
        text_format: TextFormat = TextFormat.RAW,
        separator: Optional[str] = None,
    ) -> str:
        """
        One-liner to create packer and pack text immediately.

        Default refining strategies are automatically applied (same as __init__):
        - system/query: MinimalStrategy
        - context/history: StandardStrategy

        Args:
            system: System message (str or (str, Refiner/Pipeline) tuple)
            context: Context documents (list or (list, Refiner/Pipeline) tuple)
            history: Conversation history (list or (list, Refiner/Pipeline) tuple)
            query: Current query (str or (str, Refiner/Pipeline) tuple)
            text_format: Text formatting strategy (RAW, MARKDOWN, XML)
            separator: String to join items

        Returns:
            Packed text ready for completion API

        Example (Simple):
            >>> prompt = TextPacker.quick_pack(
            ...     text_format=TextFormat.MARKDOWN,
            ...     system="You are helpful.",
            ...     context=["Doc 1", "Doc 2"],
            ...     query="What's the weather?"
            ... )

        Example (With single Refiner):
            >>> from prompt_refiner import TextPacker, StripHTML, TextFormat
            >>> prompt = TextPacker.quick_pack(
            ...     text_format=TextFormat.MARKDOWN,
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>"], StripHTML()),
            ...     query="What's the weather?"
            ... )

        Example (With Pipeline - multiple refiners):
            >>> from prompt_refiner import (
            ...     TextPacker, StripHTML, NormalizeWhitespace, TextFormat, Pipeline
            ... )
            >>> cleaner = StripHTML() | NormalizeWhitespace()
            >>> # Or: cleaner = Pipeline([StripHTML(), NormalizeWhitespace()])
            >>> prompt = TextPacker.quick_pack(
            ...     text_format=TextFormat.MARKDOWN,
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>"], cleaner),
            ...     query="What's the weather?"
            ... )
        """
        packer = cls(
            text_format=text_format,
            separator=separator,
            system=system,
            context=context,
            history=history,
            query=query,
        )
        return packer.pack()

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

        MARKDOWN format uses grouped sections:
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
        selected_items = self._select_items()

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

        logger.info(f"Packed {len(selected_items)} items (format={self.text_format.value})")
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
