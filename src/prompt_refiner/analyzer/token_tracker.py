"""Token tracker for measuring refiner/pipeline optimization impact."""

from typing import Callable, Optional

from ..refiner import Refiner


class TokenTracker:
    """
    Context manager for tracking token usage in refiners/pipelines.

    Wraps any Refiner (operation, pipeline, or strategy) and tracks
    token counts before and after processing. Users provide their own
    token counting function for maximum flexibility.

    Example:
        >>> def count_tokens(text: str) -> int:
        ...     # User's custom counter (tiktoken, character-based, etc.)
        ...     return len(text) // 4
        >>>
        >>> refiner = StripHTML() | NormalizeWhitespace()
        >>> with TokenTracker(refiner, count_tokens) as tracker:
        ...     result = tracker.process("<div>Hello   World</div>")
        >>>
        >>> print(tracker.stats)
        {'original_tokens': 28, 'refined_tokens': 12, 'saved_tokens': 16, 'saving_percent': '57.1%'}
    """

    def __init__(
        self,
        refiner: Refiner,
        token_counter: Callable[[str], int],
    ):
        """
        Initialize token tracker.

        Args:
            refiner: Any Refiner (operation or pipeline) to track
            token_counter: Function that counts tokens in text.
                Should accept a string and return an integer token count.
        """
        self._refiner = refiner
        self._counter = token_counter
        self._original_tokens: Optional[int] = None
        self._refined_tokens: Optional[int] = None
        self._original_text: Optional[str] = None
        self._result: Optional[str] = None

    def __enter__(self) -> "TokenTracker":
        """Enter context - returns self for method access."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - cleanup if needed."""
        # No cleanup needed, but required for context manager protocol
        pass

    def process(self, text: str) -> str:
        """
        Process text through refiner and track tokens.

        Args:
            text: Input text to process

        Returns:
            Processed text from the refiner

        Example:
            >>> with TokenTracker(StripHTML(), lambda t: len(t)//4) as tracker:
            ...     result = tracker.process("<p>Hello</p>")
            ...     print(tracker.stats["saved_tokens"])
            3
        """
        # Track original
        self._original_text = text
        self._original_tokens = self._counter(text)

        # Process through refiner
        self._result = self._refiner.process(text)

        # Track refined
        self._refined_tokens = self._counter(self._result)

        return self._result

    @property
    def stats(self) -> dict:
        """
        Get token statistics.

        Returns:
            Dictionary with:
            - original_tokens: Tokens before processing
            - refined_tokens: Tokens after processing
            - saved_tokens: Tokens saved (original - refined)
            - saving_percent: Percentage saved as formatted string (e.g., "12.5%")

            Returns empty dict if process() hasn't been called yet.

        Example:
            >>> with TokenTracker(StripHTML(), lambda t: len(t)//4) as tracker:
            ...     tracker.process("<div>Test</div>")
            ...     stats = tracker.stats
            ...     print(f"Saved {stats['saved_tokens']} tokens")
            Saved 3 tokens
        """
        if self._original_tokens is None:
            return {}

        saved = self._original_tokens - self._refined_tokens
        percent = (saved / self._original_tokens * 100) if self._original_tokens > 0 else 0.0

        return {
            "original_tokens": self._original_tokens,
            "refined_tokens": self._refined_tokens,
            "saved_tokens": saved,
            "saving_percent": f"{percent:.1f}%",
        }

    @property
    def original_text(self) -> Optional[str]:
        """
        Get the original input text.

        Returns:
            The text passed to process(), or None if process() hasn't been called
        """
        return self._original_text

    @property
    def result(self) -> Optional[str]:
        """
        Get the processed result text.

        Returns:
            The refined text returned by process(), or None if process() hasn't been called
        """
        return self._result
