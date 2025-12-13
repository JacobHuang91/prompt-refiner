"""Base refiner class for prompt processing."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline import Pipeline


class Refiner(ABC):
    """Base class for all prompt refining operations."""

    @abstractmethod
    def process(self, text: str) -> str:
        """
        Process the input text.

        Args:
            text: The input text to process

        Returns:
            The processed text
        """
        pass

    def __or__(self, other: "Refiner") -> "Pipeline":
        """
        Support pipe operator syntax for composing refiners.

        Enables LangChain-style pipeline composition: refiner1 | refiner2 | refiner3

        Args:
            other: The refiner to chain with this refiner

        Returns:
            A Pipeline containing both refiners

        Example:
            >>> from prompt_refiner import StripHTML, NormalizeWhitespace
            >>> pipeline = StripHTML() | NormalizeWhitespace()
            >>> result = pipeline.run("<div>  hello  </div>")
            >>> # Returns: "hello"
        """
        from .pipeline import Pipeline

        return Pipeline().pipe(self).pipe(other)
