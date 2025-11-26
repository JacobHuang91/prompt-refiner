"""Whitespace normalization operation."""

from ..operation import Operation


class NormalizeWhitespace(Operation):
    """Normalize whitespace in text."""

    def process(self, text: str) -> str:
        """
        Normalize whitespace by collapsing multiple spaces into one.

        Args:
            text: The input text

        Returns:
            Text with normalized whitespace
        """
        # Replace multiple whitespace with single space and strip edges
        return " ".join(text.split())
