# HTML Cleaning Example

Clean HTML content from web scraping or user input.

## Scenario

You've scraped content from a website and need to clean it before sending to an LLM API.

## Example Code

```python
from prompt_refiner import StripHTML, NormalizeWhitespace

html_content = """
<div class="article">
    <h1>Understanding <strong>LLMs</strong></h1>
    <p>Large Language Models are powerful <em>AI systems</em>.</p>
</div>
"""

# Remove all HTML and normalize whitespace
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
)

cleaned = pipeline.run(html_content)
print(cleaned)
# Output: "Understanding LLMs Large Language Models are powerful AI systems."
```

## Converting to Markdown

```python
# Convert HTML to Markdown instead of removing
pipeline = (
    StripHTML(to_markdown=True)
    | NormalizeWhitespace()
)

markdown = pipeline.run(html_content)
print(markdown)
# Output:
# # Understanding **LLMs**
#
# Large Language Models are powerful *AI systems*.
```

## Full Example

See the complete example: [`examples/cleaner/html_cleaning.py`](https://github.com/JacobHuang91/prompt-refiner/blob/main/examples/cleaner/html_cleaning.py)

```bash
python examples/cleaner/html_cleaning.py
```

## Related

- [StripHTML API Reference](../api-reference/cleaner.md#striphtml)
- [Cleaner Module Guide](../modules/cleaner.md)
