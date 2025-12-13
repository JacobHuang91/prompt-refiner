"""Standard refining strategy with deduplication."""

from typing import Literal

from ..cleaner import NormalizeWhitespace, StripHTML
from ..compressor import Deduplicate
from ..pipeline import Pipeline


class StandardStrategy(Pipeline):
    """
    Standard strategy: Cleaning plus deduplication.

    This strategy is itself a Pipeline, so you can use it directly or extend it.

    Refiners:
    - StripHTML: Remove HTML tags (optional)
    - NormalizeWhitespace: Collapse excessive whitespace
    - Deduplicate: Remove similar content

    Characteristics:
    - Token reduction: ~4.8%
    - Quality: 98.4% (cosine similarity)
    - Use case: RAG contexts with potential duplicates
    - Latency: 0.25ms per 1k tokens

    Example:
        >>> # Use with defaults
        >>> strategy = StandardStrategy()
        >>> cleaned = strategy.run(text)
        >>>
        >>> # Customize operator parameters
        >>> strategy = StandardStrategy(
        ...     strip_html_to_markdown=True,
        ...     deduplicate_method="levenshtein",
        ...     deduplicate_similarity_threshold=0.9,
        ...     deduplicate_granularity="paragraph"
        ... )
        >>> cleaned = strategy.run(text)
        >>>
        >>> # Extend with additional operators
        >>> extended = StandardStrategy().pipe(TruncateTokens(max_tokens=500))
        >>> cleaned = extended.run(text)
    """

    def __init__(
        self,
        # Parameters to configure StripHTML operator
        strip_html: bool = True,
        strip_html_to_markdown: bool = False,
        # Parameters to configure Deduplicate operator
        deduplicate_method: Literal["jaccard", "levenshtein"] = "jaccard",
        deduplicate_similarity_threshold: float = 0.8,
        deduplicate_granularity: Literal["sentence", "paragraph"] = "sentence",
    ):
        """
        Initialize standard strategy with configured operators.

        Args:
            strip_html: Whether to include StripHTML operator (default: True)
            strip_html_to_markdown: Convert HTML to Markdown instead of stripping (default: False)
            deduplicate_method: Deduplication method (default: "jaccard")
            deduplicate_similarity_threshold: Similarity threshold (default: 0.8)
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

        # Initialize Pipeline with the configured operators
        super().__init__(operations)
