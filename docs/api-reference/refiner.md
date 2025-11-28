# Refiner Class

The `Refiner` class is the core pipeline builder that allows you to chain multiple operations together.

::: prompt_refiner.refiner.Refiner
    options:
      show_source: true
      members_order: source
      heading_level: 2

## Usage Examples

### Pipe Operator (Recommended)

```python
from prompt_refiner import StripHTML, NormalizeWhitespace

# Create a pipeline using the pipe operator
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
)

# Execute the pipeline
result = pipeline.run("<p>Hello   World!</p>")
print(result)  # "Hello World!"
```

### Fluent API with .pipe()

The `Refiner` class supports method chaining with `.pipe()`:

```python
from prompt_refiner import Refiner, StripHTML, NormalizeWhitespace

# Create a pipeline using the fluent API
pipeline = (
    Refiner()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
)

# Execute the pipeline
result = pipeline.run("<p>Hello   World!</p>")
print(result)  # "Hello World!"
```

Both approaches work identically - choose the one that fits your style.

## Pipeline Execution

When you call `run(text)`, the Refiner:

1. Takes the input text
2. Passes it through each operation in sequence
3. Each operation's output becomes the next operation's input
4. Returns the final processed text

```python
# Pipeline: text → Operation1 → Operation2 → Operation3 → result
result = refiner.run(text)
```
