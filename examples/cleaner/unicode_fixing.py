"""Example: Fixing problematic Unicode characters."""

from prompt_groomer import FixUnicode, Groomer

# Text with problematic Unicode characters
text_with_issues = (
    "Hello\u200bWorld\u200c"  # Zero-width space and non-joiner
    "\ufeff"  # BOM
    "This\u2060is\u200dtext"  # Word joiner and zero-width joiner
)

print("=" * 60)
print("UNICODE FIXING EXAMPLE")
print("=" * 60)
print(f"\nOriginal (with invisible characters):\n{repr(text_with_issues)}")
print(f"Visual appearance: {text_with_issues}")

# Clean unicode
groomer = Groomer().pipe(FixUnicode())
cleaned = groomer.run(text_with_issues)
print(f"\nCleaned:\n{repr(cleaned)}")
print(f"Visual appearance: {cleaned}")
