"""Example: Cleaning HTML from web-scraped content."""

from prompt_groomer import Groomer, NormalizeWhitespace, StripHTML

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
groomer = Groomer().pipe(StripHTML()).pipe(NormalizeWhitespace())
cleaned = groomer.run(html_content)
print(f"\nCleaned (HTML removed):\n{cleaned}")

# Example 2: Convert HTML to Markdown
groomer_md = Groomer().pipe(StripHTML(to_markdown=True)).pipe(NormalizeWhitespace())
markdown = groomer_md.run(html_content)
print(f"\nConverted to Markdown:\n{markdown}")

# Example 3: Preserve semantic tags
groomer_preserve = Groomer().pipe(StripHTML(preserve_tags={"p"}))
preserved = groomer_preserve.run(html_content)
print(f"\nWith <p> tags preserved:\n{preserved}")
