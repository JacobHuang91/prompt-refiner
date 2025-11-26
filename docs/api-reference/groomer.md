# Groomer Class

The `Groomer` class is the core pipeline builder that allows you to chain multiple operations together.

::: prompt_groomer.groomer.Groomer
    options:
      show_source: true
      members_order: source
      heading_level: 2

## Usage Example

```python
from prompt_groomer import Groomer, StripHTML, NormalizeWhitespace

# Create and configure a pipeline
groomer = (
    Groomer()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
)

# Execute the pipeline
result = groomer.run("<p>Hello   World!</p>")
print(result)  # "Hello World!"
```

## Method Chaining

The `Groomer` class supports method chaining, allowing you to build readable pipelines:

```python
groomer = (
    Groomer()
    .pipe(Operation1())
    .pipe(Operation2())
    .pipe(Operation3())
)
```

This is equivalent to:

```python
groomer = Groomer()
groomer.pipe(Operation1())
groomer.pipe(Operation2())
groomer.pipe(Operation3())
```

## Pipeline Execution

When you call `run(text)`, the Groomer:

1. Takes the input text
2. Passes it through each operation in sequence
3. Each operation's output becomes the next operation's input
4. Returns the final processed text

```python
# Pipeline: text → Operation1 → Operation2 → Operation3 → result
result = groomer.run(text)
```
