"""Aggressive refining strategy for maximum token reduction."""

from typing import Literal

from ..cleaner import NormalizeWhitespace, StripHTML
from ..compressor import Deduplicate, TruncateTokens
from ..pipeline import Pipeline


class AggressiveStrategy(Pipeline):
    """
    Aggressive strategy: Maximum token reduction with truncation.

    This strategy is itself a Pipeline, so you can use it directly or extend it.

    Refiners:
    - StripHTML: Remove HTML tags (optional)
    - NormalizeWhitespace: Collapse excessive whitespace
    - Deduplicate: Remove similar content
    - TruncateTokens: Limit to max_tokens

    Characteristics:
    - Token reduction: ~15% (up to 74% on long contexts)
    - Quality: 96.4% (cosine similarity)
    - Use case: Cost optimization, long contexts, lenient quality requirements
    - Latency: 0.25ms per 1k tokens

    Example:
        >>> # Use with defaults
        >>> strategy = AggressiveStrategy()
        >>> cleaned = strategy.run(text)
        >>>
        >>> # Customize operator parameters
        >>> strategy = AggressiveStrategy(
        ...     truncate_max_tokens=500,
        ...     truncate_strategy="tail",
        ...     strip_html_to_markdown=True,
        ...     deduplicate_method="levenshtein",
        ...     deduplicate_similarity_threshold=0.9,
        ...     deduplicate_granularity="paragraph"
        ... )
        >>> cleaned = strategy.run(text)
        >>>
        >>> # Extend with additional operators
        >>> extended = AggressiveStrategy().pipe(RedactPII())
        >>> cleaned = extended.run(text)
    """

    def __init__(
        self,
        # Parameters to configure TruncateTokens operator
        truncate_max_tokens: int = 150,
        truncate_strategy: Literal["head", "tail", "middle_out"] = "head",
        # Parameters to configure StripHTML operator
        strip_html: bool = True,
        strip_html_to_markdown: bool = False,
        # Parameters to configure Deduplicate operator
        deduplicate_method: Literal["jaccard", "levenshtein"] = "jaccard",
        deduplicate_similarity_threshold: float = 0.7,
        deduplicate_granularity: Literal["sentence", "paragraph"] = "sentence",
    ):
        """
        Initialize aggressive strategy with configured operators.

        Args:
            truncate_max_tokens: Maximum tokens to keep (default: 150)
            truncate_strategy: Truncation strategy (default: "head")
            strip_html: Whether to include StripHTML operator (default: True)
            strip_html_to_markdown: Convert HTML to Markdown instead of stripping (default: False)
            deduplicate_method: Deduplication method (default: "jaccard")
            deduplicate_similarity_threshold: Similarity threshold (default: 0.7)
            deduplicate_granularity: Deduplication granularity (default: "sentence")
        """
        operations = []

        if strip_html:
            operations.append(StripHTML(to_markdown=strip_html_to_markdown))

        operations.append(NormalizeWhitespace())

        operations.append(
            Deduplicate(
                method=deduplicate_method,
                similarity_threshold=deduplicate_similarity_threshold,
                granularity=deduplicate_granularity,
            )
        )

        operations.append(
            TruncateTokens(
                max_tokens=truncate_max_tokens,
                strategy=truncate_strategy,
            )
        )

        # Initialize Pipeline with the configured operators
        super().__init__(operations)
