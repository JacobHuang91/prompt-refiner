"""Demo script showing all 4 core modules of Prompt Refiner."""

from prompt_refiner import (
    CountTokens,
    Deduplicate,
    FixUnicode,
    Refiner,
    NormalizeWhitespace,
    RedactPII,
    StripHTML,
    TruncateTokens,
)


def demo_cleaner_module():
    """Demo the Cleaner module - for cleaning dirty data."""
    print("\n" + "=" * 60)
    print("1. CLEANER MODULE - Cleaning Dirty Data")
    print("=" * 60)

    # Sample dirty text with HTML, bad whitespace, and unicode issues
    dirty_text = """
    <div style="color: red">
        <h1>Welcome   to  <strong>Prompt Refiner</strong>!</h1>
        <p>This    is    a   paragraph    with   excessive    spaces.</p>
        <p>Here's some zero-width space:\u200bHidden\u200bSpaces</p>
    </div>
    """

    print(f"\nOriginal text:\n{repr(dirty_text)}")

    # Clean it up
    refiner = (
        Refiner().pipe(StripHTML(to_markdown=True)).pipe(NormalizeWhitespace()).pipe(FixUnicode())
    )

    cleaned = refiner.run(dirty_text)
    print(f"\nCleaned text:\n{cleaned}")


def demo_compressor_module():
    """Demo the Compressor module - for reducing prompt size."""
    print("\n" + "=" * 60)
    print("2. COMPRESSOR MODULE - Reducing Prompt Size")
    print("=" * 60)

    # Long text with repetition
    long_text = """
    The quick brown fox jumps over the lazy dog. This is the first sentence.
    The quick brown fox jumps over the lazy dog. This is similar content.
    Python is a great programming language. It is widely used.
    The quick brown fox jumps over the lazy dog. This is almost identical.
    Machine learning is revolutionizing the world. AI is everywhere now.
    Python is an amazing programming language. It's very popular.
    """

    print(f"\nOriginal text:\n{long_text}")

    # Deduplicate
    dedup_refiner = Refiner().pipe(Deduplicate(similarity_threshold=0.7))
    deduped = dedup_refiner.run(long_text)
    print(f"\nAfter deduplication:\n{deduped}")

    # Truncate with smart sentence boundaries
    truncate_refiner = Refiner().pipe(TruncateTokens(max_tokens=20, strategy="head"))
    truncated = truncate_refiner.run(long_text)
    print(f"\nAfter truncation (20 tokens, head strategy):\n{truncated}")


def demo_scrubber_module():
    """Demo the Scrubber module - for security and privacy."""
    print("\n" + "=" * 60)
    print("3. SCRUBBER MODULE - Security and Privacy")
    print("=" * 60)

    # Text with PII
    sensitive_text = """
    Please contact John at john.doe@example.com or call him at 555-123-4567.
    His IP address is 192.168.1.1 and his credit card is 4532-1234-5678-9010.
    You can also visit https://example.com/profile for more info.
    """

    print(f"\nOriginal text:\n{sensitive_text}")

    # Redact PII
    refiner = Refiner().pipe(RedactPII())
    redacted = refiner.run(sensitive_text)
    print(f"\nAfter PII redaction:\n{redacted}")

    # Redact only specific types
    refiner_selective = Refiner().pipe(RedactPII(redact_types={"email", "phone"}))
    redacted_selective = refiner_selective.run(sensitive_text)
    print(f"\nAfter selective PII redaction (only email/phone):\n{redacted_selective}")


def demo_analyzer_module():
    """Demo the Analyzer module - for showing value."""
    print("\n" + "=" * 60)
    print("4. ANALYZER MODULE - Showing Value")
    print("=" * 60)

    original_text = """
    <div>
        <p>This   is   a   long    document    with   lots   of   HTML  tags.</p>
        <p>It   also   has   excessive   whitespace   and   could   be   optimized.</p>
        <p>Let's   see   how   much   we   can   save   by   cleaning   it   up.</p>
    </div>
    """

    print(f"\nOriginal text:\n{original_text}")

    # Create counter with original text
    counter = CountTokens(original_text=original_text)

    # Clean and count
    refiner = (
        Refiner()
        .pipe(StripHTML())
        .pipe(NormalizeWhitespace())
        .pipe(counter)  # Counter as the last step
    )

    cleaned = refiner.run(original_text)
    print(f"\nCleaned text:\n{cleaned}")

    # Show statistics
    print(f"\n{counter.format_stats()}")


def demo_full_pipeline():
    """Demo a complete pipeline using all modules."""
    print("\n" + "=" * 60)
    print("5. FULL PIPELINE - All Modules Combined")
    print("=" * 60)

    original_text = """
    <div>
        <h1>Customer   Support   Ticket   #12345</h1>
        <p>Customer: John Doe</p>
        <p>Email: john.doe@example.com</p>
        <p>Phone: 555-123-4567</p>
        <p>Issue: The   product   is   not   working   properly.   The   product   is   not   working   properly.</p>
        <p>The   customer   is   very   frustrated.   Please   help   resolve   this   issue   immediately.</p>
        <p>IP   Address:   192.168.1.100</p>
    </div>
    """

    print(f"\nOriginal text:\n{original_text}")

    counter = CountTokens(original_text=original_text)

    # Complete pipeline
    refiner = (
        Refiner()
        .pipe(StripHTML(to_markdown=True))  # Cleaner
        .pipe(NormalizeWhitespace())  # Cleaner
        .pipe(FixUnicode())  # Cleaner
        .pipe(Deduplicate(similarity_threshold=0.9))  # Compressor
        .pipe(RedactPII(redact_types={"email", "phone", "ip"}))  # Scrubber
        .pipe(TruncateTokens(max_tokens=50, strategy="head"))  # Compressor
        .pipe(counter)  # Analyzer
    )

    result = refiner.run(original_text)

    print(f"\nFinal result:\n{result}")
    print(f"\n{counter.format_stats()}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PROMPT REFINER - 4 CORE MODULES DEMONSTRATION")
    print("=" * 60)

    demo_cleaner_module()
    demo_compressor_module()
    demo_scrubber_module()
    demo_analyzer_module()
    demo_full_pipeline()

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60 + "\n")
