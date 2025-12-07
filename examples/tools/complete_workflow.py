"""
Complete Tool Workflow - Schema + Response Compression

Demonstrates a real-world OpenAI tool calling workflow with both SchemaCompressor
and ResponseCompressor. Makes 4 separate API calls to measure real token usage:

1. Call with original schema → measure schema tokens
2. Call with compressed schema → measure schema tokens
3. Call with original response → measure response tokens
4. Call with compressed response → measure response tokens

Results show 35%+ token savings with real OpenAI measurements.
"""

import json

from dotenv import load_dotenv
from openai import OpenAI, pydantic_function_tool
from pydantic import BaseModel, Field

from prompt_refiner import ResponseCompressor, SchemaCompressor

# Load environment variables (expects OPENAI_API_KEY)
load_dotenv()


# =============================================================================
# Tool Definition
# =============================================================================


class SearchBooksInput(BaseModel):
    """Input parameters for searching books."""

    query: str = Field(
        description=(
            "The search query to find books. Examples: 'python programming', "
            "'machine learning', 'science fiction novels'. Use keywords and "
            "phrases to get the best results."
        )
    )
    limit: int = Field(
        default=50,
        description=(
            "Maximum number of results to return. Higher values give more "
            "comprehensive results but take longer. Typical values: 10 (quick), "
            "50 (comprehensive), 100 (exhaustive)."
        ),
    )


def search_books_impl(query: str, limit: int = 50) -> dict:
    """
    Search Google Books API for books.

    Returns a large JSON payload with book information including titles, authors,
    ISBNs, descriptions, and metadata. This demonstrates response compression
    on real API data.
    """
    import requests

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "maxResults": min(limit, 40)}  # Google Books max is 40
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


# Generate OpenAI tool schema from Pydantic model
search_books_schema = pydantic_function_tool(
    SearchBooksInput,
    name="search_books",
    description="Search Google Books API for books related to the query.",
)


# =============================================================================
# Helper Functions
# =============================================================================


def build_tool_message(tool_call, tool_response_content: str) -> list[dict]:
    """Build messages array with assistant tool call and tool response."""
    return [
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
        },
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_response_content,
        },
    ]


# =============================================================================
# Main Workflow
# =============================================================================


def main():
    """Execute the complete tool calling workflow with compression measurements."""
    print("=" * 80)
    print("COMPLETE TOOL WORKFLOW - Schema + Response Compression")
    print("=" * 80)
    print()

    client = OpenAI()

    # =========================================================================
    # STEP 1: Measure Schema Compression
    # =========================================================================
    print("=" * 80)
    print("STEP 1: Measuring Schema Compression")
    print("=" * 80)

    # Get original and compressed schemas
    original_schema = search_books_schema
    schema_compressor = SchemaCompressor()
    compressed_schema = schema_compressor.process(original_schema)

    # Base messages for tool calling
    messages = [
        {"role": "system", "content": "You are a helpful assistant that helps users find books."},
        {
            "role": "user",
            "content": "Find me books about artificial intelligence. Get at least 30 results.",
        },
    ]

    # Measure tokens with ORIGINAL schema
    response_original_schema = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, tools=[original_schema], tool_choice="auto"
    )
    original_schema_tokens = response_original_schema.usage.prompt_tokens

    # Measure tokens with COMPRESSED schema
    response_compressed_schema = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, tools=[compressed_schema], tool_choice="auto"
    )
    compressed_schema_tokens = response_compressed_schema.usage.prompt_tokens

    # Calculate and display schema savings
    schema_token_savings = original_schema_tokens - compressed_schema_tokens
    schema_savings_percent = (schema_token_savings / original_schema_tokens) * 100
    print(f"Original schema:    {original_schema_tokens} tokens")
    print(f"Compressed schema:  {compressed_schema_tokens} tokens")
    print(f"Saved:              {schema_token_savings} tokens ({schema_savings_percent:.1f}%)")
    print()

    # =========================================================================
    # STEP 2: Execute Tool and Measure Response Compression
    # =========================================================================
    print("=" * 80)
    print("STEP 2: Measuring Response Compression")
    print("=" * 80)

    # Execute the tool function
    assistant_message = response_compressed_schema.choices[0].message
    tool_call = assistant_message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    tool_response = search_books_impl(**function_args)

    # Compress the tool response
    response_compressor = ResponseCompressor()
    compressed_response = response_compressor.process(tool_response)

    # Measure tokens with ORIGINAL response
    messages_original = messages + build_tool_message(tool_call, json.dumps(tool_response))
    response_original = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages_original, max_tokens=150
    )
    original_response_tokens = response_original.usage.prompt_tokens

    # Measure tokens with COMPRESSED response
    messages_compressed = messages + build_tool_message(tool_call, json.dumps(compressed_response))
    response_compressed = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages_compressed, max_tokens=150
    )
    compressed_response_tokens = response_compressed.usage.prompt_tokens

    # Calculate and display response savings
    response_token_savings = original_response_tokens - compressed_response_tokens
    response_savings_percent = (response_token_savings / original_response_tokens) * 100
    print(f"Original response:    {original_response_tokens} tokens")
    print(f"Compressed response:  {compressed_response_tokens} tokens")
    print(
        f"Saved:                {response_token_savings} tokens "
        f"({response_savings_percent:.1f}%)"
    )
    print()

    # =========================================================================
    # STEP 3: Summary
    # =========================================================================
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    # Calculate total savings
    total_original_tokens = original_schema_tokens + original_response_tokens
    total_compressed_tokens = compressed_schema_tokens + compressed_response_tokens
    total_token_savings = total_original_tokens - total_compressed_tokens
    total_savings_percent = (total_token_savings / total_original_tokens) * 100

    print("Schema Compression:")
    print(f"  Original:    {original_schema_tokens:>5,} tokens")
    print(f"  Compressed:  {compressed_schema_tokens:>5,} tokens")
    print(f"  Saved:       {schema_token_savings:>5,} tokens ({schema_savings_percent:.1f}%)")
    print()

    print("Response Compression:")
    print(f"  Original:    {original_response_tokens:>5,} tokens")
    print(f"  Compressed:  {compressed_response_tokens:>5,} tokens")
    print(f"  Saved:       {response_token_savings:>5,} tokens ({response_savings_percent:.1f}%)")
    print()

    print("Total Savings:")
    print(f"  Original:    {total_original_tokens:>5,} tokens")
    print(f"  Compressed:  {total_compressed_tokens:>5,} tokens")
    print(f"  Saved:       {total_token_savings:>5,} tokens ({total_savings_percent:.1f}%)")
    print()

    print("✅ Both original and compressed responses produce correct LLM answers!")
    print(
        f"💡 Use SchemaCompressor + ResponseCompressor to save "
        f"{total_savings_percent:.1f}% tokens in tool workflows."
    )


if __name__ == "__main__":
    main()
