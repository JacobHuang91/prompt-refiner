"""MessagesPacker for chat completion APIs (OpenAI, Anthropic, etc.)."""

import logging
from typing import Dict, List, Optional

from .base import BasePacker, PackableItem

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

    def __init__(self, max_tokens: Optional[int] = None, model: Optional[str] = None):
        """
        Initialize messages packer.

        Args:
            max_tokens: Maximum token budget. If None, includes all items without limit.
            model: Optional model name for precise token counting
        """
        super().__init__(max_tokens, model)

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

        Returns:
            List of message dictionaries with 'role' and 'content' keys.
            Items without role default to 'user'.

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
            # Default to 'user' role if not specified
            role = item.role or "user"
            messages.append({"role": role, "content": item.content})

        logger.info(f"Packed {len(messages)} messages for chat API")
        return messages
