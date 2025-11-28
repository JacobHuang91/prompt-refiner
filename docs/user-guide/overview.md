# User Guide Overview

Learn how to use Prompt Refiner effectively to optimize your LLM inputs.

## What is Prompt Refiner?

Prompt Refiner is a library for cleaning and optimizing text before sending it to LLM APIs. It helps you:

- **Save money** by reducing token usage
- **Improve quality** by cleaning and normalizing text
- **Enhance security** by redacting PII
- **Track value** by measuring optimization impact

## Core Concepts

### Operations

An **Operation** is a single transformation that processes text:

```python
from prompt_refiner import StripHTML

operation = StripHTML()
result = operation.process("<p>Hello</p>")
# Output: "Hello"
```

All operations implement the same interface: `process(text: str) -> str`

### Pipelines

A **Pipeline** chains multiple operations together:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace

# Using the pipe operator (recommended)
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
)

result = pipeline.run("<p>Hello    World</p>")
# Output: "Hello World"
```

Alternatively, use the fluent API:
```python
from prompt_refiner import Refiner

pipeline = Refiner().pipe(StripHTML()).pipe(NormalizeWhitespace())
```

### The 4 Modules

- **[Cleaner](../modules/cleaner.md)** - Clean dirty data
- **[Compressor](../modules/compressor.md)** - Reduce size
- **[Scrubber](../modules/scrubber.md)** - Security & privacy
- **[Analyzer](../modules/analyzer.md)** - Track metrics

## Next Steps

- [Learn about pipelines](pipelines.md)
- [Create custom operations](custom-operations.md)
- [Browse examples](../examples/index.md)
