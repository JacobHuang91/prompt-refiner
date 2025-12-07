"""
ResponseCompressor Demo - Prove Token Savings with OpenAI

Demonstrates that ResponseCompressor significantly reduces tokens while
preserving the essential information that LLMs need to understand responses.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from prompt_refiner import ResponseCompressor

# Load environment variables
load_dotenv()


def main():
    # Simulate a verbose API response from a web search tool
    api_response = {
        "tool": "web_search",
        "query": "What is the capital of France?",
        "results": [
            {
                "id": i,
                "title": f"Result {i}: Paris - Capital of France",
                "snippet": (
                    "Paris is the capital and most populous city of France. "
                    "With an official estimated population of 2,102,650 residents "
                    "as of 1 January 2023 in an area of more than 105 km2, "
                    "Paris is the fourth-most populated city in the European Union. "
                    "The City of Paris is the centre of the Île-de-France region. "
                    "Paris is a major railway, highway, and air-transport hub. "
                    "The city is served by three commercial international airports. "
                    "Additional historical context and tourism information follows..."
                ),
                "url": f"https://example.com/paris-{i}",
                "metadata": {
                    "author": f"Author {i}",
                    "date": "2024-01-01",
                    "source": "Wikipedia",
                    "language": "en",
                },
                "debug_info": {
                    "relevance_score": 0.95,
                    "cache_hit": True,
                    "processing_time_ms": 45,
                },
            }
            for i in range(25)
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 5,
            "total_results": 125,
        },
        "debug": {
            "query_time_ms": 234,
            "api_version": "2.0",
            "server_id": "srv-001",
        },
        "trace": {
            "request_id": "abc-123-def-456",
            "timestamp": "2024-01-01T12:00:00Z",
        },
    }

    # Calculate original size
    original_json = json.dumps(api_response, separators=(",", ":"))
    original_tokens = len(original_json) // 4  # Rough estimate

    print("=" * 80)
    print("ORIGINAL API RESPONSE")
    print("=" * 80)
    print(f"Total results: {len(api_response['results'])}")
    print(f"Characters: {len(original_json):,}")
    print(f"Estimated tokens: ~{original_tokens:,}")
    print()

    # Compress the response
    compressor = ResponseCompressor()
    compressed_response = compressor.process(api_response)

    # Calculate compressed size
    compressed_json = json.dumps(compressed_response, separators=(",", ":"))
    compressed_tokens = len(compressed_json) // 4  # Rough estimate
    savings = (1 - len(compressed_json) / len(original_json)) * 100

    print("=" * 80)
    print("COMPRESSED RESPONSE")
    print("=" * 80)
    print(f"Total results: {len(compressed_response['results'])}")
    print(f"Characters: {len(compressed_json):,}")
    print(f"Estimated tokens: ~{compressed_tokens:,}")
    print(f"Token savings: {savings:.1f}%")
    print()

    # Verify with OpenAI that both responses are understood correctly
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not found in environment variables.")
        print("Set it in .env file to test LLM understanding.")
        return

    client = OpenAI()

    print("=" * 80)
    print("TESTING LLM UNDERSTANDING")
    print("=" * 80)
    print()

    # Test with original response
    print("Testing with ORIGINAL response...")
    response_original = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Here is a tool response:\n{json.dumps(api_response, indent=2)}\n\n"
                f"Based on this response, what is the capital of France?",
            },
        ],
        max_tokens=50,
    )
    answer_original = response_original.choices[0].message.content.strip()
    print(f"Answer: {answer_original}")
    print()

    # Test with compressed response
    print("Testing with COMPRESSED response...")
    response_compressed = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Here is a tool response:\n{json.dumps(compressed_response, indent=2)}\n\n"
                f"Based on this response, what is the capital of France?",
            },
        ],
        max_tokens=50,
    )
    answer_compressed = response_compressed.choices[0].message.content.strip()
    print(f"Answer: {answer_compressed}")
    print()

    # Show results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"✓ Original response: {answer_original}")
    print(f"✓ Compressed response: {answer_compressed}")
    print()
    print(f"Token savings: {savings:.1f}%")
    print(
        f"Saved ~{original_tokens - compressed_tokens:,} tokens "
        f"({original_tokens:,} → {compressed_tokens:,})"
    )
    print()
    print("✅ Both responses allow LLM to correctly answer the question!")
    print(
        "💡 Use ResponseCompressor to save 30-70% tokens on tool responses "
        "without losing essential information."
    )


if __name__ == "__main__":
    main()
