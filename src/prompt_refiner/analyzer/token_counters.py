"""Built-in token counting functions for common use cases."""

import math
from typing import Callable


def character_based_counter(text: str) -> int:
    """
    Estimate tokens using character-based approximation.

    Uses conservative estimate: 1 token ≈ 4 characters.
    Fast but less accurate than model-specific counters.

    Args:
        text: Input text to count tokens for

    Returns:
        Estimated token count

    Example:
        >>> character_based_counter("Hello World")
        3
        >>> character_based_counter("A longer sentence with many words")
        9
    """
    if not text:
        return 0
    return math.ceil(len(text) / 4)


def word_based_counter(text: str) -> int:
    """
    Estimate tokens using word count approximation.

    Uses estimate: 1 token ≈ 1 word.
    Reasonable for English text.

    Args:
        text: Input text to count tokens for

    Returns:
        Estimated token count based on word splits

    Example:
        >>> word_based_counter("Hello World")
        2
        >>> word_based_counter("A longer sentence with many words")
        6
    """
    if not text:
        return 0
    return len(text.split())


def create_tiktoken_counter(model: str = "gpt-4") -> Callable[[str], int]:
    """
    Create a tiktoken-based counter for precise token counting.

    Requires tiktoken to be installed. Use this for accurate token counts
    when working with specific models.

    Args:
        model: Model name for tokenizer selection (e.g., "gpt-4", "gpt-3.5-turbo")

    Returns:
        Token counting function that uses tiktoken

    Raises:
        ImportError: If tiktoken is not installed

    Example:
        >>> counter = create_tiktoken_counter(model="gpt-4")
        >>> counter("Hello World")
        2

        >>> # If tiktoken not installed:
        >>> try:
        ...     counter = create_tiktoken_counter()
        ... except ImportError as e:
        ...     print("Install tiktoken: pip install llm-prompt-refiner[token]")
    """
    try:
        import tiktoken
    except ImportError:
        raise ImportError(
            "tiktoken is required for precise token counting. "
            "Install with: pip install llm-prompt-refiner[token]"
        )

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base (used by gpt-4, gpt-3.5-turbo)
        encoding = tiktoken.get_encoding("cl100k_base")

    def counter(text: str) -> int:
        """Count tokens using tiktoken encoding."""
        if not text:
            return 0
        return len(encoding.encode(text))

    return counter
