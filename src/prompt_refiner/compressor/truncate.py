"""Token truncation operation."""

import re
from typing import Literal

from ..refiner import Refiner


class TruncateTokens(Refiner):
    """Truncate text to a maximum number of tokens with intelligent sentence boundary detection."""

    def __init__(
        self,
        max_tokens: int,
        strategy: Literal["head", "tail", "middle_out"] = "head",
        respect_sentence_boundary: bool = True,
    ):
        """
        Initialize the truncation operation.

        Args:
            max_tokens: Maximum number of tokens to keep
            strategy: Truncation strategy:
                - "head": Keep the beginning of the text
                - "tail": Keep the end of the text (useful for conversation history)
                - "middle_out": Keep beginning and end, remove middle
            respect_sentence_boundary: If True, truncate at sentence boundaries
        """
        self.max_tokens = max_tokens
        self.strategy = strategy
        self.respect_sentence_boundary = respect_sentence_boundary

    def _split_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences.

        Args:
            text: The input text

        Returns:
            List of sentences
        """
        # Simple sentence splitter that handles common cases
        # Matches sentence-ending punctuation followed by space and capital letter
        sentence_pattern = r"(?<=[.!?。!?])\s+(?=[A-Z\u4e00-\u9fff])"
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count.

        Simple approximation: ~1 token per word.
        Will be improved with actual tokenization later.

        Args:
            text: The input text

        Returns:
            Estimated token count
        """
        return len(text.split())

    def process(self, text: str) -> str:
        """
        Truncate text to max_tokens.

        Args:
            text: The input text

        Returns:
            Truncated text respecting sentence boundaries if configured
        """
        estimated_tokens = self._estimate_tokens(text)

        if estimated_tokens <= self.max_tokens:
            return text

        if self.respect_sentence_boundary:
            sentences = self._split_sentences(text)

            if self.strategy == "head":
                return self._truncate_head_sentences(sentences)
            elif self.strategy == "tail":
                return self._truncate_tail_sentences(sentences)
            elif self.strategy == "middle_out":
                return self._truncate_middle_out_sentences(sentences)
        else:
            # Fallback to word-based truncation
            words = text.split()

            if self.strategy == "head":
                return " ".join(words[: self.max_tokens])
            elif self.strategy == "tail":
                return " ".join(words[-self.max_tokens :])
            elif self.strategy == "middle_out":
                half = self.max_tokens // 2
                start_words = words[:half]
                end_words = words[-(self.max_tokens - half) :]
                return " ".join(start_words) + " ... " + " ".join(end_words)

        return text

    def _truncate_head_sentences(self, sentences: list[str]) -> str:
        """Keep sentences from the beginning until we hit the token limit."""
        result = []
        token_count = 0

        for sentence in sentences:
            sentence_tokens = self._estimate_tokens(sentence)
            if token_count + sentence_tokens <= self.max_tokens:
                result.append(sentence)
                token_count += sentence_tokens
            else:
                break

        return " ".join(result) if result else sentences[0][: self.max_tokens * 5]

    def _truncate_tail_sentences(self, sentences: list[str]) -> str:
        """Keep sentences from the end until we hit the token limit."""
        result = []
        token_count = 0

        for sentence in reversed(sentences):
            sentence_tokens = self._estimate_tokens(sentence)
            if token_count + sentence_tokens <= self.max_tokens:
                result.insert(0, sentence)
                token_count += sentence_tokens
            else:
                break

        return " ".join(result) if result else sentences[-1][-self.max_tokens * 5 :]

    def _truncate_middle_out_sentences(self, sentences: list[str]) -> str:
        """Keep sentences from beginning and end, truncate middle."""
        if not sentences:
            return ""

        head = []
        tail = []
        head_tokens = 0
        tail_tokens = 0
        half_tokens = self.max_tokens // 2

        # Collect head sentences
        for sentence in sentences:
            sentence_tokens = self._estimate_tokens(sentence)
            if head_tokens + sentence_tokens <= half_tokens:
                head.append(sentence)
                head_tokens += sentence_tokens
            else:
                break

        # Collect tail sentences
        for sentence in reversed(sentences):
            sentence_tokens = self._estimate_tokens(sentence)
            if tail_tokens + sentence_tokens <= (self.max_tokens - head_tokens):
                tail.insert(0, sentence)
                tail_tokens += sentence_tokens
            else:
                break

        # Avoid duplicating sentences
        if head and tail and head[-1] == tail[0]:
            tail = tail[1:]

        if not head and not tail:
            return sentences[0][: self.max_tokens * 5]

        return " ".join(head) + " ... " + " ".join(tail)
