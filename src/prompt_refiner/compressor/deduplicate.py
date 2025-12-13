"""Deduplication operation for removing similar text chunks."""

from typing import Literal

from ..refiner import Refiner


class Deduplicate(Refiner):
    """Remove duplicate or highly similar text chunks (useful for RAG contexts).

    Performance Characteristics:
        This operation uses an O(n²) comparison algorithm, where each chunk is
        compared against all previously seen chunks. The total complexity is
        O(n² × comparison_cost), where comparison_cost depends on the selected
        similarity method:
        - Jaccard: O(m) where m is the chunk length (word-based)
        - Levenshtein: O(m₁ × m₂) where m₁, m₂ are the chunk lengths (character-based)

        For typical RAG contexts (10-50 chunks), performance is acceptable with
        either method. For larger inputs (200+ chunks), consider using paragraph
        granularity to reduce the number of comparisons, or use Jaccard method
        for better performance.
    """

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
                - "jaccard": Jaccard similarity (word-based, faster)
                    * Complexity: O(m) per comparison where m is chunk length
                    * Recommended for most use cases (10-200 chunks)
                    * Fast even with long chunks
                - "levenshtein": Levenshtein distance (character-based)
                    * Complexity: O(m₁ × m₂) per comparison
                    * More precise but computationally expensive
                    * Can be slow with long chunks (1000+ characters)
            granularity: Text granularity to deduplicate at
                - "sentence": Deduplicate at sentence level
                    * More comparisons (more chunks) but smaller chunk sizes
                    * Better for fine-grained deduplication
                - "paragraph": Deduplicate at paragraph level
                    * Fewer comparisons but larger chunk sizes
                    * Recommended for large documents to reduce n² scaling
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

        Performance Note:
            This method uses O(n²) comparisons where n is the number of chunks.
            For large inputs (200+ chunks), consider using paragraph granularity
            to reduce the number of chunks, or ensure you're using the jaccard
            method for better performance.
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
