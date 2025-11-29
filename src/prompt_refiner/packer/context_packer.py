"""Context packing operation for managing context budget."""

from dataclasses import dataclass
from typing import List, Optional, Union

from ..analyzer.counter import CountTokens
from ..operation import Operation

# Priority constants - lower values = higher priority
PRIORITY_SYSTEM = 0  # Absolute must-have (e.g., system prompts)
PRIORITY_USER = 10  # Critical user input
PRIORITY_HIGH = 20  # Important context (e.g., core RAG documents)
PRIORITY_MEDIUM = 30  # Normal priority (e.g., general RAG documents)
PRIORITY_LOW = 40  # Optional content (e.g., old conversation history)


@dataclass
class PackableItem:
    """Internal dataclass representing a text chunk with metadata."""

    content: str
    tokens: int
    priority: int
    insertion_index: int


class ContextPacker:
    """
    Context budget manager that packs text items into a token budget.

    Uses a greedy algorithm to select items based on priority while respecting
    the maximum token limit. Items are selected by priority but restored to
    insertion order for natural reading flow.

    Example:
        >>> packer = ContextPacker(max_tokens=1000)
        >>> packer.add_item("System prompt", priority=PRIORITY_SYSTEM)
        >>> packer.add_item("User query", priority=PRIORITY_USER)
        >>> packer.add_item(doc, priority=PRIORITY_HIGH, refine_with=StripHTML())
        >>> final_prompt = packer.pack()
    """

    def __init__(self, max_tokens: int):
        """
        Initialize the context packer.

        Args:
            max_tokens: Maximum token budget (e.g., 4096, 8192)
        """
        self.max_tokens = max_tokens
        self._items: List[PackableItem] = []
        self._insertion_counter = 0
        self._token_counter = CountTokens()

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text using word-based estimation.

        Args:
            text: Text to count tokens in

        Returns:
            Number of tokens (estimated)
        """
        return self._token_counter._estimate_tokens(text)

    def add_item(
        self,
        content: str,
        priority: int = PRIORITY_MEDIUM,
        refine_with: Optional[Union[Operation, List[Operation]]] = None,
    ) -> "ContextPacker":
        """
        Add a text item to the packer.

        Items can be optionally refined (cleaned/processed) before being added.
        This JIT (just-in-time) refinement ensures accurate token counting.

        Args:
            content: Text content to add
            priority: Priority level (lower = more important). Use PRIORITY_* constants.
            refine_with: Optional operation(s) to apply before adding

        Returns:
            Self for method chaining
        """
        # Apply JIT refinement if specified
        processed_content = content
        if refine_with:
            operations = refine_with if isinstance(refine_with, list) else [refine_with]
            for op in operations:
                processed_content = op.process(processed_content)

        # Count tokens (using refined content)
        token_count = self._count_tokens(processed_content)

        # Create and store item
        item = PackableItem(
            content=processed_content,
            tokens=token_count,
            priority=priority,
            insertion_index=self._insertion_counter,
        )
        self._items.append(item)
        self._insertion_counter += 1

        return self

    def pack(self, separator: str = "\n\n") -> str:
        """
        Pack items into the token budget using a greedy algorithm.

        Algorithm:
        1. Sort items by priority (lower number = higher priority)
        2. Greedily select items that fit within budget
        3. Restore selected items to insertion order
        4. Join with separator

        Args:
            separator: String to join packed items

        Returns:
            Packed text string fitting within token budget
        """
        if not self._items:
            return ""

        # Sort by priority (stable sort preserves insertion order for equal priorities)
        sorted_items = sorted(self._items, key=lambda x: (x.priority, x.insertion_index))

        selected_items: List[PackableItem] = []
        current_tokens = 0
        separator_tokens = self._count_tokens(separator)

        # Greedy packing
        for item in sorted_items:
            # Calculate cost including separator (except for first item)
            item_cost = item.tokens
            if selected_items:  # Not the first item
                item_cost += separator_tokens

            if current_tokens + item_cost <= self.max_tokens:
                selected_items.append(item)
                current_tokens += item_cost

        # Restore insertion order for natural reading flow
        selected_items.sort(key=lambda x: x.insertion_index)

        # Join items
        final_text = separator.join(item.content for item in selected_items)

        return final_text

    def reset(self) -> "ContextPacker":
        """
        Reset the packer, removing all items.

        Returns:
            Self for method chaining
        """
        self._items.clear()
        self._insertion_counter = 0
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
            }
            for item in self._items
        ]
