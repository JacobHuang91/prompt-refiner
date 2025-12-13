"""Minimal refining strategy for maximum quality preservation."""

from ..cleaner import NormalizeWhitespace, StripHTML
from ..pipeline import Pipeline


class MinimalStrategy(Pipeline):
    """
    Minimal strategy: Basic cleaning with minimal token reduction.

    This strategy is itself a Pipeline, so you can use it directly or extend it.

    Refiners:
    - StripHTML: Remove HTML tags (optional)
    - NormalizeWhitespace: Collapse excessive whitespace

    Characteristics:
    - Token reduction: ~4.3%
    - Quality: 98.7% (cosine similarity)
    - Use case: When quality is paramount, minimal risk
    - Latency: 0.05ms per 1k tokens

    Example:
        >>> # Use with defaults
        >>> strategy = MinimalStrategy()
        >>> cleaned = strategy.run(text)
        >>>
        >>> # Customize operators
        >>> strategy = MinimalStrategy(
        ...     strip_html_to_markdown=True
        ... )
        >>> cleaned = strategy.run(text)
        >>>
        >>> # Extend with additional operators
        >>> extended = MinimalStrategy().pipe(RedactPII())
        >>> cleaned = extended.run(text)
    """

    def __init__(
        self,
        strip_html: bool = True,
        strip_html_to_markdown: bool = False,
    ):
        """
        Initialize minimal strategy with configured operators.

        Args:
            strip_html: Whether to include StripHTML operator (default: True)
            strip_html_to_markdown: Convert HTML to Markdown instead of stripping (default: False)
        """
        operations = []

        if strip_html:
            operations.append(StripHTML(to_markdown=strip_html_to_markdown))

        operations.append(NormalizeWhitespace())

        # Initialize Pipeline with the configured operators
        super().__init__(operations)
