"""Example: Normalizing excessive whitespace."""

from prompt_refiner import Pipeline, NormalizeWhitespace

# Text with excessive whitespace (common in web scraping)
messy_text = """
    This    text    has


    way    too    much

    whitespace   and   line   breaks



    that    waste    tokens
"""

print("=" * 60)
print("WHITESPACE NORMALIZATION EXAMPLE")
print("=" * 60)
print(f"\nOriginal text:\n{repr(messy_text)}")

# Normalize whitespace
refiner = Pipeline().pipe(NormalizeWhitespace())
cleaned = refiner.run(messy_text)
print(f"\nNormalized text:\n{repr(cleaned)}")
print(f"\nVisual comparison:")
print(f"Before: {len(messy_text.split())} words, {len(messy_text)} characters")
print(f"After:  {len(cleaned.split())} words, {len(cleaned)} characters")
print(f"Saved:  {len(messy_text) - len(cleaned)} characters")
