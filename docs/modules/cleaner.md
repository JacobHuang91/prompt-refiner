# Cleaner Module

The Cleaner module provides operations for cleaning dirty data from various sources.

## Overview

When working with real-world text data, you often encounter:

- HTML tags from web scraping
- Excessive whitespace and formatting issues
- Problematic Unicode characters

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

## Next Steps

- [View Examples](../examples/html-cleaning.md)
- [Full API Reference](../api-reference/cleaner.md)
- [Explore Other Modules](overview.md)
