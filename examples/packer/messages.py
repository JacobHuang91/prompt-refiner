"""
MessagesPacker Demo - Chat Completion APIs

Shows how to use MessagesPacker to manage chat context and call OpenAI API.
Demonstrates token optimization through HTML cleaning and priority-based packing.
"""

from dotenv import load_dotenv
from openai import OpenAI

from prompt_refiner import MessagesPacker, NormalizeWhitespace, StripHTML

# Load environment variables from .env file
load_dotenv()


def main():
    # RAG documents with messy HTML and excessive whitespace (common in web scraping)
    doc_html = """
    <div class="doc">
        <h2>MessagesPacker   Documentation</h2>
        <p>MessagesPacker   is   optimized   for   chat   completion   APIs.
        It   automatically   accounts   for   ChatML   format   overhead
        (~4   tokens   per   message).</p>

        <script>trackEvent('pageview');</script>
        <style>.header { color: blue; }</style>
        <div class="ads"><!-- Advertisement --></div>
    </div>
    """

    # Initialize packer with automatic token savings tracking
    packer = MessagesPacker(model="gpt-4o", track_savings=True)

    # Add system prompt
    packer.add(
        "You are a helpful AI assistant. Answer questions based on the provided documentation.",
        role="system",
    )

    # Add RAG documents with automatic cleaning pipeline
    packer.add(doc_html, role="context", refine_with=[StripHTML(), NormalizeWhitespace()])
    packer.add(
        "The library includes MessagesPacker for chat APIs and TextPacker for completion APIs.",
        role="context",
    )

    # Add conversation history
    history = [
        {"role": "user", "content": "What is prompt-refiner?"},
        {"role": "assistant", "content": "Prompt-refiner is a Python library for optimizing LLM inputs."},
        {"role": "user", "content": "Does it support token counting?"},
        {"role": "assistant", "content": "Yes, it has precise token counting with tiktoken."},
    ]
    packer.add_messages(history)

    # Add current query
    packer.add("How does MessagesPacker handle conversation history?", role="query")

    # Pack messages with priority-based selection
    messages = packer.pack()

    # Get automatic token savings
    savings = packer.get_token_savings()

    if savings:
        print("Token Optimization (automatic tracking):")
        print(f"  Before: {savings['original_tokens']} tokens")
        print(f"  After:  {savings['refined_tokens']} tokens")
        print(f"  Saved:  {savings['saved_tokens']} tokens ({savings['saving_percent']})")
        print()

    print(f"Context Management:")
    print(f"  Packed {len(messages)}/{len(packer.get_items())} messages")
    print()

    # Call OpenAI API
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    print("Response:")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
