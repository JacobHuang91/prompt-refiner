"""Main Refiner class for building prompt processing pipelines."""

from typing import List

from .operation import Operation


class Refiner:
    """A pipeline builder for prompt refining operations."""

    def __init__(self):
        """Initialize an empty refiner pipeline."""
        self._operations: List[Operation] = []

    def pipe(self, operation: Operation) -> "Refiner":
        """
        Add an operation to the pipeline.

        Args:
            operation: The operation to add

        Returns:
            Self for method chaining
        """
        self._operations.append(operation)
        return self

    def run(self, text: str) -> str:
        """
        Execute the pipeline on the input text.

        Args:
            text: The input text to process

        Returns:
            The processed text after all operations
        """
        result = text
        for operation in self._operations:
            result = operation.process(result)
        return result

    def __or__(self, other: Operation) -> "Refiner":
        """
        Support pipe operator syntax for adding operations to the pipeline.

        Enables continued chaining: (op1 | op2) | op3

        Args:
            other: The operation to add to the pipeline

        Returns:
            Self for method chaining

        Example:
            >>> from prompt_refiner import StripHTML, NormalizeWhitespace, TruncateTokens
            >>> pipeline = StripHTML() | NormalizeWhitespace() | TruncateTokens(max_tokens=100)
            >>> result = pipeline.run(text)
        """
        return self.pipe(other)
