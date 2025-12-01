# JSON Cleaning Example

Clean and compress JSON from API responses before sending to LLM.

## Scenario

You're building a RAG application that fetches documents from an API. The API responses contain many null values and empty fields that waste tokens. You need to compress the JSON before including it in your LLM prompt.

## Example Code

```python
from prompt_refiner import JsonCleaner

api_response = """
{
    "documents": [
        {
            "id": 1,
            "title": "Introduction to LLMs",
            "content": "Large Language Models are powerful AI systems...",
            "metadata": {
                "author": "Alice",
                "deprecated": null,
                "tags": []
            }
        }
    ],
    "next_page": null,
    "filters": {}
}
"""

# Strip nulls and empty containers
cleaner = JsonCleaner(strip_nulls=True, strip_empty=True)
compressed = cleaner.run(api_response)
print(compressed)
# Output: {"documents":[{"id":1,"title":"Introduction to LLMs","content":"Large Language Models are powerful AI systems...","metadata":{"author":"Alice"}}]}
```

**Token savings:** 61% reduction (791 → 316 characters)

## Only Minify (Keep All Data)

```python
# Just remove whitespace, keep all data
cleaner = JsonCleaner(strip_nulls=False, strip_empty=False)
minified = cleaner.run(api_response)
# Output: {"documents":[...],"next_page":null,"filters":{}}
```

## RAG Pipeline

```python
from prompt_refiner import JsonCleaner, TruncateTokens

# Compress JSON and truncate if still too long
rag_pipeline = (
    JsonCleaner(strip_nulls=True, strip_empty=True)
    | TruncateTokens(max_tokens=500, strategy="head")
)

compressed = rag_pipeline.run(large_api_response)
```

## Full Example

See the complete example: [`examples/cleaner/json_cleaning.py`](https://github.com/JacobHuang91/prompt-refiner/blob/main/examples/cleaner/json_cleaning.py)

```bash
python examples/cleaner/json_cleaning.py
```

## Related

- [JsonCleaner API Reference](../api-reference/cleaner.md#jsoncleaner)
- [Cleaner Module Guide](../modules/cleaner.md)
