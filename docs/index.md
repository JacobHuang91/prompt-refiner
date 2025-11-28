# Prompt Refiner

A lightweight Python library for optimizing and cleaning LLM inputs. Reduce token usage, improve prompt quality, and lower API costs.

## Overview

Prompt Refiner helps you clean and optimize prompts before sending them to LLM APIs. By removing unnecessary whitespace, duplicate characters, and other inefficiencies, you can:

- **Reduce token usage and API costs** - Remove unnecessary characters and content
- **Improve prompt quality** - Clean HTML, fix Unicode issues, normalize whitespace
- **Enhance security** - Redact PII automatically before sending to APIs
- **Track optimization value** - Measure token savings and cost reductions

!!! success "Proven Effectiveness"
    Benchmarked on 30 real-world test cases, Prompt Refiner achieves **4-15% token reduction** while maintaining 96-99% quality. Aggressive optimization can save up to **~$54/month** on GPT-4 at scale (1M tokens/month).

    Processing overhead is **< 0.5ms per 1k tokens** - negligible compared to network and LLM latency.

    [See benchmark results →](benchmark.md)

## Status

!!! info "Early Development"
    This project is in early development. Features are being added iteratively.

## Quick Start

Build custom cleaning pipelines with the pipe operator:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace, TruncateTokens

# Define a cleaning pipeline
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | TruncateTokens(max_tokens=1000, strategy="middle_out")
)

raw_input = "<div>  User input with <b>lots</b> of   spaces... </div>"
clean_prompt = pipeline.run(raw_input)
# Output: "User input with lots of spaces..."
```

!!! tip "Alternative: Fluent API"
    Prefer method chaining? Use `Refiner().pipe()`:
    ```python
    from prompt_refiner import Refiner

    pipeline = Refiner().pipe(StripHTML()).pipe(NormalizeWhitespace())
    ```

## 4 Core Modules

Prompt Refiner is organized into 4 specialized modules:

### 1. Cleaner - Clean Dirty Data
- **StripHTML()** - Remove HTML tags, convert to Markdown
- **NormalizeWhitespace()** - Collapse excessive whitespace
- **FixUnicode()** - Remove zero-width spaces and problematic Unicode

[Learn more about Cleaner →](modules/cleaner.md){ .md-button }

### 2. Compressor - Reduce Size
- **TruncateTokens()** - Smart truncation with sentence boundaries
    - Strategies: `"head"`, `"tail"`, `"middle_out"`
- **Deduplicate()** - Remove similar content (great for RAG)

[Learn more about Compressor →](modules/compressor.md){ .md-button }

### 3. Scrubber - Security & Privacy
- **RedactPII()** - Automatically redact emails, phones, IPs, credit cards, URLs, SSNs

[Learn more about Scrubber →](modules/scrubber.md){ .md-button }

### 4. Analyzer - Show Value
- **CountTokens()** - Track token savings and optimization impact

[Learn more about Analyzer →](modules/analyzer.md){ .md-button }

## Complete Example

```python
from prompt_refiner import (
    # Cleaner
    StripHTML, NormalizeWhitespace, FixUnicode,
    # Compressor
    Deduplicate, TruncateTokens,
    # Scrubber
    RedactPII,
    # Analyzer
    CountTokens
)

original_text = """Your messy input here..."""

counter = CountTokens(original_text=original_text)

pipeline = (
    # Clean
    StripHTML(to_markdown=True)
    | NormalizeWhitespace()
    | FixUnicode()
    # Compress
    | Deduplicate(similarity_threshold=0.85)
    | TruncateTokens(max_tokens=500, strategy="head")
    # Secure
    | RedactPII(redact_types={"email", "phone"})
    # Analyze
    | counter
)

result = pipeline.run(original_text)
print(counter.format_stats())  # Shows token savings
```

## Next Steps

<div class="grid cards" markdown>

-   __Get Started__

    ---

    Install Prompt Refiner and build your first pipeline in minutes

    [:octicons-arrow-right-24: Getting Started](getting-started.md)

-   __API Reference__

    ---

    Complete API documentation for all operations and modules

    [:octicons-arrow-right-24: API Reference](api-reference/index.md)

-   __Examples__

    ---

    Browse practical examples for each module

    [:octicons-arrow-right-24: Examples](examples/index.md)

-   __Contributing__

    ---

    Learn how to contribute to the project

    [:octicons-arrow-right-24: Contributing Guide](contributing.md)

</div>
