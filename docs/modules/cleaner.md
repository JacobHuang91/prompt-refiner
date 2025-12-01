# Cleaner Module

The Cleaner module provides operations for cleaning dirty data from various sources.

## Overview

When working with real-world text data, you often encounter:

- HTML tags from web scraping
- Excessive whitespace and formatting issues
- Problematic Unicode characters
- JSON with null values and empty containers

The Cleaner module addresses these issues efficiently.

## Operations

### StripHTML

Remove HTML tags or convert them to Markdown.

**Use cases:**

- Web scraping
- Email content processing
- User-generated HTML content

**Example:**

```python
from prompt_refiner import StripHTML

# Remove all HTML
cleaner = StripHTML()
result = cleaner.run("<p>Hello <b>World</b>!</p>")
# Output: "Hello World!"

# Convert to Markdown
cleaner = StripHTML(to_markdown=True)
result = cleaner.run("<p>Hello <b>World</b>!</p>")
# Output: "Hello **World**!\n\n"
```

[Full API Reference →](../api-reference/cleaner.md#striphtml){ .md-button }

### NormalizeWhitespace

Collapse excessive whitespace, tabs, and newlines.

**Use cases:**

- Text from PDFs
- User input normalization
- Copy-pasted content

**Example:**

```python
from prompt_refiner import NormalizeWhitespace

cleaner = NormalizeWhitespace()
result = cleaner.run("Hello    World  \t\n  Foo")
# Output: "Hello World Foo"
```

[Full API Reference →](../api-reference/cleaner.md#normalizewhitespace){ .md-button }

### FixUnicode

Remove problematic Unicode characters.

**Use cases:**

- Zero-width spaces from copy-paste
- Control characters
- Invisible characters causing issues

**Example:**

```python
from prompt_refiner import FixUnicode

cleaner = FixUnicode()
result = cleaner.run("Hello\u200bWorld")
# Output: "HelloWorld"
```

[Full API Reference →](../api-reference/cleaner.md#fixunicode){ .md-button }

### JsonCleaner

Clean and minify JSON by removing null values and empty containers.

**Use cases:**

- RAG API responses with null/empty fields
- Compressing JSON context before LLM input
- Normalizing inconsistent API data
- Token optimization for JSON-heavy prompts

**Example:**

```python
from prompt_refiner import JsonCleaner

# Strip nulls and empty containers
cleaner = JsonCleaner(strip_nulls=True, strip_empty=True)
dirty_json = """
{
    "name": "Alice",
    "age": null,
    "address": {},
    "tags": []
}
"""
result = cleaner.run(dirty_json)
# Output: {"name":"Alice"}

# Only minify (keep all data)
cleaner = JsonCleaner(strip_nulls=False, strip_empty=False)
result = cleaner.run(dirty_json)
# Output: {"name":"Alice","age":null,"address":{},"tags":[]}
```

**Token savings:** 50-60% reduction in typical RAG API responses!

[Full API Reference →](../api-reference/cleaner.md#jsoncleaner){ .md-button }

## Common Patterns

### Web Content Pipeline

```python
from prompt_refiner import StripHTML, FixUnicode, NormalizeWhitespace

web_cleaner = (
    StripHTML(to_markdown=True)
    | FixUnicode()
    | NormalizeWhitespace()
)
```

### Text Normalization

```python
from prompt_refiner import FixUnicode, NormalizeWhitespace

normalizer = (
    FixUnicode()
    | NormalizeWhitespace()
)
```

### RAG Context Compression

```python
from prompt_refiner import JsonCleaner, TruncateTokens

rag_compressor = (
    JsonCleaner(strip_nulls=True, strip_empty=True)
    | TruncateTokens(max_tokens=500, strategy="head")
)
```

## Next Steps

- [View Examples](../examples/html-cleaning.md)
- [Full API Reference](../api-reference/cleaner.md)
- [Explore Other Modules](overview.md)
