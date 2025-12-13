"""
OpenAI Agents + Prompt Refiner

Demonstrates using TextPacker and ResponseCompressor to optimize:
1. Input messages (TextPacker with StripHTML)
2. Tool responses (ResponseCompressor)

Run: python examples/agents/openai_agents.py
"""

import asyncio

from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

from prompt_refiner import ResponseCompressor, StripHTML, TextFormat, TextPacker
from shared_data import CONTEXT_DOCUMENTS, MESSAGE_HISTORY, QUERY, SYSTEM_PROMPT, search_books

load_dotenv()


@function_tool
def search_books_tool(query: str) -> dict:
    """Search for books by query.

    Args:
        query: Search query

    Returns:
        Book search results
    """
    import json

    # Execute search
    tool_response = search_books(query)
    original_size = len(json.dumps(tool_response))

    # Compress response to reduce tokens
    compressor = ResponseCompressor()
    compressed_response = compressor.process(tool_response)
    compressed_size = len(json.dumps(compressed_response))

    # Log compression
    saved = original_size - compressed_size
    percent = (saved / original_size * 100) if original_size > 0 else 0
    print(f"\n✓ Tool response compressed: {original_size} → {compressed_size} chars ({percent:.1f}% reduction)\n")

    return compressed_response


async def main():
    """Run the OpenAI agents example with context and history."""
    print("OpenAI Agents + Prompt Refiner (Optimized)")
    print("=" * 80)
    print()

    # Use TextPacker to build structured, optimized input message (using shared data)
    input_message = TextPacker.quick_pack(
        text_format=TextFormat.MARKDOWN,
        system="Context (use this when answering):",
        context=(
            CONTEXT_DOCUMENTS,  # Shared context documents with HTML
            [StripHTML()]  # Clean HTML from context docs
        ),
        history=MESSAGE_HISTORY,  # Shared message history
        query=QUERY  # Shared query
    )

    print("✓ Input optimized with TextPacker (MARKDOWN format + StripHTML)")
    print()

    # Create agent (using shared system prompt)
    agent = Agent(
        name="Book Recommender",
        instructions=SYSTEM_PROMPT,
        tools=[search_books_tool],
    )

    print("Running agent...")
    result = await Runner.run(agent, input=input_message)

    print("Final Response:")
    print("-" * 80)
    print(result.final_output)
    print()
    print("=" * 80)
    print()
    print("Optimizations Applied:")
    print("  ✅ TextPacker: Structured MARKDOWN format")
    print("  ✅ StripHTML: Removed HTML tags from context")
    print("  ✅ ResponseCompressor: Removed debug fields from tool response")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
