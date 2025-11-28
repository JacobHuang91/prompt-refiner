"""Base operation class for prompt processing."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .refiner import Refiner


class Operation(ABC):
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

    def __or__(self, other: "Operation") -> "Refiner":
        """
        Support pipe operator syntax for composing operations.

        Enables LangChain-style pipeline composition: op1 | op2 | op3

        Args:
            other: The operation to chain with this operation

        Returns:
            A Refiner pipeline containing both operations

        Example:
            >>> from prompt_refiner import StripHTML, NormalizeWhitespace
            >>> pipeline = StripHTML() | NormalizeWhitespace()
            >>> result = pipeline.run("<div>  hello  </div>")
            >>> # Returns: "hello"
        """
        from .refiner import Refiner

        return Refiner().pipe(self).pipe(other)
