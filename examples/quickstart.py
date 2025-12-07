"""
Quickstart - Complete Production RAG Workflow

Demonstrates:
- MessagesPacker for context budget management
- SchemaCompressor for tool definitions
- ResponseCompressor for tool API responses

Run: python examples/quickstart.py
"""

import json

import requests
from dotenv import load_dotenv
from openai import OpenAI, pydantic_function_tool
from pydantic import BaseModel, Field

from prompt_refiner import MessagesPacker, ResponseCompressor, SchemaCompressor, StripHTML

# Load environment variables
load_dotenv()


def search_books(query: str) -> dict:
    """Search Google Books API for books.

    Args:
        query: Search query to find books
    """
    resp = requests.get(
        "https://www.googleapis.com/books/v1/volumes",
        params={"q": query, "maxResults": 30},
        timeout=30,
    )
    return resp.json()


def main():
    """Run the complete quickstart example."""
    print("=" * 80)
    print("Prompt Refiner - Quickstart Example")
    print("=" * 80)
    print()

    # 1. Pack messages with token budget (track savings from JIT cleaning)
    packer = MessagesPacker(max_tokens=1000, model="gpt-4o-mini", track_savings=True)
    packer.add("You are a helpful AI assistant that helps users find books.", role="system")
    packer.add("Search for books about Python programming.", role="query")

    # Add multiple RAG documents with HTML/whitespace to demonstrate cleaning
    packer.add(
        "<div><h1>Installation    Guide</h1><p>To   install   prompt-refiner, use pip install llm-prompt-refiner.</p></div>",
        role="context",
        refine_with=[StripHTML()],
    )
    packer.add(
        "<div><h2>Features</h2><p>Our    library    provides    token    optimization    and    context    management.</p></div>",
        role="context",
        refine_with=[StripHTML()],
    )
    packer.add(
        "<section><h2>Documentation</h2><p>Visit   our   GitHub   for   complete   documentation   and   examples.</p></section>",
        role="context",
        refine_with=[StripHTML()],
    )

    messages = packer.pack()

    savings_info = packer.get_token_savings()
    original = savings_info["original_tokens"]
    refined = savings_info["refined_tokens"]
    saved = savings_info["saved_tokens"]
    percent = (saved / original * 100) if original > 0 else 0
    print(f"✓ MessagesPacker: {original} → {refined} tokens ({percent:.1f}% saved)")
    print()

    # 2. Generate and compress tool schema from function
    class SearchBooksInput(BaseModel):
        query: str = Field(description="Search query to find books")

    tool_schema = pydantic_function_tool(SearchBooksInput, name="search_books")
    compressed_schema = SchemaCompressor().process(tool_schema)

    # Measure real token usage with OpenAI API
    client = OpenAI()

    # Call with original schema
    response_original = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, tools=[tool_schema]
    )
    original_tokens = response_original.usage.prompt_tokens

    # Call with compressed schema
    response_compressed = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, tools=[compressed_schema]
    )
    compressed_tokens = response_compressed.usage.prompt_tokens

    savings = (1 - compressed_tokens / original_tokens) * 100
    print(f"✓ SchemaCompressor: {original_tokens} → {compressed_tokens} tokens ({savings:.1f}% saved)")
    print()

    # 3. Execute the tool call
    tool_call = response_compressed.choices[0].message.tool_calls[0]
    tool_args = json.loads(tool_call.function.arguments)
    tool_response = search_books(**tool_args)
    print(f"✓ Tool executed: {tool_call.function.name}(query='{tool_args['query']}')")
    print()

    # 4. Compress tool response and measure with OpenAI API
    compressed_response = ResponseCompressor().process(tool_response)

    # Build tool call messages
    tool_call_messages = [
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
            ],
        }
    ]

    # Measure with original response
    response_with_original = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages + tool_call_messages + [
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(tool_response)}
        ],
        max_tokens=50,
    )
    original_tokens = response_with_original.usage.prompt_tokens

    # Measure with compressed response
    response_with_compressed = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages + tool_call_messages + [
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(compressed_response)}
        ],
        max_tokens=50,
    )
    compressed_tokens = response_with_compressed.usage.prompt_tokens

    savings = (1 - compressed_tokens / original_tokens) * 100
    print(f"✓ ResponseCompressor: {original_tokens} → {compressed_tokens} tokens ({savings:.1f}% saved)")
    print()

    # 5. Verify compressed response works with final answer
    final_answer = response_with_compressed.choices[0].message.content
    print(f"✓ LLM Response: {final_answer[:80]}...")
    print()

    print("=" * 80)
    print("✓ Complete workflow: Schema + Tool Execution + Response Compression")
    print("=" * 80)


if __name__ == "__main__":
    main()
