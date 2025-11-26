"""Token counting and analysis operation."""

from typing import Optional

from ..operation import Operation


class CountTokens(Operation):
    """Count tokens and provide statistics before/after processing."""

    def __init__(self, original_text: Optional[str] = None):
        """
        Initialize the token counter.

        Args:
            original_text: Optional original text to compare against
        """
        self.original_text = original_text
        self._stats: Optional[dict] = None

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count.

        Simple approximation: ~1 token per word.
        For more accurate counting, use tiktoken as an optional dependency.

        Args:
            text: The input text

        Returns:
            Estimated token count
        """
        return len(text.split())

    def process(self, text: str) -> str:
        """
        Count tokens in the text and store statistics.

        This operation doesn't modify the text, it just analyzes it.

        Args:
            text: The input text

        Returns:
            The same text (unchanged)
        """
        current_tokens = self._estimate_tokens(text)

        if self.original_text is not None:
            original_tokens = self._estimate_tokens(self.original_text)
            saved_tokens = original_tokens - current_tokens
            saving_percent = (saved_tokens / original_tokens * 100) if original_tokens > 0 else 0

            self._stats = {
                "original": original_tokens,
                "cleaned": current_tokens,
                "saved": saved_tokens,
                "saving_percent": f"{saving_percent:.1f}%",
            }
        else:
            self._stats = {
                "tokens": current_tokens,
            }

        return text

    def get_stats(self) -> dict:
        """
        Get token statistics.

        Returns:
            Dictionary containing token statistics
        """
        return self._stats or {}

    def format_stats(self) -> str:
        """
        Format statistics as a human-readable string.

        Returns:
            Formatted statistics string
        """
        if not self._stats:
            return "No statistics available"

        if "original" in self._stats:
            return (
                f"Original: {self._stats['original']} tokens\n"
                f"Cleaned: {self._stats['cleaned']} tokens\n"
                f"Saved: {self._stats['saved']} tokens ({self._stats['saving_percent']})"
            )
        else:
            return f"Tokens: {self._stats['tokens']}"
