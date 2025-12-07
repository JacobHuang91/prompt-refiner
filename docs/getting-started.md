# Getting Started

Get up and running with Prompt Refiner in minutes.

## Installation

=== "Default (Lightweight)"

    Zero dependencies - perfect for most use cases:

    ```bash
    pip install llm-prompt-refiner
    ```

=== "With Precise Token Counting"

    Install with optional `tiktoken` for precise token counting:

    ```bash
    pip install llm-prompt-refiner[token]
    ```

    Then opt-in by passing a `model` parameter:

    ```python
    from prompt_refiner import CountTokens, MessagesPacker

    counter = CountTokens(model="gpt-4")
    packer = MessagesPacker(max_tokens=1000, model="gpt-4")
    ```

## Your First Pipeline

Let's create a simple pipeline to clean HTML and normalize whitespace:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace

# Create a pipeline using the pipe operator
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
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

clean_output = pipeline.run(raw_input)
print(clean_output)
# Output: "Welcome This has excessive spaces."
```

## Understanding the Pipeline Pattern

Prompt Refiner uses a **pipeline pattern** where you chain operations together:

1. **Create operations** - Initialize the operations you need
2. **Chain with `|` operator** - Combine operations in order
3. **Run with `.run()`** - Execute the pipeline on your text

```python
pipeline = (
    Operation1()            # 1. Create operations
    | Operation2()          # 2. Chain with | operator
    | Operation3()
)

result = pipeline.run(text)  # 3. Run
```

!!! tip "Alternative: Fluent API"
    Prefer method chaining? Use the traditional fluent API with `Refiner().pipe()`:
    ```python
    from prompt_refiner import Refiner

    pipeline = (
        Refiner()
        .pipe(Operation1())
        .pipe(Operation2())
        .pipe(Operation3())
    )
    ```

!!! tip "Order Matters"
    Operations run in the order you add them. For example, you should typically clean HTML before normalizing whitespace.

## Common Patterns

### Pattern 1: Web Content Cleaning

Clean content scraped from the web:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace, FixUnicode

web_cleaner = (
    StripHTML(to_markdown=True)  # Convert to Markdown
    | FixUnicode()               # Fix Unicode issues
    | NormalizeWhitespace()      # Normalize spaces
)
```

### Pattern 2: RAG Context Optimization

Optimize retrieved context for RAG applications:

```python
from prompt_refiner import Deduplicate, TruncateTokens

rag_optimizer = (
    Deduplicate(similarity_threshold=0.85)  # Remove duplicates
    | TruncateTokens(max_tokens=2000)       # Fit in context window
)
```

### Pattern 3: Secure PII Handling

Redact sensitive information before sending to APIs:

```python
from prompt_refiner import RedactPII

secure_pipeline = RedactPII(redact_types={"email", "phone", "ssn"})
```

### Pattern 4: Full Optimization with Tracking

Complete optimization with metrics:

```python
from prompt_refiner import (
    StripHTML, NormalizeWhitespace,
    TruncateTokens, RedactPII, CountTokens
)

original_text = "Your text here..."
counter = CountTokens(original_text=original_text)

full_pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | TruncateTokens(max_tokens=1000)
    | RedactPII()
    | counter
)

result = full_pipeline.run(original_text)
print(counter.format_stats())
```

### Pattern 5: Advanced - RAG with Context Budget (v0.1.3+)

For RAG applications, manage context budgets with smart priority-based packing:

```python
from prompt_refiner import MessagesPacker, StripHTML, NormalizeWhitespace

packer = MessagesPacker(max_tokens=1000)

# System prompt (auto-prioritized: highest)
packer.add(
    "Answer based on provided context.",
    role="system"
)

# RAG documents with JIT cleaning (auto-prioritized: high)
packer.add(
    "<div>Document 1...</div>",
    role="context",
    refine_with=[StripHTML(), NormalizeWhitespace()]
)

# Current user query (auto-prioritized: critical)
packer.add(
    "What is the answer?",
    role="query"
)

messages = packer.pack()  # Ready for chat APIs
# response = client.chat.completions.create(messages=messages)
```

## Proven Results

Curious about the real-world effectiveness? Check out our comprehensive benchmark results:

!!! success "Benchmark Highlights"
    - **4-15% token reduction** across 30 test cases
    - **96-99% quality preservation** (cosine similarity + LLM judge)
    - **Real cost savings**: $48-$150/month per 1M tokens

[View Full Benchmark →](benchmark.md){ .md-button .md-button--primary }

## Exploring Modules

Prompt Refiner has 5 specialized modules:

- **[Cleaner](modules/cleaner.md)** - Clean dirty data (HTML, whitespace, Unicode, JSON)
- **[Compressor](modules/compressor.md)** - Reduce size (truncation, deduplication)
- **[Scrubber](modules/scrubber.md)** - Security and privacy (PII redaction)
- **[Packer](modules/packer.md)** - Context budget management for RAG and chatbots (v0.1.3+)
- **[Strategy](api-reference/strategy.md)** - Preset strategies for quick setup (v0.1.5+)
- **[Analyzer](modules/analyzer.md)** - Metrics and analysis (token counting)

## Next Steps

<div class="grid cards" markdown>

-   __Learn the Modules__

    ---

    Deep dive into each of the 5 core modules

    [:octicons-arrow-right-24: Modules Overview](modules/overview.md)

-   __Browse Examples__

    ---

    See practical examples for each operation

    [:octicons-arrow-right-24: Examples](examples/index.md)

-   __API Reference__

    ---

    Explore the complete API documentation

    [:octicons-arrow-right-24: API Reference](api-reference/index.md)

</div>
