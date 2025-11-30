"""Base packer with common logic for token budget management."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from ..analyzer.counter import CountTokens
from ..operation import Operation

logger = logging.getLogger(__name__)

# Priority constants - lower values = higher priority
PRIORITY_SYSTEM = 0  # Absolute must-have (e.g., system prompts)
PRIORITY_USER = 10  # Critical user input
PRIORITY_HIGH = 20  # Important context (e.g., core RAG documents)
PRIORITY_MEDIUM = 30  # Normal priority (e.g., general RAG documents)
PRIORITY_LOW = 40  # Optional content (e.g., old conversation history)


@dataclass
class PackableItem:
    """
    Item to be packed into token budget.

    Attributes:
        content: The text content
        tokens: Base token count (without format overhead)
        priority: Priority value (lower = higher priority)
        insertion_index: Order in which item was added
        role: Optional role for message-based APIs (system, user, assistant)
    """

    content: str
    tokens: int
    priority: int
    insertion_index: int
    role: Optional[str] = None


class BasePacker(ABC):
    """
    Abstract base class for token budget packers.

    Provides common functionality:
    - Adding items with priorities
    - JIT refinement with operations
    - Greedy selection algorithm
    - Token counting with safety buffer

    Subclasses must implement:
    - _calculate_overhead(): Calculate format-specific overhead
    - pack(): Format and return packed items
    """

    def __init__(self, max_tokens: Optional[int] = None, model: Optional[str] = None):
        """
        Initialize packer with optional token budget.

        Args:
            max_tokens: Maximum token budget. If None, includes all items without limit.
            model: Optional model name for precise token counting (requires tiktoken)
        """
        self.raw_max_tokens = max_tokens
        self._items: List[PackableItem] = []
        self._insertion_counter = 0
        self._token_counter = CountTokens(model=model)

        # Calculate effective max tokens
        if max_tokens is None:
            self.effective_max_tokens = None
            logger.debug("Unlimited mode: all items will be included")
        elif not self._token_counter.is_precise:
            self.effective_max_tokens = int(max_tokens * 0.9)
            logger.debug(
                f"Using estimation mode with 10% safety buffer: "
                f"{self.effective_max_tokens}/{max_tokens}"
            )
        else:
            self.effective_max_tokens = max_tokens
            logger.debug(f"Using precise mode with tiktoken: {self.effective_max_tokens} tokens")

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using configured counter."""
        return self._token_counter._estimate_tokens(text)

    def add(
        self,
        content: str,
        role: Optional[str] = None,
        priority: Optional[int] = None,
        refine_with: Optional[Union[Operation, List[Operation]]] = None,
    ) -> "BasePacker":
        """
        Add an item to the packer.

        Args:
            content: Text content to add
            role: Optional role for message APIs (system, user, assistant)
            priority: Priority level (use PRIORITY_* constants). If None, infers from role:
                - role="system" → PRIORITY_SYSTEM (0)
                - role="user" → PRIORITY_USER (10)
                - role=None → PRIORITY_HIGH (20) - for RAG documents
                - role="assistant" or other → PRIORITY_MEDIUM (30)
            refine_with: Optional operation(s) to apply before adding

        Returns:
            Self for method chaining
        """
        # Smart priority defaults based on role
        if priority is None:
            if role == "system":
                priority = PRIORITY_SYSTEM  # 0 - Highest priority
            elif role == "user":
                priority = PRIORITY_USER  # 10 - User queries are critical
            elif role is None:
                priority = PRIORITY_HIGH  # 20 - RAG documents (no role)
            else:
                priority = PRIORITY_MEDIUM  # 30 - Assistant and other roles

        # JIT refinement
        if refine_with:
            if isinstance(refine_with, list):
                for op in refine_with:
                    content = op.process(content)
            else:
                content = refine_with.process(content)

        # Count base tokens (without format overhead)
        tokens = self._count_tokens(content)

        item = PackableItem(
            content=content,
            tokens=tokens,
            priority=priority,
            insertion_index=self._insertion_counter,
            role=role,
        )

        self._items.append(item)
        self._insertion_counter += 1

        logger.debug(f"Added item: {tokens} tokens, priority={priority}, role={role}")
        return self

    def add_messages(
        self,
        messages: List[Dict[str, str]],
        priority: int = PRIORITY_LOW,
    ) -> "BasePacker":
        """
        Batch add messages (convenience method).

        Defaults to PRIORITY_LOW because conversation history is usually the first
        to be dropped in favor of RAG context and current queries.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            priority: Priority level for all messages (default: PRIORITY_LOW for history)

        Returns:
            Self for method chaining
        """
        for msg in messages:
            self.add(content=msg["content"], role=msg["role"], priority=priority)
        return self

    @abstractmethod
    def _calculate_overhead(self, item: PackableItem) -> int:
        """
        Calculate format-specific overhead for an item.

        Subclasses must implement this to calculate tokens consumed by:
        - Chat APIs: ChatML format markers (<|im_start|>, etc.)
        - Text APIs: Separators, role labels, etc.

        Args:
            item: Item to calculate overhead for

        Returns:
            Number of overhead tokens
        """
        pass

    def _greedy_select(self) -> List[PackableItem]:
        """
        Select items using greedy algorithm based on priorities.

        Algorithm:
        1. Sort items by priority (lower value = higher priority)
        2. If max_tokens is None, include all items
        3. Otherwise, greedily select items that fit within budget (including overhead)
        4. Restore insertion order for natural reading flow

        Returns:
            List of selected items in insertion order
        """
        if not self._items:
            return []

        # Unlimited mode: include all items
        if self.effective_max_tokens is None:
            logger.info(f"Unlimited mode: packed all {len(self._items)} items")
            return list(self._items)

        # Sort by priority (stable sort preserves insertion order for equal priorities)
        sorted_items = sorted(self._items, key=lambda x: (x.priority, x.insertion_index))

        selected: List[PackableItem] = []
        current_tokens = 0

        # Greedy packing with format overhead
        for item in sorted_items:
            overhead = self._calculate_overhead(item)
            total_cost = item.tokens + overhead

            if current_tokens + total_cost <= self.effective_max_tokens:
                selected.append(item)
                current_tokens += total_cost
                logger.debug(
                    f"Selected item: {item.tokens}+{overhead} tokens "
                    f"(total: {current_tokens}/{self.effective_max_tokens})"
                )
            else:
                logger.debug(f"Dropped item: {item.tokens}+{overhead} tokens would exceed budget")

        # Restore insertion order
        selected.sort(key=lambda x: x.insertion_index)

        logger.info(
            f"Packed {len(selected)}/{len(self._items)} items using "
            f"{current_tokens}/{self.effective_max_tokens} tokens"
        )
        return selected

    def reset(self) -> "BasePacker":
        """
        Reset the packer, removing all items.

        Returns:
            Self for method chaining
        """
        self._items.clear()
        self._insertion_counter = 0
        logger.debug("Packer reset")
        return self

    def get_items(self) -> List[dict]:
        """
        Get information about all added items.

        Returns:
            List of dictionaries containing item metadata
        """
        return [
            {
                "priority": item.priority,
                "tokens": item.tokens,
                "insertion_index": item.insertion_index,
                "role": item.role,
            }
            for item in self._items
        ]

    @abstractmethod
    def pack(self):
        """
        Pack items into final format.

        Subclasses must implement this to return format-specific output:
        - MessagesPacker: Returns List[Dict[str, str]]
        - TextPacker: Returns str
        """
        pass
