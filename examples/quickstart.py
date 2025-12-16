"""
Quickstart - Complete Production RAG Workflow

Demonstrates MessagesPacker, SchemaCompressor, and ResponseCompressor.

Run: python examples/quickstart.py
"""

import json

import requests
from dotenv import load_dotenv
from openai import OpenAI, pydantic_function_tool
from pydantic import BaseModel, Field

from prompt_refiner import (
    MessagesPacker,
    NormalizeWhitespace,
    ResponseCompressor,
    SchemaCompressor,
    StripHTML,
)

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
    print("Prompt Refiner - Quickstart")
    print("=" * 80)
    print()

    # 1. Pack messages (track savings from automatic refinement)
    #
    # Default refining strategies:
    # - system/query: MinimalStrategy (StripHTML + NormalizeWhitespace)
    # - context/history: StandardStrategy (StripHTML + NormalizeWhitespace + Deduplicate)
    #
    # You can override with custom pipelines:
    # - Use tuple: (content, refiner_or_pipeline)
    # - Example: context=(["<div>Doc</div>"], StripHTML() | NormalizeWhitespace())

    packer = MessagesPacker(
        # system uses default MinimalStrategy (StripHTML + NormalizeWhitespace)
        system="<p>You are a helpful AI assistant    that    helps users find books.</p>",
        # context with explicit pipeline (overrides default StandardStrategy)
        context=(
            [
                "<div><h1>Installation    Guide</h1><p>To   install   prompt-refiner, use pip install llm-prompt-refiner.</p></div>",
                "<div><h2>Features</h2><p>Our    library    provides    token    optimization    and    context    management.</p></div>",
                "<section><h2>Documentation</h2><p>Visit   our   GitHub   for   complete   documentation   and   examples.</p></section>",
            ],
            StripHTML() | NormalizeWhitespace()  # Pipeline: chain multiple operations
        ),
        # query uses default MinimalStrategy
        query="<span>Search    for    books about Python programming.</span>"
    )

    messages = packer.pack()

    print(f"✓ MessagesPacker: Messages packed successfully")
    print()

    # 2. Generate and compress tool schema from function
    class SearchBooksInput(BaseModel):
        query: str = Field(description="Search query to find books")

    tool_schema = pydantic_function_tool(SearchBooksInput, name="search_books")
    compressed_schema = SchemaCompressor().process(tool_schema)

    client = OpenAI()

    # Call with compressed schema
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, tools=[compressed_schema]
    )

    print(f"✓ SchemaCompressor applied")
    print()

    # 3. Execute the tool call
    tool_call = response.choices[0].message.tool_calls[0]
    tool_args = json.loads(tool_call.function.arguments)
    tool_response = search_books(**tool_args)

    # 4. Compress tool response
    compressed_response = ResponseCompressor().process(tool_response)

    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(compressed_response)
    })

    print(f"✓ ResponseCompressor applied")
    print()

    # 5. Get final response
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=100,
    )

    print("Final Response:")
    print("-" * 80)
    print(final_response.choices[0].message.content)
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
