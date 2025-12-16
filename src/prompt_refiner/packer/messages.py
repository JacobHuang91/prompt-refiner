"""MessagesPacker for chat completion APIs (OpenAI, Anthropic, etc.)."""

import logging
from typing import Callable, Dict, List, Optional, Tuple, Union

from ..refiner import Refiner

# Import default strategies for auto-refinement
from ..strategy import MinimalStrategy, StandardStrategy
from .base import ROLE_CONTEXT, ROLE_QUERY, BasePacker

logger = logging.getLogger(__name__)


class MessagesPacker(BasePacker):
    """
    Packer for chat completion APIs.

    Designed for:
    - OpenAI Chat Completions (gpt-4, gpt-3.5-turbo, etc.)
    - Anthropic Messages API (claude-3-opus, claude-3-sonnet, etc.)
    - Any API using ChatML-style message format

    Returns: List[Dict[str, str]] with 'role' and 'content' keys

    Example:
        >>> from prompt_refiner import MessagesPacker
        >>> # Basic usage with automatic refining
        >>> packer = MessagesPacker(
        ...     system="You are helpful.",
        ...     context=["<div>Doc 1</div>", "<div>Doc 2</div>"],
        ...     query="What's the weather?"
        ... )
        >>> messages = packer.pack()
        >>> # Use directly: openai.chat.completions.create(messages=messages)
        >>>
        >>> # Traditional API still supported
        >>> packer = MessagesPacker()
        >>> packer.add("System prompt", role="system")
        >>> packer.add("User query", role="user")
        >>> messages = packer.pack()
    """

    def __init__(
        self,
        track_tokens: bool = False,
        token_counter: Optional[Callable[[str], int]] = None,
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
        Initialize messages packer.

        **Default Refining Strategies**:
        When no explicit refiner is provided, automatic refining strategies are applied:
        - system/query: MinimalStrategy (StripHTML + NormalizeWhitespace)
        - context/history: StandardStrategy (StripHTML + NormalizeWhitespace + Deduplicate)

        To override defaults, provide explicit refiner tuple: (content, refiner).
        For raw content with no refinement, use .add() method with refine_with=None.

        Args:
            track_tokens: Enable token tracking to measure refinement effectiveness
            token_counter: Function to count tokens (required if track_tokens=True)
            system: System message. Can be:
                - str: "You are helpful"  (automatically refined with MinimalStrategy)
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
            >>> packer = MessagesPacker(
            ...     system="You are helpful.",
            ...     context=["<div>Doc 1</div>", "<p>Doc 2</p>"],
            ...     history=[{"role": "user", "content": "Hi"}],
            ...     query="What's the weather?"
            ... )
            >>> messages = packer.pack()

        Example (With single Refiner):
            >>> from prompt_refiner import MessagesPacker, StripHTML
            >>> packer = MessagesPacker(
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>", "<p>Doc 2</p>"], StripHTML()),
            ...     query="What's the weather?"
            ... )
            >>> messages = packer.pack()

        Example (With Pipeline - multiple refiners):
            >>> from prompt_refiner import MessagesPacker, StripHTML, NormalizeWhitespace, Pipeline
            >>> cleaner = StripHTML() | NormalizeWhitespace()
            >>> # Or: cleaner = Pipeline([StripHTML(), NormalizeWhitespace()])
            >>> packer = MessagesPacker(
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>", "<p>Doc 2</p>"], cleaner),
            ...     query="What's the weather?"
            ... )
            >>> messages = packer.pack()

        Example (Traditional API - still supported):
            >>> packer = MessagesPacker()
            >>> packer.add("You are helpful.", role="system")
            >>> packer.add("Doc 1", role="context")
            >>> messages = packer.pack()
        """
        super().__init__(track_tokens, token_counter)
        logger.debug("MessagesPacker initialized")

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
    ) -> List[Dict[str, str]]:
        """
        One-liner to create packer and pack messages immediately.

        Default refining strategies are automatically applied (same as __init__):
        - system/query: MinimalStrategy
        - context/history: StandardStrategy

        Args:
            system: System message (str or (str, Refiner/Pipeline) tuple)
            context: Context documents (list or (list, Refiner/Pipeline) tuple)
            history: Conversation history (list or (list, Refiner/Pipeline) tuple)
            query: Current query (str or (str, Refiner/Pipeline) tuple)

        Returns:
            Packed messages ready for LLM API

        Example (Simple):
            >>> messages = MessagesPacker.quick_pack(
            ...     system="You are helpful.",
            ...     context=["<div>Doc 1</div>", "<p>Doc 2</p>"],
            ...     query="What's the weather?"
            ... )

        Example (With single Refiner):
            >>> from prompt_refiner import MessagesPacker, StripHTML
            >>> messages = MessagesPacker.quick_pack(
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>", "<p>Doc 2</p>"], StripHTML()),
            ...     query="What's the weather?"
            ... )

        Example (With Pipeline - multiple refiners):
            >>> from prompt_refiner import MessagesPacker, StripHTML, NormalizeWhitespace, Pipeline
            >>> cleaner = StripHTML() | NormalizeWhitespace()
            >>> # Or: cleaner = Pipeline([StripHTML(), NormalizeWhitespace()])
            >>> messages = MessagesPacker.quick_pack(
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>", "<p>Doc 2</p>"], cleaner),
            ...     query="What's the weather?"
            ... )
            >>> # Ready to use: client.chat.completions.create(messages=messages)
        """
        packer = cls(
            system=system,
            context=context,
            history=history,
            query=query,
        )
        return packer.pack()

    def pack(self) -> List[Dict[str, str]]:
        """
        Pack items into message format for chat APIs.

        Automatically maps semantic roles to API-compatible roles:
        - ROLE_CONTEXT → "user" (RAG documents as user-provided context)
        - ROLE_QUERY → "user" (current user question)
        - Other roles (system, user, assistant) remain unchanged

        Returns:
            List of message dictionaries with 'role' and 'content' keys,
            ready for OpenAI, Anthropic, and other chat completion APIs.

        Example:
            >>> messages = packer.pack()
            >>> openai.chat.completions.create(model="gpt-4", messages=messages)
        """
        selected_items = self._select_items()

        if not selected_items:
            logger.warning("No items selected, returning empty message list")
            return []

        messages = []
        for item in selected_items:
            # Map semantic roles to API-compatible roles
            api_role = item.role

            if item.role == ROLE_CONTEXT:
                # RAG documents become user messages (context provided by user)
                api_role = "user"
            elif item.role == ROLE_QUERY:
                # Current query becomes user message
                api_role = "user"
            # Other roles (system, user, assistant) remain unchanged

            messages.append({"role": api_role, "content": item.content})

        logger.info(f"Packed {len(messages)} messages for chat API")
        return messages
