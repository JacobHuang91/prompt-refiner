"""Example: Counting tokens and showing optimization value."""

from prompt_groomer import (
    CountTokens,
    FixUnicode,
    Groomer,
    NormalizeWhitespace,
    StripHTML,
    TruncateTokens,
)

# Original messy text
original_text = """
<div class="content" style="padding: 20px;">
    <h1>Welcome   to   Our   Service</h1>
    <p>This   is   a   long   document   with   lots   of   HTML   tags.</p>
    <p>It   also   has   excessive   whitespace   and   could   be   optimized.</p>
    <p>We   want   to   show   how   much   we   can   save   by   cleaning   it   up.</p>
    <p>Every   token   counts   when   using   LLM   APIs!</p>
    <p>Let's   see   the   impact   of   our   optimization   pipeline.</p>
</div>
"""

print("=" * 60)
print("TOKEN COUNTING & OPTIMIZATION VALUE")
print("=" * 60)
print(f"\nOriginal text:\n{original_text}")

# Create counter with original text for comparison
counter = CountTokens(original_text=original_text)

# Build optimization pipeline
groomer = (
    Groomer()
    .pipe(StripHTML())  # Remove HTML tags
    .pipe(NormalizeWhitespace())  # Fix whitespace
    .pipe(FixUnicode())  # Clean unicode
    .pipe(counter)  # Count tokens (should be last)
)

# Process text
cleaned = groomer.run(original_text)

print(f"\nCleaned text:\n{cleaned}")
print("\n" + "=" * 60)
print("TOKEN STATISTICS")
print("=" * 60)
print(counter.format_stats())

# Example 2: With truncation for even more savings
print("\n\n" + "=" * 60)
print("WITH TRUNCATION")
print("=" * 60)

counter2 = CountTokens(original_text=original_text)
groomer_truncate = (
    Groomer()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(TruncateTokens(max_tokens=20, strategy="head"))
    .pipe(counter2)
)

truncated = groomer_truncate.run(original_text)
print(f"\nTruncated text:\n{truncated}")
print("\n" + "=" * 60)
print("TOKEN STATISTICS")
print("=" * 60)
print(counter2.format_stats())

# Calculate cost savings (example: $0.01 per 1000 tokens)
original_cost = counter2.get_stats()["original"] * 0.01 / 1000
cleaned_cost = counter2.get_stats()["cleaned"] * 0.01 / 1000
print(f"\n💰 Cost savings (at $0.01/1k tokens):")
print(f"   Original cost: ${original_cost:.6f}")
print(f"   Optimized cost: ${cleaned_cost:.6f}")
print(f"   Savings: ${(original_cost - cleaned_cost):.6f}")
