# Cleaner Module

The Cleaner module provides operations for cleaning dirty data, including HTML removal, whitespace normalization, Unicode fixing, and JSON compression.

## StripHTML

Remove HTML tags from text, with options to preserve semantic tags or convert to Markdown.

::: prompt_refiner.cleaner.StripHTML
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Examples

```python
from prompt_refiner import StripHTML

# Basic HTML stripping
stripper = StripHTML()
result = stripper.process("<p>Hello <b>World</b>!</p>")
# Output: "Hello World!"

# Convert to Markdown
stripper = StripHTML(to_markdown=True)
result = stripper.process("<p>Hello <b>World</b>!</p>")
# Output: "Hello **World**!\n\n"

# Preserve specific tags
stripper = StripHTML(preserve_tags={"p", "div"})
result = stripper.process("<div>Keep <b>Remove</b></div>")
# Output: "<div>Keep Remove</div>"
```

---

## NormalizeWhitespace

Collapse excessive whitespace, tabs, and newlines into single spaces.

::: prompt_refiner.cleaner.NormalizeWhitespace
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Examples

```python
from prompt_refiner import NormalizeWhitespace

normalizer = NormalizeWhitespace()
result = normalizer.process("Hello    World  \t\n  Foo")
# Output: "Hello World Foo"
```

---

## FixUnicode

Remove problematic Unicode characters including zero-width spaces and control characters.

::: prompt_refiner.cleaner.FixUnicode
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Examples

```python
from prompt_refiner import FixUnicode

# Remove zero-width spaces and control chars
fixer = FixUnicode()
result = fixer.process("Hello\u200bWorld\u0000")
# Output: "HelloWorld"

# Only remove zero-width spaces
fixer = FixUnicode(remove_control_chars=False)
result = fixer.process("Hello\u200bWorld")
# Output: "HelloWorld"
```

---

## JsonCleaner

Clean and minify JSON by removing null values and empty containers.

::: prompt_refiner.cleaner.JsonCleaner
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Examples

```python
from prompt_refiner import JsonCleaner

# Strip nulls and empty containers
cleaner = JsonCleaner(strip_nulls=True, strip_empty=True)
dirty_json = """
{
    "name": "Alice",
    "age": null,
    "address": {},
    "tags": [],
    "bio": ""
}
"""
result = cleaner.process(dirty_json)
# Output: {"name":"Alice"}

# Only strip nulls, keep empties
cleaner = JsonCleaner(strip_nulls=True, strip_empty=False)
result = cleaner.process(dirty_json)
# Output: {"name":"Alice","address":{},"tags":[],"bio":""}

# Only minify (no cleaning)
cleaner = JsonCleaner(strip_nulls=False, strip_empty=False)
result = cleaner.process(dirty_json)
# Output: {"name":"Alice","age":null,"address":{},"tags":[],"bio":""}

# Works with dict/list inputs too
cleaner = JsonCleaner(strip_nulls=True, strip_empty=True)
data = {"name": "Bob", "tags": [], "age": None}
result = cleaner.process(data)
# Output: {"name":"Bob"}
```

## Common Use Cases

### Web Scraping

```python
from prompt_refiner import Refiner, StripHTML, NormalizeWhitespace, FixUnicode

web_cleaner = (
    Refiner()
    .pipe(StripHTML(to_markdown=True))
    .pipe(FixUnicode())
    .pipe(NormalizeWhitespace())
)
```

### Text Normalization

```python
from prompt_refiner import Refiner, NormalizeWhitespace, FixUnicode

text_normalizer = (
    Refiner()
    .pipe(FixUnicode())
    .pipe(NormalizeWhitespace())
)
```

### RAG JSON Compression

```python
from prompt_refiner import Refiner, JsonCleaner, TruncateTokens

rag_compressor = (
    Refiner()
    .pipe(JsonCleaner(strip_nulls=True, strip_empty=True))
    .pipe(TruncateTokens(max_tokens=500, strategy="head"))
)
```
