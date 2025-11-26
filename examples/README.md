# Prompt Groomer Examples

This directory contains examples demonstrating the 4 core modules of Prompt Groomer.

## Quick Start

Run the all-in-one demo:
```bash
python examples/all_modules_demo.py
```

## Module Examples

### 1. Cleaner Module

Clean and normalize dirty text data.

#### `cleaner/html_cleaning.py`
Demonstrates HTML tag removal and conversion to Markdown.
```bash
python examples/cleaner/html_cleaning.py
```

**What it shows:**
- Basic HTML stripping
- HTML to Markdown conversion
- Preserving semantic tags

#### `cleaner/whitespace_normalization.py`
Shows how to normalize excessive whitespace from web scraping.
```bash
python examples/cleaner/whitespace_normalization.py
```

**What it shows:**
- Collapsing multiple spaces
- Removing extra newlines
- Character count reduction

#### `cleaner/unicode_fixing.py`
Fixes problematic Unicode characters that can cause issues.
```bash
python examples/cleaner/unicode_fixing.py
```

**What it shows:**
- Zero-width space removal
- Control character cleanup
- Unicode normalization

---

### 2. Compressor Module

Reduce token count intelligently.

#### `compressor/smart_truncation.py`
Demonstrates intelligent text truncation with sentence boundaries.
```bash
python examples/compressor/smart_truncation.py
```

**What it shows:**
- Head strategy (keep beginning)
- Tail strategy (keep end - for conversation history)
- Middle-out strategy (keep both ends)
- Sentence boundary respect

#### `compressor/deduplication.py`
Shows how to remove duplicate content (essential for RAG).
```bash
python examples/compressor/deduplication.py
```

**What it shows:**
- Jaccard similarity for fast deduplication
- Levenshtein distance for accurate matching
- Sentence vs paragraph granularity
- RAG context optimization

---

### 3. Scrubber Module

Protect sensitive information.

#### `scrubber/pii_redaction.py`
Demonstrates automatic PII detection and redaction.
```bash
python examples/scrubber/pii_redaction.py
```

**What it shows:**
- Email, phone, IP, credit card redaction
- Selective PII type filtering
- Custom patterns and keywords
- Enterprise data protection

---

### 4. Analyzer Module

Measure and demonstrate optimization value.

#### `analyzer/token_counting.py`
Shows token counting and cost savings calculation.
```bash
python examples/analyzer/token_counting.py
```

**What it shows:**
- Token count comparison
- Optimization statistics
- Cost savings calculation
- Before/after analysis

---

## Custom Operations

### `custom_operation.py`
Learn how to create your own custom operations by extending the base `Operation` class.
```bash
python examples/custom_operation.py
```

**What it shows:**
- Creating custom operations
- Extending the Operation base class
- Using custom operations in pipelines
- Example: RemoveEmojis operation

---

## Complete Pipeline Demo

### `all_modules_demo.py`
Comprehensive demonstration of all 4 modules working together.
```bash
python examples/all_modules_demo.py
```

**What it shows:**
- Each module in isolation
- Complete pipeline combining all modules
- Real-world use cases
- Performance metrics

---

## Running Examples

All examples can be run from the project root:

```bash
# Run all module examples
python examples/cleaner/html_cleaning.py
python examples/compressor/smart_truncation.py
python examples/scrubber/pii_redaction.py
python examples/analyzer/token_counting.py

# Run complete demo
python examples/all_modules_demo.py
```

---

## Example Use Cases

### Web Scraping Pipeline
```python
from prompt_groomer import Groomer, StripHTML, NormalizeWhitespace, FixUnicode

groomer = (
    Groomer()
    .pipe(StripHTML(to_markdown=True))
    .pipe(NormalizeWhitespace())
    .pipe(FixUnicode())
)
```

### RAG Context Optimization
```python
from prompt_groomer import Groomer, Deduplicate, TruncateTokens

groomer = (
    Groomer()
    .pipe(Deduplicate(similarity_threshold=0.85))
    .pipe(TruncateTokens(max_tokens=500, strategy="head"))
)
```

### Enterprise Data Protection
```python
from prompt_groomer import Groomer, RedactPII, CountTokens

counter = CountTokens(original_text=original)
groomer = (
    Groomer()
    .pipe(RedactPII())
    .pipe(counter)
)
```

---

## Tips

1. **Order matters**: Run Cleaner operations first, then Compressor, then Scrubber, with Analyzer last
2. **Test with real data**: These examples use simplified data - test with your actual use case
3. **Tune parameters**: Adjust thresholds and strategies based on your specific needs
4. **Monitor savings**: Use CountTokens to track actual token reduction
5. **Combine strategically**: Not every operation is needed for every use case

---

## Learn More

- See `MODULES.md` for detailed API documentation
- See `README.md` for installation and quickstart
- See `tests/` for more usage patterns
