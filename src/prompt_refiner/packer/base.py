"""Base packer with common logic for token budget management."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

from ..analyzer.counter import CountTokens
from ..refiner import Refiner

if TYPE_CHECKING:
    from ..pipeline import Pipeline

logger = logging.getLogger(__name__)

# Priority constants - lower values = higher priority
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
    Item to be packed into token budget.

    Attributes:
        content: The text content
        tokens: Base token count (without format overhead)
        priority: Priority value (lower = higher priority)
        insertion_index: Order in which item was added
        role: Optional role for message-based APIs (system, query, context, user, assistant)
    """

    content: str
    tokens: int
    priority: int
    insertion_index: int
    role: Optional[RoleType] = None


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

    def __init__(
        self,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        track_savings: bool = False,
    ):
        """
        Initialize packer with optional token budget.

        Args:
            max_tokens: Maximum token budget. If None, includes all items without limit.
            model: Optional model name for precise token counting (requires tiktoken)
            track_savings: Enable automatic token savings tracking for refine_with
                operations (default: False)
        """
        self.raw_max_tokens = max_tokens
        self._items: List[PackableItem] = []
        self._insertion_counter = 0
        self._token_counter = CountTokens(model=model)

        # Token savings tracking (opt-in)
        self.track_savings = track_savings
        self._savings_stats = {
            "original_tokens": 0,  # Sum of tokens before refinement
            "refined_tokens": 0,  # Sum of tokens after refinement
            "items_refined": 0,  # Count of items that used refine_with
        }

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
        role: RoleType,
        priority: Optional[int] = None,
        refine_with: Optional[Union[Refiner, "Pipeline"]] = None,
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

        # JIT refinement with optional tracking
        if refine_with:
            # Track original tokens before refinement (if tracking enabled)
            original_content = content if self.track_savings else None

            # Apply refinement (Refiner or Pipeline both use process() method)
            content = refine_with.process(content)

            # Update savings statistics (if tracking enabled)
            if self.track_savings and original_content is not None:
                original_tokens = self._count_tokens(original_content)
                refined_tokens = self._count_tokens(content)
                self._savings_stats["original_tokens"] += original_tokens
                self._savings_stats["refined_tokens"] += refined_tokens
                self._savings_stats["items_refined"] += 1

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
        1. Sort items by priority (lower value = higher priority, stable sort)
        2. If max_tokens is None, return all sorted items (maintains priority order)
        3. Otherwise, greedily select items that fit within budget (including overhead)
        4. Restore insertion order for natural reading flow (limited mode only)

        Returns:
            List of selected items:
            - Unlimited mode: Sorted by (priority, insertion_index)
            - Limited mode: Restored to insertion order after selection
        """
        if not self._items:
            return []

        # Sort by priority (stable sort preserves insertion order for equal priorities)
        sorted_items = sorted(self._items, key=lambda x: (x.priority, x.insertion_index))

        # Unlimited mode: include all items (sorted by priority)
        if self.effective_max_tokens is None:
            logger.info(f"Unlimited mode: packed all {len(self._items)} items (sorted by priority)")
            return sorted_items

        # Limited mode: greedy selection
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
        Reset the packer, removing all items and clearing savings statistics.

        Returns:
            Self for method chaining
        """
        self._items.clear()
        self._insertion_counter = 0

        # Reset savings tracking
        if self.track_savings:
            self._savings_stats = {
                "original_tokens": 0,
                "refined_tokens": 0,
                "items_refined": 0,
            }

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

    def get_token_savings(self) -> dict:
        """
        Get token savings statistics from refinement operations.

        Only includes items that used refine_with parameter. Items added
        without refinement are not counted.

        Returns:
            Dictionary with savings statistics:
            - original_tokens: Total tokens before refinement
            - refined_tokens: Total tokens after refinement
            - saved_tokens: Tokens saved (original - refined)
            - saving_percent: Percentage saved as formatted string (e.g., "12.5%")
            - items_refined: Number of items that were refined

            Returns empty dict if track_savings=False or no items refined.

        Example:
            >>> packer = MessagesPacker(max_tokens=1000, track_savings=True)
            >>> packer.add(html_doc, role=ROLE_CONTEXT, refine_with=StripHTML())
            >>> messages = packer.pack()
            >>> stats = packer.get_token_savings()
            >>> print(f"Saved {stats['saved_tokens']} tokens ({stats['saving_percent']})")
        """
        if not self.track_savings:
            logger.debug("Token savings tracking is disabled. Enable with track_savings=True")
            return {}

        if self._savings_stats["items_refined"] == 0:
            logger.debug("No items have been refined yet")
            return {}

        original = self._savings_stats["original_tokens"]
        refined = self._savings_stats["refined_tokens"]
        saved = original - refined
        saving_percent = (saved / original * 100) if original > 0 else 0.0

        return {
            "original_tokens": original,
            "refined_tokens": refined,
            "saved_tokens": saved,
            "saving_percent": f"{saving_percent:.1f}%",
            "items_refined": self._savings_stats["items_refined"],
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
