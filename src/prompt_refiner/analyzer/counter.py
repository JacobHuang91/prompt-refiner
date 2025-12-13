"""Token counting and analysis operation."""

import logging
import math
from typing import Optional

from ..refiner import Refiner

logger = logging.getLogger(__name__)


class CountTokens(Refiner):
    """Count tokens and provide statistics before/after processing.

    Supports two modes:
    - Precise mode: Uses tiktoken if installed (pip install llm-prompt-refiner[token])
    - Estimation mode: Uses character-based approximation (1 token ≈ 4 characters)
    """

    def __init__(self, original_text: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the token counter.

        Args:
            original_text: Optional original text to compare against
            model: Model name for tiktoken encoding. If None, uses character-based
                   estimation. If specified, attempts to use tiktoken for precise counting.
        """
        self.original_text = original_text
        self.model = model
        self._stats: Optional[dict] = None
        self.is_precise = False
        self._encoding = None

        # Only try tiktoken if user explicitly requests it by passing a model
        if model is not None:
            try:
                import tiktoken

                try:
                    self._encoding = tiktoken.encoding_for_model(model)
                except KeyError:
                    # Fall back to cl100k_base if model not found
                    self._encoding = tiktoken.get_encoding("cl100k_base")
                self.is_precise = True
                logger.debug(f"Using tiktoken for precise token counting (model: {model})")
            except ImportError:
                # User requested precise mode but tiktoken not installed
                self.is_precise = False
                logger.warning(
                    f"Model '{model}' specified but tiktoken not installed. "
                    "Falling back to character-based estimation. "
                    "Install with: pip install llm-prompt-refiner[token]"
                )
        else:
            # User didn't specify model - use estimation mode directly
            self.is_precise = False
            logger.debug("Using character-based token estimation (model not specified)")

    def _estimate_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Uses precise counting with tiktoken if available, otherwise falls back
        to character-based estimation (1 token ≈ 4 characters).

        Args:
            text: The input text

        Returns:
            Token count (precise or estimated)
        """
        if not text:
            return 0

        # Precise mode: Use tiktoken
        if self.is_precise and self._encoding:
            try:
                return len(self._encoding.encode_ordinary(text))
            except Exception as e:
                logger.warning(f"tiktoken encoding failed: {e}. Falling back to estimation.")
                # Fall through to estimation mode

        # Estimation mode: 1 token ≈ 4 characters
        # Using ceiling to be conservative (avoid underestimation)
        return math.ceil(len(text) / 4)

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
