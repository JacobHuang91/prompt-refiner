# API Reference

Complete API reference for all Prompt Groomer classes and operations.

This section contains auto-generated documentation from the codebase docstrings. All operations inherit from the base `Operation` class and implement a `process(text: str) -> str` method.

## Quick Navigation

<div class="grid cards" markdown>

-   :material-pipe:{ .lg .middle } __Groomer__

    ---

    Pipeline builder for chaining operations

    [:octicons-arrow-right-24: Groomer API](groomer.md)

-   :material-broom:{ .lg .middle } __Cleaner__

    ---

    Operations for cleaning dirty data

    [:octicons-arrow-right-24: Cleaner API](cleaner.md)

-   :material-compress:{ .lg .middle } __Compressor__

    ---

    Operations for reducing size

    [:octicons-arrow-right-24: Compressor API](compressor.md)

-   :material-shield-lock:{ .lg .middle } __Scrubber__

    ---

    Operations for security and privacy

    [:octicons-arrow-right-24: Scrubber API](scrubber.md)

-   :material-chart-line:{ .lg .middle } __Analyzer__

    ---

    Operations for metrics and analysis

    [:octicons-arrow-right-24: Analyzer API](analyzer.md)

</div>

## Operation Base Class

All operations in Prompt Groomer inherit from the `Operation` base class:

```python
from abc import ABC, abstractmethod

class Operation(ABC):
    @abstractmethod
    def process(self, text: str) -> str:
        """Process the input text and return the result."""
        pass
```

## Usage Pattern

Operations are used within a `Groomer` pipeline:

```python
from prompt_groomer import Groomer, StripHTML, NormalizeWhitespace

groomer = (
    Groomer()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
)

result = groomer.run("Your text here...")
```

## Module Organization

- **[Groomer](groomer.md)** - Core pipeline builder class
- **[Cleaner](cleaner.md)** - `StripHTML`, `NormalizeWhitespace`, `FixUnicode`
- **[Compressor](compressor.md)** - `TruncateTokens`, `Deduplicate`
- **[Scrubber](scrubber.md)** - `RedactPII`
- **[Analyzer](analyzer.md)** - `CountTokens`
