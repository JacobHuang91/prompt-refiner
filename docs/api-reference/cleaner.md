# Cleaner Module

The Cleaner module provides operations for cleaning dirty data, including HTML removal, whitespace normalization, and Unicode fixing.

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
