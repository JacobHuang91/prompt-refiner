# Pipeline Basics

Learn how to build effective pipelines with Prompt Refiner.

## Two Ways to Build Pipelines

Prompt Refiner supports two syntax options for building pipelines:

### Pipe Operator (Recommended)

The pipe operator (`|`) provides a clean, Pythonic syntax similar to LangChain:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace, TruncateTokens

pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | TruncateTokens(max_tokens=1000)
)

result = pipeline.run(input_text)
```

**Why use this:**
- More concise - no need to import or instantiate `Refiner()`
- Familiar to LangChain, LangGraph, and modern Python framework users
- Cleaner visual appearance

### Fluent API

The fluent API uses method chaining with `.pipe()`:

```python
from prompt_refiner import Refiner, StripHTML, NormalizeWhitespace, TruncateTokens

pipeline = (
    Refiner()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(TruncateTokens(max_tokens=1000))
)

result = pipeline.run(input_text)
```

**Why use this:**
- More explicit - clear that you're creating a Refiner pipeline
- Traditional method chaining pattern

!!! tip "Choose One Style"
    Pick one syntax style per project and use it consistently. Both work identically under the hood. Don't mix styles in the same pipeline.

## The Pipeline Pattern

A pipeline chains operations in sequence:

```python
input → Operation1 → Operation2 → Operation3 → output
```

All operations process the text in order, with each operation's output becoming the next operation's input.

## How Pipelines Work

1. Text enters the pipeline
2. Each operation processes it in order
3. Output of one operation becomes input of the next
4. Final result is returned

```
input → Operation1 → Operation2 → Operation3 → output
```

## Order Matters

Operations run in the order you add them:

```python
# ✅ Correct: Clean HTML first, then normalize
pipeline = StripHTML() | NormalizeWhitespace()

# ❌ Wrong order - normalizes first, HTML remains
pipeline = NormalizeWhitespace() | StripHTML()
```

## Best Practices

### 1. Clean Before Compressing

```python
pipeline = (
    StripHTML()                  # Clean first
    | NormalizeWhitespace()
    | TruncateTokens()           # Then compress
)
```

### 2. Compress Before Redacting

```python
pipeline = (
    TruncateTokens()  # Compress first
    | RedactPII()     # Then redact
)
```

### 3. Analyze Last

```python
counter = CountTokens(original_text=text)
pipeline = (
    StripHTML()
    | TruncateTokens()
    | counter  # Analyze at the end
)
```

## Multiple Pipelines

Create different pipelines for different use cases:

```python
# Pipeline for web content
web_pipeline = (
    StripHTML(to_markdown=True)
    | FixUnicode()
    | NormalizeWhitespace()
)

# Pipeline for RAG
rag_pipeline = (
    Deduplicate()
    | TruncateTokens(max_tokens=2000)
)

# Pipeline for secure processing
secure_pipeline = RedactPII()

# Use them
cleaned_web = web_pipeline.run(html_content)
optimized_rag = rag_pipeline.run(rag_context)
safe_text = secure_pipeline.run(user_input)
```

[Learn about custom operations →](custom-operations.md){ .md-button }
