# Prompt Groomer

A lightweight Python library for optimizing and cleaning LLM inputs. Reduce token usage, improve prompt quality, and lower API costs.

## Overview

Prompt Groomer helps you clean and optimize prompts before sending them to LLM APIs. By removing unnecessary whitespace, duplicate characters, and other inefficiencies, you can:

- Reduce token usage and API costs
- Improve prompt quality and consistency
- Process inputs more efficiently

## Status

This project is in early development. Features are being added iteratively.

## Installation

```bash
# Using uv (recommended)
uv pip install prompt-groomer

# Using pip
pip install prompt-groomer
```

## Quick Start

Build custom cleaning pipelines with a fluent API:

```python
from prompt_groomer import Groomer, StripHTML, NormalizeWhitespace, TruncateTokens

# Define a cleaning pipeline
groomer = (
    Groomer()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(TruncateTokens(max_tokens=1000, strategy="middle_out"))
)

raw_input = "<div>  User input with <b>lots</b> of   spaces... </div>"
clean_prompt = groomer.run(raw_input)
# Output: "User input with lots of spaces..."
```

## 4 Core Modules

Prompt Groomer is organized into 4 specialized modules:

### 1. **Cleaner** - Clean Dirty Data
- `StripHTML()` - Remove HTML tags, convert to Markdown
- `NormalizeWhitespace()` - Collapse excessive whitespace
- `FixUnicode()` - Remove zero-width spaces and problematic Unicode

### 2. **Compressor** - Reduce Size
- `TruncateTokens()` - Smart truncation with sentence boundaries
  - Strategies: `"head"`, `"tail"`, `"middle_out"`
- `Deduplicate()` - Remove similar content (great for RAG)

### 3. **Scrubber** - Security & Privacy
- `RedactPII()` - Automatically redact emails, phones, IPs, credit cards, URLs, SSNs

### 4. **Analyzer** - Show Value
- `CountTokens()` - Track token savings and optimization impact

## Complete Example

```python
from prompt_groomer import (
    Groomer,
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

groomer = (
    Groomer()
    # Clean
    .pipe(StripHTML(to_markdown=True))
    .pipe(NormalizeWhitespace())
    .pipe(FixUnicode())
    # Compress
    .pipe(Deduplicate(similarity_threshold=0.85))
    .pipe(TruncateTokens(max_tokens=500, strategy="head"))
    # Secure
    .pipe(RedactPII(redact_types={"email", "phone"}))
    # Analyze
    .pipe(counter)
)

result = groomer.run(original_text)
print(counter.format_stats())  # Shows token savings
```

## Examples

Check out the [`examples/`](examples/) folder for detailed examples organized by module:
- `cleaner/` - HTML cleaning, whitespace normalization, Unicode fixing
- `compressor/` - Smart truncation, deduplication
- `scrubber/` - PII redaction
- `analyzer/` - Token counting and cost savings
- `all_modules_demo.py` - Complete demonstration

## Development

This project uses `uv` for dependency management and `make` for common tasks.

```bash
# Install dependencies
make install

# Run tests
make test

# Format code
make format
```

## License

MIT