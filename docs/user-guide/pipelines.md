# Pipeline Basics

Learn how to build effective pipelines with Prompt Groomer.

## The Pipeline Pattern

A pipeline chains operations in sequence:

```python
from prompt_groomer import Groomer

pipeline = (
    Groomer()
    .pipe(Operation1())
    .pipe(Operation2())
    .pipe(Operation3())
)

result = pipeline.run(input_text)
```

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
# Clean HTML first, then normalize
Groomer().pipe(StripHTML()).pipe(NormalizeWhitespace())

# Wrong order - normalizes first, HTML remains
Groomer().pipe(NormalizeWhitespace()).pipe(StripHTML())
```

## Best Practices

### 1. Clean Before Compressing

```python
Groomer()
    .pipe(StripHTML())           # Clean first
    .pipe(NormalizeWhitespace())
    .pipe(TruncateTokens())      # Then compress
```

### 2. Compress Before Redacting

```python
Groomer()
    .pipe(TruncateTokens())  # Compress first
    .pipe(RedactPII())       # Then redact
```

### 3. Analyze Last

```python
counter = CountTokens(original_text=text)
Groomer()
    .pipe(StripHTML())
    .pipe(TruncateTokens())
    .pipe(counter)  # Analyze at the end
```

## Multiple Pipelines

Create different pipelines for different use cases:

```python
# Pipeline for web content
web_pipeline = (
    Groomer()
    .pipe(StripHTML(to_markdown=True))
    .pipe(FixUnicode())
    .pipe(NormalizeWhitespace())
)

# Pipeline for RAG
rag_pipeline = (
    Groomer()
    .pipe(Deduplicate())
    .pipe(TruncateTokens(max_tokens=2000))
)

# Pipeline for secure processing
secure_pipeline = (
    Groomer()
    .pipe(RedactPII())
)
```

[Learn about custom operations →](custom-operations.md){ .md-button }
