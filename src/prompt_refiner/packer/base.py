"""Base packer with common logic for prompt composition."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Literal, Optional

from ..refiner import Refiner

logger = logging.getLogger(__name__)

# Priority constants - lower values = higher priority
# These are preserved for backward compatibility and can be used for custom sorting
PRIORITY_SYSTEM = 0  # Absolute must-have (e.g., system prompts)
PRIORITY_QUERY = 10  # Current user query (critical for response)
PRIORITY_HIGH = 20  # Important context (e.g., core RAG documents)
PRIORITY_MEDIUM = 30  # Normal priority (e.g., general RAG documents)
PRIORITY_LOW = 40  # Optional content (e.g., old conversation history)

# Semantic roles for RAG applications
ROLE_SYSTEM = "system"  # System instructions (P0, highest priority)
ROLE_QUERY = "query"  # Current user question (P10, high priority)
ROLE_CONTEXT = "context"  # RAG retrieved documents (P20, medium-high priority)
ROLE_USER = "user"  # User messages in conversation history (P40, low priority)
ROLE_ASSISTANT = "assistant"  # Assistant messages in history (P40, low priority)

# Type alias for valid roles
RoleType = Literal["system", "query", "context", "user", "assistant"]


@dataclass
class PackableItem:
    """
    Item to be included in packed output.

    Attributes:
        content: The text content
        priority: Priority value (lower = higher priority, used for sorting)
        insertion_index: Order in which item was added
        role: Optional role for message-based APIs (system, query, context, user, assistant)
    """

    content: str
    priority: int
    insertion_index: int
    role: Optional[RoleType] = None


class BasePacker(ABC):
    """
    Abstract base class for prompt packers.

    Provides common functionality:
    - Adding items with priorities
    - JIT refinement with strategies/operations
    - Priority-based sorting

    Subclasses must implement:
    - pack(): Format and return packed items
    """

    def __init__(
        self,
        track_tokens: bool = False,
        token_counter: Optional[Callable[[str], int]] = None,
    ):
        """
        Initialize packer.

        Args:
            track_tokens: Enable token tracking to measure refinement effectiveness
            token_counter: Function to count tokens (required if track_tokens=True)
        """
        self._items: List[PackableItem] = []
        self._insertion_counter = 0

        # Token tracking
        self._track_tokens = track_tokens
        self._token_counter = token_counter
        self._raw_tokens = 0
        self._refined_tokens = 0

        # Validate: if tracking enabled, counter is required
        if self._track_tokens and self._token_counter is None:
            raise ValueError("token_counter is required when track_tokens=True")

    def add(
        self,
        content: str,
        role: RoleType,
        priority: Optional[int] = None,
        refine_with: Optional[Refiner] = None,
    ) -> "BasePacker":
        """
        Add an item to the packer.

        Args:
            content: Text content to add
            role: Semantic role (required). Use ROLE_* constants:
                - ROLE_SYSTEM: System instructions
                - ROLE_QUERY: Current user question
                - ROLE_CONTEXT: RAG retrieved documents
                - ROLE_USER: User messages in conversation history
                - ROLE_ASSISTANT: Assistant messages in history
            priority: Priority level (use PRIORITY_* constants). If None, infers from role:
                - ROLE_SYSTEM → PRIORITY_SYSTEM (0)
                - ROLE_QUERY → PRIORITY_QUERY (10)
                - ROLE_CONTEXT → PRIORITY_HIGH (20)
                - ROLE_USER/ROLE_ASSISTANT → PRIORITY_LOW (40)
                - Other roles → PRIORITY_MEDIUM (30)
            refine_with: Optional refiner or pipeline to apply before adding.
                Can be:
                - Single refiner: StripHTML()
                - Pipeline: StripHTML() | NormalizeWhitespace()
                - Pipeline from list: Pipeline([StripHTML(), NormalizeWhitespace()])

        Returns:
            Self for method chaining
        """
        # Token tracking: count raw tokens BEFORE refinement
        if self._track_tokens:
            self._raw_tokens += self._token_counter(content)

        # Smart priority defaults based on semantic roles
        if priority is None:
            if role == ROLE_SYSTEM:
                priority = PRIORITY_SYSTEM  # 0 - Highest priority
            elif role == ROLE_QUERY:
                priority = PRIORITY_QUERY  # 10 - Current query is critical
            elif role == ROLE_CONTEXT:
                priority = PRIORITY_HIGH  # 20 - RAG documents
            elif role in (ROLE_USER, ROLE_ASSISTANT):
                priority = PRIORITY_LOW  # 40 - Conversation history
            else:
                priority = PRIORITY_MEDIUM  # 30 - Unknown roles

        # JIT refinement
        refined_content = content
        if refine_with:
            # Apply refinement (Refiner or Pipeline both use process() method)
            refined_content = refine_with.process(content)

        # Token tracking: count refined tokens AFTER refinement
        if self._track_tokens:
            self._refined_tokens += self._token_counter(refined_content)

        content = refined_content

        item = PackableItem(
            content=content,
            priority=priority,
            insertion_index=self._insertion_counter,
            role=role,
        )

        self._items.append(item)
        self._insertion_counter += 1

        logger.debug(f"Added item: priority={priority}, role={role}")
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

    def _select_items(self) -> List[PackableItem]:
        """
        Select and sort all items by priority, then restore insertion order.

        Algorithm:
        1. Sort items by priority (lower value = higher priority, stable sort)
        2. Restore insertion order for natural reading flow

        Returns:
            List of all items in insertion order
        """
        if not self._items:
            return []

        # Sort by priority (stable sort preserves insertion order for equal priorities)
        sorted_items = sorted(self._items, key=lambda x: (x.priority, x.insertion_index))

        # Restore insertion order for natural reading flow
        sorted_items.sort(key=lambda x: x.insertion_index)

        logger.info(f"Packed all {len(self._items)} items")
        return sorted_items

    def reset(self) -> "BasePacker":
        """
        Reset the packer, removing all items and token stats.

        Returns:
            Self for method chaining
        """
        self._items.clear()
        self._insertion_counter = 0

        # Reset token tracking
        if self._track_tokens:
            self._raw_tokens = 0
            self._refined_tokens = 0

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
                "insertion_index": item.insertion_index,
                "role": item.role,
            }
            for item in self._items
        ]

    @property
    def token_stats(self) -> Dict[str, Any]:
        """
        Get token savings statistics (only available when track_tokens=True).

        Returns:
            Dictionary with the following keys:
                - raw_tokens: int - Total tokens before refinement
                - refined_tokens: int - Total tokens after refinement
                - saved_tokens: int - Tokens saved by refinement
                - saving_percent: str - Percentage saved (e.g., "25.5%")

        Raises:
            ValueError: If token tracking is not enabled

        Example:
            >>> packer = MessagesPacker(track_tokens=True, token_counter=character_based_counter)
            >>> packer.add("<div>Hello</div>", role="user", refine_with=StripHTML())
            >>> stats = packer.token_stats
            >>> print(stats)
            {'raw_tokens': 17, 'refined_tokens': 5, 'saved_tokens': 12, 'saving_percent': '70.6%'}
        """
        if not self._track_tokens:
            raise ValueError(
                "Token tracking is not enabled. "
                "Create packer with track_tokens=True and provide a token_counter."
            )

        saved = self._raw_tokens - self._refined_tokens
        percent = (saved / self._raw_tokens * 100) if self._raw_tokens > 0 else 0.0

        return {
            "raw_tokens": self._raw_tokens,
            "refined_tokens": self._refined_tokens,
            "saved_tokens": saved,
            "saving_percent": f"{percent:.1f}%",
        }

    @abstractmethod
    def pack(self):
        """
        Pack items into final format.

        Subclasses must implement this to return format-specific output:
        - MessagesPacker: Returns List[Dict[str, str]]
        - TextPacker: Returns str
        """
        pass
