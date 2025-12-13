"""
Example: Using Refiner Pipelines with MessagesPacker and TextPacker

This example demonstrates the new cleaner syntax for using Refiner pipelines
with packers instead of passing lists of operations.

Before v0.1.9:
    packer = MessagesPacker(
        context=(docs, [StripHTML(), NormalizeWhitespace()])
    )

After v0.1.9:
    cleaner = StripHTML() | NormalizeWhitespace()
    packer = MessagesPacker(
        context=(docs, cleaner)
    )

Benefits:
- Cleaner, more readable syntax
- Reusable pipelines across multiple parameters
- Easier to compose complex transformations
"""

from prompt_refiner import MessagesPacker, NormalizeWhitespace, StripHTML, TextPacker, TextFormat


def main():
    print("=" * 60)
    print("Refiner Pipeline Example")
    print("=" * 60)

    # Create a reusable cleaning pipeline
    print("\n1. Creating reusable cleaning pipeline:")
    cleaner = StripHTML() | NormalizeWhitespace()
    print(f"   cleaner = StripHTML() | NormalizeWhitespace()")
    print(f"   Type: {type(cleaner).__name__}")

    # Sample dirty data
    dirty_context = [
        "<div>  The   Quick   Brown   Fox  </div>",
        "<p>  Jumps   Over   The   Lazy   Dog  </p>",
    ]
    dirty_query = "<strong>  What   does   the   fox   say?  </strong>"

    print("\n2. Using pipeline with MessagesPacker:")
    messages_packer = MessagesPacker(
        model="gpt-4o-mini",
        system="You are a helpful assistant.",
        context=(dirty_context, cleaner),  # Reuse cleaner
        query=(dirty_query, cleaner),  # Reuse cleaner again
    )
    messages = messages_packer.pack()

    print("\n   Packed messages:")
    for i, msg in enumerate(messages, 1):
        print(f"   {i}. [{msg['role']}] {msg['content']}")

    print("\n3. Using pipeline with TextPacker:")
    text_packer = TextPacker(
        model="gpt-4o-mini",
        text_format=TextFormat.MARKDOWN,
        system="You are a helpful assistant.",
        context=(dirty_context, cleaner),  # Reuse cleaner
        query=(dirty_query, cleaner),  # Reuse cleaner again
    )
    text = text_packer.pack()

    print("\n   Packed text:")
    print("   " + "\n   ".join(text.split("\n")))

    print("\n4. Comparing old vs new syntax:")
    print("\n   Old syntax (still works):")
    print("   packer = MessagesPacker(")
    print("       context=(docs, [StripHTML(), NormalizeWhitespace()])")
    print("   )")

    print("\n   New syntax (cleaner):")
    print("   cleaner = StripHTML() | NormalizeWhitespace()")
    print("   packer = MessagesPacker(")
    print("       context=(docs, cleaner)")
    print("   )")

    print("\n5. Creating multiple specialized pipelines:")
    html_cleaner = StripHTML()
    aggressive_cleaner = StripHTML() | NormalizeWhitespace()

    mixed_packer = MessagesPacker(
        system=("<div>System prompt</div>", html_cleaner),
        query=("Query   with   spaces", aggressive_cleaner),
    )
    mixed_messages = mixed_packer.pack()

    print("\n   Using different pipelines for different parameters:")
    for msg in mixed_messages:
        print(f"   [{msg['role']}] {msg['content']}")

    print("\n" + "=" * 60)
    print("Summary:")
    print("- Refiner pipelines can be reused across parameters")
    print("- Cleaner syntax than lists of operations")
    print("- Both syntaxes work (backward compatible)")
    print("=" * 60)


if __name__ == "__main__":
    main()
