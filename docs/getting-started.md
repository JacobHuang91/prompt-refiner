# Getting Started

Get up and running with Prompt Groomer in minutes.

## Installation

=== "Using uv (recommended)"

    ```bash
    uv pip install prompt-groomer
    ```

=== "Using pip"

    ```bash
    pip install prompt-groomer
    ```

## Your First Pipeline

Let's create a simple pipeline to clean HTML and normalize whitespace:

```python
from prompt_groomer import Groomer, StripHTML, NormalizeWhitespace

# Create a pipeline
groomer = (
    Groomer()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
)

# Process some text
raw_input = """
<html>
    <body>
        <h1>Welcome</h1>
        <p>This  has    excessive   spaces.</p>
    </body>
</html>
"""

clean_output = groomer.run(raw_input)
print(clean_output)
# Output: "Welcome This has excessive spaces."
```

## Understanding the Pipeline Pattern

Prompt Groomer uses a **pipeline pattern** where you chain operations together:

1. **Create a Groomer** - Initialize an empty pipeline
2. **Add operations with `.pipe()`** - Chain operations in order
3. **Run with `.run()`** - Execute the pipeline on your text

```python
groomer = (
    Groomer()               # 1. Create
    .pipe(Operation1())     # 2. Add operations
    .pipe(Operation2())
    .pipe(Operation3())
)

result = groomer.run(text)  # 3. Run
```

!!! tip "Order Matters"
    Operations run in the order you add them. For example, you should typically clean HTML before normalizing whitespace.

## Common Patterns

### Pattern 1: Web Content Cleaning

Clean content scraped from the web:

```python
from prompt_groomer import Groomer, StripHTML, NormalizeWhitespace, FixUnicode

web_cleaner = (
    Groomer()
    .pipe(StripHTML(to_markdown=True))  # Convert to Markdown
    .pipe(FixUnicode())                 # Fix Unicode issues
    .pipe(NormalizeWhitespace())        # Normalize spaces
)
```

### Pattern 2: RAG Context Optimization

Optimize retrieved context for RAG applications:

```python
from prompt_groomer import Groomer, Deduplicate, TruncateTokens

rag_optimizer = (
    Groomer()
    .pipe(Deduplicate(similarity_threshold=0.85))  # Remove duplicates
    .pipe(TruncateTokens(max_tokens=2000))        # Fit in context window
)
```

### Pattern 3: Secure PII Handling

Redact sensitive information before sending to APIs:

```python
from prompt_groomer import Groomer, RedactPII

secure_groomer = (
    Groomer()
    .pipe(RedactPII(redact_types={"email", "phone", "ssn"}))
)
```

### Pattern 4: Full Optimization with Tracking

Complete optimization with metrics:

```python
from prompt_groomer import (
    Groomer, StripHTML, NormalizeWhitespace,
    TruncateTokens, RedactPII, CountTokens
)

original_text = "Your text here..."
counter = CountTokens(original_text=original_text)

full_pipeline = (
    Groomer()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(TruncateTokens(max_tokens=1000))
    .pipe(RedactPII())
    .pipe(counter)
)

result = full_pipeline.run(original_text)
print(counter.format_stats())
```

## Exploring Modules

Prompt Groomer has 4 specialized modules:

- **[Cleaner](modules/cleaner.md)** - Clean dirty data (HTML, whitespace, Unicode)
- **[Compressor](modules/compressor.md)** - Reduce size (truncation, deduplication)
- **[Scrubber](modules/scrubber.md)** - Security and privacy (PII redaction)
- **[Analyzer](modules/analyzer.md)** - Metrics and analysis (token counting)

## Next Steps

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } __Learn the Modules__

    ---

    Deep dive into each of the 4 core modules

    [:octicons-arrow-right-24: Modules Overview](modules/overview.md)

-   :material-code-braces:{ .lg .middle } __Browse Examples__

    ---

    See practical examples for each operation

    [:octicons-arrow-right-24: Examples](examples/index.md)

-   :material-file-document:{ .lg .middle } __API Reference__

    ---

    Explore the complete API documentation

    [:octicons-arrow-right-24: API Reference](api-reference/index.md)

</div>
