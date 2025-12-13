"""MessagesPacker for chat completion APIs (OpenAI, Anthropic, etc.)."""

import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

from .base import ROLE_CONTEXT, ROLE_QUERY, BasePacker, PackableItem

if TYPE_CHECKING:
    from ..pipeline import Pipeline
    from ..refiner import Refiner

logger = logging.getLogger(__name__)

# Token overhead for ChatML format
# Each message has: <|im_start|>role\n{content}\n<|im_end|>
PER_MESSAGE_OVERHEAD = 4
PER_REQUEST_OVERHEAD = 3  # Base overhead for the request


class MessagesPacker(BasePacker):
    """
    Packer for chat completion APIs.

    Designed for:
    - OpenAI Chat Completions (gpt-4, gpt-3.5-turbo, etc.)
    - Anthropic Messages API (claude-3-opus, claude-3-sonnet, etc.)
    - Any API using ChatML-style message format

    Returns: List[Dict[str, str]] with 'role' and 'content' keys

    Example:
        >>> from prompt_refiner import MessagesPacker, PRIORITY_SYSTEM, PRIORITY_USER
        >>> # With token budget
        >>> packer = MessagesPacker(max_tokens=1000)
        >>> packer.add("You are helpful.", role="system", priority=PRIORITY_SYSTEM)
        >>> packer.add("Hello!", role="user", priority=PRIORITY_USER)
        >>> messages = packer.pack()
        >>> # Use directly: openai.chat.completions.create(messages=messages)
        >>>
        >>> # Without token budget (unlimited mode)
        >>> packer = MessagesPacker()  # All items included
        >>> packer.add("System prompt", role="system", priority=PRIORITY_SYSTEM)
        >>> packer.add("User query", role="user", priority=PRIORITY_USER)
        >>> messages = packer.pack()
    """

    def __init__(
        self,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        track_savings: bool = False,
        system: Optional[Union[str, Tuple[str, Union["Refiner", "Pipeline"]]]] = None,
        context: Optional[Union[List[str], Tuple[List[str], Union["Refiner", "Pipeline"]]]] = None,
        history: Optional[
            Union[
                List[Dict[str, str]],
                Tuple[List[Dict[str, str]], Union["Refiner", "Pipeline"]],
            ]
        ] = None,
        query: Optional[Union[str, Tuple[str, Union["Refiner", "Pipeline"]]]] = None,
    ):
        """
        Initialize messages packer.

        Args:
            max_tokens: Maximum token budget. If None, includes all items without limit.
            model: Optional model name for precise token counting
            track_savings: Enable automatic token savings tracking for refine_with
                operations (default: False)
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
            >>> packer = MessagesPacker(
            ...     model="gpt-4o-mini",
            ...     system="You are helpful.",
            ...     context=["<div>Doc 1</div>", "<p>Doc 2</p>"],
            ...     history=[{"role": "user", "content": "Hi"}],
            ...     query="What's the weather?"
            ... )
            >>> messages = packer.pack()

        Example (With single Refiner):
            >>> from prompt_refiner import MessagesPacker, StripHTML
            >>> packer = MessagesPacker(
            ...     model="gpt-4o-mini",
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
            ...     model="gpt-4o-mini",
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>", "<p>Doc 2</p>"], cleaner),
            ...     query="What's the weather?"
            ... )
            >>> messages = packer.pack()

        Example (Traditional API - still supported):
            >>> packer = MessagesPacker(model="gpt-4o-mini")
            >>> packer.add("You are helpful.", role="system")
            >>> packer.add("Doc 1", role="context")
            >>> messages = packer.pack()
        """
        super().__init__(max_tokens, model, track_savings)

        # Pre-deduct request-level overhead (priming tokens) if budget is limited
        if self.effective_max_tokens is not None:
            self.effective_max_tokens -= PER_REQUEST_OVERHEAD
            logger.debug(
                f"MessagesPacker initialized with {max_tokens} tokens "
                f"(effective: {self.effective_max_tokens} after {PER_REQUEST_OVERHEAD} "
                f"token request overhead)"
            )
        else:
            logger.debug("MessagesPacker initialized in unlimited mode")

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
    def _extract_field(
        field: Union[any, Tuple[any, Union["Refiner", "Pipeline"]]],
    ) -> Tuple[any, Optional[Union["Refiner", "Pipeline"]]]:
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
        system: Optional[Union[str, Tuple[str, Union["Refiner", "Pipeline"]]]] = None,
        context: Optional[Union[List[str], Tuple[List[str], Union["Refiner", "Pipeline"]]]] = None,
        history: Optional[
            Union[
                List[Dict[str, str]],
                Tuple[List[Dict[str, str]], Union["Refiner", "Pipeline"]],
            ]
        ] = None,
        query: Optional[Union[str, Tuple[str, Union["Refiner", "Pipeline"]]]] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        track_savings: bool = False,
    ) -> List[Dict[str, str]]:
        """
        One-liner to create packer and pack messages immediately.

        Args:
            system: System message (str or (str, Refiner/Pipeline) tuple)
            context: Context documents (list or (list, Refiner/Pipeline) tuple)
            history: Conversation history (list or (list, Refiner/Pipeline) tuple)
            query: Current query (str or (str, Refiner/Pipeline) tuple)
            model: Optional model name for precise token counting
            max_tokens: Optional token budget
            track_savings: Enable token savings tracking

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
            ...     query="What's the weather?",
            ...     model="gpt-4o-mini"
            ... )

        Example (With Pipeline - multiple refiners):
            >>> from prompt_refiner import MessagesPacker, StripHTML, NormalizeWhitespace, Pipeline
            >>> cleaner = StripHTML() | NormalizeWhitespace()
            >>> # Or: cleaner = Pipeline([StripHTML(), NormalizeWhitespace()])
            >>> messages = MessagesPacker.quick_pack(
            ...     system="You are helpful.",
            ...     context=(["<div>Doc 1</div>", "<p>Doc 2</p>"], cleaner),
            ...     query="What's the weather?",
            ...     model="gpt-4o-mini"
            ... )
            >>> # Ready to use: client.chat.completions.create(messages=messages)
        """
        packer = cls(
            max_tokens=max_tokens,
            model=model,
            track_savings=track_savings,
            system=system,
            context=context,
            history=history,
            query=query,
        )
        return packer.pack()

    def _calculate_overhead(self, item: PackableItem) -> int:
        """
        Calculate ChatML format overhead for messages.

        Each message in ChatML format consumes ~4 tokens for formatting:
        <|im_start|>role\n{content}\n<|im_end|>

        Note: PER_REQUEST_OVERHEAD (3 tokens) is pre-deducted in __init__,
        so we only return per-message overhead here.

        Args:
            item: Item to calculate overhead for

        Returns:
            Number of overhead tokens (4 tokens per message)
        """
        return PER_MESSAGE_OVERHEAD

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
        selected_items = self._greedy_select()

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
