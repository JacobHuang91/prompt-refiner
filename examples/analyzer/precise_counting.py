"""
Example: Precise Token Counting with Optional Tiktoken

Demonstrates the optional tiktoken dependency for precise token counting.

Installation:
- Default (lightweight): pip install llm-prompt-refiner
- Precise mode: pip install llm-prompt-refiner[token]

Usage:
- Default (estimation): CountTokens() or CountTokens(model=None)
- Precise mode: CountTokens(model="gpt-4")
"""

from prompt_refiner import ContextPacker, CountTokens, PRIORITY_HIGH, PRIORITY_SYSTEM

print("=" * 70)
print("Token Counting Modes")
print("=" * 70)

# Example 1: CountTokens - Default estimation mode
print("\n1. CountTokens - Default Estimation Mode")
print("-" * 70)

counter_default = CountTokens()
print(f"Precise mode enabled: {counter_default.is_precise}")
print(f"Using tiktoken: {'Yes ✓' if counter_default.is_precise else 'No (estimation mode)'}")

text = "The quick brown fox jumps over the lazy dog"
counter_default.process(text)
stats = counter_default.get_stats()
print(f"\nText: '{text}'")
print(f"Token count: {stats['tokens']}")
print(f"Mode: {'Precise (tiktoken)' if counter_default.is_precise else 'Estimation (chars/4)'}")

# Example 2: CountTokens - Opt-in to precise mode
print("\n\n2. CountTokens - Opt-in to Precise Mode")
print("-" * 70)

counter_precise = CountTokens(model="gpt-4")
print(f"Precise mode enabled: {counter_precise.is_precise}")
print(f"Using tiktoken: {'Yes ✓' if counter_precise.is_precise else 'No (estimation mode)'}")

counter_precise.process(text)
stats_precise = counter_precise.get_stats()
print(f"\nText: '{text}'")
print(f"Token count: {stats_precise['tokens']}")
print(f"Mode: {'Precise (tiktoken)' if counter_precise.is_precise else 'Estimation (chars/4)'}")

# Example 3: ContextPacker - Default estimation mode
print("\n\n3. ContextPacker - Default Estimation Mode")
print("-" * 70)
print("Creating ContextPacker with max_tokens=100 (no model specified)...")
print()

packer_default = ContextPacker(max_tokens=100)

print(f"\nPacker settings:")
print(f"  Raw max tokens: {packer_default.raw_max_tokens}")
print(f"  Effective max tokens: {packer_default.effective_max_tokens}")
print(f"  Safety buffer: {packer_default.raw_max_tokens - packer_default.effective_max_tokens} tokens")

# Example 4: ContextPacker - Opt-in to precise mode
print("\n\n4. ContextPacker - Opt-in to Precise Mode")
print("-" * 70)
print("Creating ContextPacker with max_tokens=100, model='gpt-4'...")
print()

packer_precise = ContextPacker(max_tokens=100, model="gpt-4")

print(f"\nPacker settings:")
print(f"  Raw max tokens: {packer_precise.raw_max_tokens}")
print(f"  Effective max tokens: {packer_precise.effective_max_tokens}")
print(f"  Safety buffer: {packer_precise.raw_max_tokens - packer_precise.effective_max_tokens} tokens")

# Example 5: Comparison between modes
print("\n\n5. Estimation vs Precise Mode Comparison")
print("-" * 70)

texts = [
    "Hello world!",
    "This is a longer sentence with more words.",
    "UTF-8: 你好世界 (Chinese characters)",
    "Code: def hello(): return 'world'",
]

print(f"\n{'Text':<50} {'Tokens':>10}")
print("-" * 62)

for text in texts:
    counter = CountTokens()  # Default estimation mode
    counter.process(text)
    stats = counter.get_stats()
    print(f"{text[:47]+'...' if len(text) > 50 else text:<50} {stats['tokens']:>10}")

# Example 6: Why the safety buffer matters
print("\n\n6. Why the 10% Safety Buffer Matters")
print("-" * 70)
print("""
In estimation mode (without tiktoken), token counting uses the approximation:
  1 token ≈ 4 characters

However, this can be inaccurate for:
- Non-English text (Chinese, Arabic, etc.)
- Special characters and emojis
- Code with lots of punctuation
- Numbers and dates

The 10% safety buffer (90% effective capacity) helps prevent context overflow
by being conservative with the budget.

Example:
  max_tokens=1000 (requested)
  → effective_max_tokens=900 (actual limit in estimation mode)
  → 100 token buffer to account for estimation errors

When you install tiktoken, the buffer is removed:
  max_tokens=1000 (requested)
  → effective_max_tokens=1000 (actual limit in precise mode)
  → 0 token buffer (no estimation error)
""")

# Example 7: How to enable precise mode
print("\n7. How to Enable Precise Mode")
print("-" * 70)
print("""
Step 1: Install tiktoken
    pip install llm-prompt-refiner[token]

Step 2: Pass a model name to opt-in
    counter = CountTokens(model="gpt-4")
    packer = ContextPacker(max_tokens=1000, model="gpt-4")

Benefits of precise mode:
✓ Accurate token counts (no approximation)
✓ Full token budget utilization (no 10% safety buffer)
✓ Better handling of non-English text
✓ More predictable context management

When to use estimation mode (default):
✓ Lightweight deployments (zero dependencies)
✓ Performance-critical applications
✓ Development/testing environments
✓ When approximate counts are sufficient
✓ Simply don't pass a model parameter (or pass model=None)
""")

print("=" * 70)
print("Example complete!")
print("=" * 70)
