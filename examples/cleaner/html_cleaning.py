"""Example: Cleaning HTML from web-scraped content."""

from prompt_refiner import Pipeline, NormalizeWhitespace, StripHTML

# Raw HTML from a web scrape
html_content = """
<div class="article" style="margin: 20px;">
    <h1>Understanding   <strong>LLMs</strong></h1>
    <p>Large   Language   Models   are   powerful   <em>AI systems</em>.</p>
    <p>They   can   process   <span style="color: blue">natural language</span>.</p>
</div>
"""

print("=" * 60)
print("HTML CLEANING EXAMPLE")
print("=" * 60)
print(f"\nOriginal HTML:\n{html_content}")

# Example 1: Simple HTML stripping
refiner = Pipeline().pipe(StripHTML()).pipe(NormalizeWhitespace())
cleaned = refiner.run(html_content)
print(f"\nCleaned (HTML removed):\n{cleaned}")

# Example 2: Convert HTML to Markdown
refiner_md = Pipeline().pipe(StripHTML(to_markdown=True)).pipe(NormalizeWhitespace())
markdown = refiner_md.run(html_content)
print(f"\nConverted to Markdown:\n{markdown}")

# Example 3: Preserve semantic tags
refiner_preserve = Pipeline().pipe(StripHTML(preserve_tags={"p"}))
preserved = refiner_preserve.run(html_content)
print(f"\nWith <p> tags preserved:\n{preserved}")
