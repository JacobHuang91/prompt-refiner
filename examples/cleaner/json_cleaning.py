"""Example: Cleaning and compressing JSON for LLM context."""

from prompt_refiner import JsonCleaner, Refiner

# Example 1: RAG API response with nulls and empty fields
api_response = """
{
    "documents": [
        {
            "id": 1,
            "title": "Introduction to LLMs",
            "content": "Large Language Models are powerful AI systems...",
            "metadata": {
                "author": "Alice",
                "date": "2024-01-15",
                "tags": ["AI", "LLM"],
                "deprecated": null,
                "legacy_field": ""
            }
        },
        {
            "id": 2,
            "title": "Advanced Prompting",
            "content": "Prompt engineering is crucial for...",
            "metadata": {
                "author": null,
                "date": "2024-02-20",
                "tags": [],
                "categories": {}
            }
        }
    ],
    "total": 2,
    "next_page": null,
    "filters": {}
}
"""

print("=" * 60)
print("JSON CLEANING EXAMPLE")
print("=" * 60)
print(f"\nOriginal JSON (formatted):\n{api_response}")
print(f"Original size: {len(api_response)} characters")

# Example 1: Strip nulls only
print("\n" + "=" * 60)
print("Example 1: Strip nulls only")
print("=" * 60)
refiner = Pipeline().pipe(JsonCleaner(strip_nulls=True, strip_empty=False))
cleaned = refiner.run(api_response)
print(f"\nResult:\n{cleaned}")
print(f"Size: {len(cleaned)} characters ({100 - len(cleaned) * 100 // len(api_response)}% reduction)")

# Example 2: Strip nulls and empties
print("\n" + "=" * 60)
print("Example 2: Strip nulls AND empty containers")
print("=" * 60)
refiner = Pipeline().pipe(JsonCleaner(strip_nulls=True, strip_empty=True))
cleaned = refiner.run(api_response)
print(f"\nResult:\n{cleaned}")
print(f"Size: {len(cleaned)} characters ({100 - len(cleaned) * 100 // len(api_response)}% reduction)")

# Example 3: User profile with many optional fields
print("\n" + "=" * 60)
print("Example 3: User profile with optional fields")
print("=" * 60)
user_profile = """
{
    "user_id": "12345",
    "name": "Bob",
    "email": "bob@example.com",
    "phone": null,
    "address": {
        "street": "",
        "city": "",
        "zip": null
    },
    "preferences": {
        "newsletter": false,
        "notifications": true,
        "theme": ""
    },
    "social_links": [],
    "bio": null,
    "avatar_url": "",
    "last_login": "2024-01-15"
}
"""
print(f"Original:\n{user_profile}")

refiner = Pipeline().pipe(JsonCleaner(strip_nulls=True, strip_empty=True))
cleaned = refiner.run(user_profile)
print(f"\nCleaned:\n{cleaned}")
print(f"\nToken savings: {len(user_profile)} → {len(cleaned)} characters ({100 - len(cleaned) * 100 // len(user_profile)}% reduction)")

# Example 4: Only minify (no cleaning)
print("\n" + "=" * 60)
print("Example 4: Only minify (keep all data)")
print("=" * 60)
data = """
{
    "status": "ok",
    "data": null,
    "items": []
}
"""
refiner = Pipeline().pipe(JsonCleaner(strip_nulls=False, strip_empty=False))
minified = refiner.run(data)
print(f"Original: {data}")
print(f"Minified: {minified}")
print("\nNote: All data preserved, only whitespace removed")

# Example 5: Use case - RAG context compression
print("\n" + "=" * 60)
print("Example 5: RAG Context Compression Pipeline")
print("=" * 60)
rag_docs = """
{
    "query": "What are LLMs?",
    "retrieved_docs": [
        {
            "score": 0.95,
            "doc_id": "doc1",
            "text": "LLMs are large language models...",
            "metadata": null,
            "source": "",
            "deprecated_field": {}
        },
        {
            "score": 0.87,
            "doc_id": "doc2",
            "text": "Applications include chatbots...",
            "author": null,
            "tags": []
        }
    ],
    "debug_info": null,
    "cache_hit": false
}
"""

print("Use Case: Compress RAG context before sending to LLM")
print(f"\nBefore compression: {len(rag_docs)} characters")

# Aggressive cleaning to maximize token savings
refiner = Pipeline().pipe(JsonCleaner(strip_nulls=True, strip_empty=True))
compressed = refiner.run(rag_docs)

print(f"After compression: {len(compressed)} characters")
print(f"Savings: {100 - len(compressed) * 100 // len(rag_docs)}%")
print(f"\nCompressed JSON:\n{compressed}")

print("\n" + "=" * 60)
print("💡 TIP: Use JsonCleaner with other operations")
print("=" * 60)
print("""
# Combine with other cleaners for maximum compression:
from prompt_refiner import JsonCleaner, NormalizeWhitespace, TruncateTokens

pipeline = (
    JsonCleaner(strip_nulls=True, strip_empty=True)
    | TruncateTokens(max_tokens=500, strategy="head")
)

# Perfect for RAG applications where API responses contain
# many null/empty fields that waste tokens!
""")
