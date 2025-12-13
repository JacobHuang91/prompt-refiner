"""Pipeline class for building prompt processing pipelines."""

from typing import List, Optional, Union

from .refiner import Refiner


class Pipeline(Refiner):
    """
    A pipeline builder for composing multiple refiners.

    Pipeline is itself a Refiner, so it can be composed with other Refiners
    or Pipelines using the pipe operator (|).
    """

    def __init__(self, refiners: Optional[Union[Refiner, List[Refiner]]] = None):
        """
        Initialize a pipeline.

        Args:
            refiners: Optional refiner(s) to initialize the pipeline with.
                Can be a single Refiner or a list of Refiners.
                If None, creates an empty pipeline.

        Example:
            >>> # Empty pipeline
            >>> pipeline = Pipeline()

            >>> # Single refiner
            >>> pipeline = Pipeline(StripHTML())

            >>> # Multiple refiners
            >>> pipeline = Pipeline([StripHTML(), NormalizeWhitespace()])
        """
        self._refiners: List[Refiner] = []

        if refiners is not None:
            if isinstance(refiners, list):
                self._refiners = refiners.copy()
            else:
                # Single refiner
                self._refiners = [refiners]

    def process(self, text: str) -> str:
        """
        Process text through the pipeline (Refiner interface).

        This method makes Pipeline compatible with the Refiner interface,
        allowing Pipelines to be used anywhere a Refiner is expected.

        Args:
            text: The input text to process

        Returns:
            The processed text after all refiners
        """
        return self.run(text)

    def pipe(self, refiner: Refiner) -> "Pipeline":
        """
        Add a refiner to the pipeline.

        Returns a new Pipeline instance with the refiner added, leaving the
        original unchanged (immutable).

        Args:
            refiner: The refiner to add

        Returns:
            A new Pipeline instance with the refiner added

        Example:
            >>> base = Pipeline().pipe(StripHTML())
            >>> pipeline1 = base.pipe(NormalizeWhitespace())
            >>> pipeline2 = base.pipe(TruncateTokens(100))
            >>> # base still has 1 refiner, pipeline1 and pipeline2 each have 2
        """
        new_pipeline = Pipeline()
        new_pipeline._refiners = self._refiners.copy()
        new_pipeline._refiners.append(refiner)
        return new_pipeline

    def run(self, text: str) -> str:
        """
        Execute the pipeline on the input text.

        Args:
            text: The input text to process

        Returns:
            The processed text after all refiners
        """
        result = text
        for refiner in self._refiners:
            result = refiner.process(result)
        return result

    def __or__(self, other: Refiner) -> "Pipeline":
        """
        Support pipe operator syntax for adding refiners to the pipeline.

        Returns a new Pipeline instance, leaving the original unchanged (immutable).
        Enables continued chaining: (refiner1 | refiner2) | refiner3

        Args:
            other: The refiner to add to the pipeline

        Returns:
            A new Pipeline instance with the refiner added

        Example:
            >>> from prompt_refiner import StripHTML, NormalizeWhitespace, TruncateTokens
            >>> base = StripHTML() | NormalizeWhitespace()
            >>> pipeline1 = base | TruncateTokens(max_tokens=100)
            >>> pipeline2 = base | TruncateTokens(max_tokens=200)
            >>> # base has 2 refiners, pipeline1 and pipeline2 each have 3 different refiners
        """
        return self.pipe(other)
