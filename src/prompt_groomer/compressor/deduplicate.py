"""Deduplication operation for removing similar text chunks."""

from typing import Literal

from ..operation import Operation


class Deduplicate(Operation):
    """Remove duplicate or highly similar text chunks (useful for RAG contexts)."""

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        method: Literal["levenshtein", "jaccard"] = "jaccard",
        granularity: Literal["sentence", "paragraph"] = "paragraph",
    ):
        """
        Initialize the deduplication operation.

        Args:
            similarity_threshold: Threshold for considering text similar (0.0-1.0)
            method: Similarity calculation method
                - "levenshtein": Levenshtein distance (character-based)
                - "jaccard": Jaccard similarity (word-based, faster)
            granularity: Text granularity to deduplicate at
                - "sentence": Deduplicate at sentence level
                - "paragraph": Deduplicate at paragraph level
        """
        self.similarity_threshold = similarity_threshold
        self.method = method
        self.granularity = granularity

    def _split_text(self, text: str) -> list[str]:
        """
        Split text into chunks based on granularity.

        Args:
            text: The input text

        Returns:
            List of text chunks
        """
        if self.granularity == "sentence":
            # Simple sentence splitting
            import re

            sentences = re.split(r"(?<=[.!?])\s+", text)
            return [s.strip() for s in sentences if s.strip()]
        else:  # paragraph
            # Split by double newlines
            paragraphs = text.split("\n\n")
            return [p.strip() for p in paragraphs if p.strip()]

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate Jaccard similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0-1.0)
        """
        # Convert to word sets
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _levenshtein_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate normalized Levenshtein similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0-1.0)
        """
        # Levenshtein distance implementation
        if text1 == text2:
            return 1.0

        len1, len2 = len(text1), len(text2)
        if len1 == 0 or len2 == 0:
            return 0.0

        # Create distance matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        # Initialize first row and column
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j

        # Calculate distances
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if text1[i - 1] == text2[j - 1] else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,  # deletion
                    matrix[i][j - 1] + 1,  # insertion
                    matrix[i - 1][j - 1] + cost,  # substitution
                )

        distance = matrix[len1][len2]
        max_len = max(len1, len2)

        # Normalize to similarity score
        return 1.0 - (distance / max_len)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using configured method.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0-1.0)
        """
        if self.method == "jaccard":
            return self._jaccard_similarity(text1, text2)
        else:  # levenshtein
            return self._levenshtein_similarity(text1, text2)

    def process(self, text: str) -> str:
        """
        Remove duplicate or similar text chunks.

        Args:
            text: The input text

        Returns:
            Text with duplicates removed
        """
        chunks = self._split_text(text)

        if not chunks:
            return text

        # Keep track of unique chunks
        unique_chunks = []
        seen_chunks = []

        for chunk in chunks:
            is_duplicate = False

            # Check similarity with all previously seen chunks
            for seen_chunk in seen_chunks:
                similarity = self._calculate_similarity(chunk, seen_chunk)
                if similarity >= self.similarity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_chunks.append(chunk)
                seen_chunks.append(chunk)

        # Reconstruct text
        if self.granularity == "paragraph":
            return "\n\n".join(unique_chunks)
        else:  # sentence
            return " ".join(unique_chunks)
