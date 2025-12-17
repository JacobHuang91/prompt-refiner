# Tools Module

The Tools module optimizes AI agent function calling by compressing tool schemas and responses. This is one of the most impactful optimizations in Prompt Refiner, achieving **57% average token reduction** with 100% lossless compression.

!!! success "Benchmark Results"
    Tested on 20 real-world API schemas (Stripe, Salesforce, HubSpot, Slack, OpenAI, Anthropic), SchemaCompressor achieves:

    - **56.9% average reduction** across all schemas
    - **70%+ reduction** on enterprise APIs
    - **100% lossless** - all protocol fields preserved
    - **100% callable (20/20 validated)** - all compressed schemas work correctly with OpenAI function calling
    - A medium agent (10 tools, 500 calls/day) saves **$541/month** on GPT-4

    [View benchmark results →](../benchmark.md#function-calling-benchmark)

## Overview

Function calling is a major source of token consumption in AI agent systems:

- **Tool schemas** with verbose descriptions consume thousands of tokens
- **API responses** often include debug info, traces, and excessive data
- **Multiple tools** multiply the cost (10 tools = 10x the schema tokens)

The Tools module solves this with two components:

1. **SchemaCompressor** - Compress function/tool schemas (OpenAI, Anthropic format)
2. **ResponseCompressor** - Compress verbose API/tool responses

## SchemaCompressor

Compresses tool schemas while preserving 100% of the protocol specification.

### Basic Usage

```python
from prompt_refiner import SchemaCompressor

# Your tool schema (OpenAI or Anthropic format)
tool_schema = {
    "type": "function",
    "function": {
        "name": "search_products",
        "description": "Search for products in the e-commerce catalog...",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query with keywords..."
                },
                # ... more parameters
            },
            "required": ["query"]
        }
    }
}

# Compress the schema
compressor = SchemaCompressor()
compressed_schema = compressor.process(tool_schema)

# Use compressed schema with OpenAI/Anthropic
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    tools=[compressed_schema]  # Compressed but functionally identical
)
```

### What Gets Compressed

SchemaCompressor optimizes documentation fields while preserving all protocol fields:

**✅ Optimized (Documentation)**:
- `description` fields (main source of verbosity)
- Redundant explanations and examples
- Marketing language and filler words
- Overly detailed parameter descriptions

**❌ Never Modified (Protocol)**:
- Function `name`
- Parameter `names`
- Parameter `type` (string, number, boolean, etc.)
- `required` fields list
- `enum` values
- `default` values
- JSON structure

### Integration with Pydantic

Works seamlessly with Pydantic function tools:

```python
from pydantic import BaseModel, Field
from openai.pydantic_function_tool import pydantic_function_tool
from prompt_refiner import SchemaCompressor

class SearchBooksInput(BaseModel):
    """Search for books in the library database."""

    query: str = Field(
        description="The search query string containing keywords..."
    )
    category: str | None = Field(
        default=None,
        description="Filter by book category like Fiction, Science..."
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of results to return..."
    )

# Generate and compress schema
tool_schema = pydantic_function_tool(SearchBooksInput, name="search_books")
compressed = SchemaCompressor().process(tool_schema)

# 30-60% token reduction typical for Pydantic schemas
```

### Performance by Schema Type

Token reduction varies by schema verbosity:

| Schema Type | Avg Reduction | Example |
|-------------|---------------|---------|
| **Very Verbose** (Enterprise APIs) | 67.4% | HubSpot Contact (73.2%), Salesforce Account (72.1%) |
| **Complex** (Rich APIs) | 61.7% | Slack (70.8%), Stripe (66.7%), E-commerce (46.0%) |
| **Medium** (Standard APIs) | 13.1% | Weather API (20.1%), GitHub (6.1%) |
| **Simple** (Minimal APIs) | 0.0% | Calculator (already minimal) |

!!! tip "Best Candidates for Compression"
    Enterprise and complex APIs with extensive documentation see 60-70%+ reduction. Simple APIs with minimal docs see little benefit (already optimized).

### Batch Compression

Compress multiple tool schemas at once:

```python
from prompt_refiner import SchemaCompressor

tools = [
    search_tool_schema,
    create_tool_schema,
    update_tool_schema,
    delete_tool_schema
]

compressor = SchemaCompressor()
compressed_tools = [compressor.process(tool) for tool in tools]

# Use all compressed tools
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    tools=compressed_tools  # All compressed
)
```

## ResponseCompressor

Compresses verbose API/tool responses before sending back to the LLM.

### Basic Usage

```python
from prompt_refiner import ResponseCompressor

# Verbose API response
api_response = {
    "results": [
        {"id": 1, "name": "Product A", "price": 29.99},
        {"id": 2, "name": "Product B", "price": 39.99},
        # ... 100 more results
    ],
    "debug_info": {
        "query_time_ms": 45,
        "cache_hit": True,
        "server": "api-01"
    },
    "trace_id": "abc123...",
    "logs": ["Started query", "Fetched from DB", ...],
    "metadata": {...}
}

# Compress the response
compressor = ResponseCompressor()
compact_response = compressor.process(api_response)

# Compact response sent back to LLM
# - Keeps essential data (results, relevant fields)
# - Removes debug/trace/logs
# - Truncates long lists and strings
# - 30-70% token reduction typical
```

### What Gets Compressed

**Removed:**
- Debug fields (`debug_info`, `trace_id`, `_debug`)
- Log fields (`logs`, `log`, `trace`, `_trace`)
- Excessive metadata

**Truncated:**
- Long strings (> 512 chars)
- Long lists (> 16 items)
- Deep nesting (> 10 levels)

**Preserved:**
- Essential data fields
- JSON structure
- Data types

### Configuration

ResponseCompressor uses sensible hardcoded limits (no configuration needed):

- **String limit**: 512 characters
- **List limit**: 16 items
- **Max depth**: 10 levels
- **Drop nulls**: Optional (default: True)
- **Drop empty containers**: Optional (default: True)

```python
# Default behavior (recommended)
compressor = ResponseCompressor()

# Keep nulls and empty containers if needed
compressor = ResponseCompressor()
# Currently no customization - uses hardcoded sensible defaults
```

### Integration in Agent Workflow

Typical AI agent flow with compression:

```python
from prompt_refiner import SchemaCompressor, ResponseCompressor
import openai

# 1. Compress tool schemas (one-time, reuse compressed schemas)
tool_schema = {...}
compressed_schema = SchemaCompressor().process(tool_schema)

# 2. Call LLM with compressed schema
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Search for Python books"}],
    tools=[compressed_schema]
)

# 3. Execute tool
tool_call = response.choices[0].message.tool_calls[0]
function_args = json.loads(tool_call.function.arguments)
tool_response = search_books(**function_args)  # Verbose response

# 4. Compress tool response before sending back to LLM
compact_response = ResponseCompressor().process(tool_response)

# 5. Continue conversation with compressed response
final_response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Search for Python books"},
        response.choices[0].message,
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(compact_response)  # Compressed
        }
    ]
)
```

## Cost Savings

Real-world cost savings for different agent sizes:

| Agent Size | Tools | Calls/Day | Monthly Savings (GPT-4) | Annual Savings |
|------------|-------|-----------|-------------------------|----------------|
| **Small** | 5 | 100 | $44 | $528 |
| **Medium** | 10 | 500 | $541 | $6,492 |
| **Large** | 20 | 1,000 | $3,249 | $38,988 |
| **Enterprise** | 50 | 5,000 | $40,664 | $487,968 |

*Assumes 56.9% average schema reduction, GPT-4 pricing ($0.03/1k input tokens)*

!!! example "Medium Agent Breakdown"
    **Setup**: 10 tools, 500 calls/day, GPT-4

    **Before compression**:
    - 10 tools × 800 tokens/tool = 8,000 tokens per call
    - 500 calls/day × 30 days = 15,000 calls/month
    - 15,000 × 8,000 = 120M tokens/month
    - Cost: 120M / 1000 × $0.03 = **$3,600/month**

    **After compression (56.9% reduction)**:
    - 10 tools × 345 tokens/tool = 3,450 tokens per call
    - 15,000 × 3,450 = 51.75M tokens/month
    - Cost: 51.75M / 1000 × $0.03 = **$1,553/month**

    **Monthly savings: $2,047** 🎉

## Best Practices

### 1. Compress Schemas Once, Reuse

Tool schemas don't change often - compress once and reuse:

```python
# At application startup
compressor = SchemaCompressor()
COMPRESSED_TOOLS = [
    compressor.process(search_schema),
    compressor.process(create_schema),
    compressor.process(update_schema)
]

# In your agent loop - use pre-compressed schemas
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=COMPRESSED_TOOLS  # Reuse compressed schemas
)
```

### 2. Always Compress Responses

API responses are often verbose - always compress before sending to LLM:

```python
# BAD: Send raw verbose response
tool_response = api.search(query)
messages.append({"role": "tool", "content": json.dumps(tool_response)})

# GOOD: Compress before sending
tool_response = api.search(query)
compact = ResponseCompressor().process(tool_response)
messages.append({"role": "tool", "content": json.dumps(compact)})
```

### 3. Monitor Token Savings

Track actual savings to validate optimization:

```python
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4")

# Before
original_tokens = len(encoder.encode(json.dumps(original_schema)))

# After
compressed_tokens = len(encoder.encode(json.dumps(compressed_schema)))

print(f"Saved {original_tokens - compressed_tokens} tokens ({(1 - compressed_tokens/original_tokens)*100:.1f}% reduction)")
```

### 4. Test with Real Schemas

Test compression on your actual tool schemas to measure impact:

```python
from prompt_refiner import SchemaCompressor
import json

# Load your schema
with open("my_tool_schema.json") as f:
    schema = json.load(f)

# Compress and compare
compressed = SchemaCompressor().process(schema)

print("Original:", json.dumps(schema, indent=2))
print("\nCompressed:", json.dumps(compressed, indent=2))
print(f"\nSize reduction: {len(json.dumps(schema))} → {len(json.dumps(compressed))} chars")
```

## Limitations

### SchemaCompressor

- Only works with OpenAI/Anthropic function calling format
- Minimal benefit on already-concise schemas (< 200 tokens)
- English-language descriptions assumed (may not optimize other languages well)

### ResponseCompressor

- Hardcoded limits (512 char strings, 16 item lists) - cannot customize
- May truncate important data if not configured for your use case
- Binary data (images, files) not supported

## Examples

### Complete Agent Example

See [`examples/tools/`](https://github.com/JacobHuang91/prompt-refiner/tree/main/examples/tools) for complete working examples with OpenAI function calling.

### Benchmark

See [`benchmark/function_calling/`](https://github.com/JacobHuang91/prompt-refiner/tree/main/benchmark/function_calling) for comprehensive benchmark on 20 real-world API schemas.

## API Reference

For detailed API documentation, see:

- [SchemaCompressor API Reference](../api-reference/tools.md#schemacompressor)
- [ResponseCompressor API Reference](../api-reference/tools.md#responsecompressor)

## Learn More

- [Function Calling Benchmark Results](../benchmark.md#function-calling-benchmark)
- [Tools Module Examples (GitHub)](https://github.com/JacobHuang91/prompt-refiner/tree/main/examples/tools)
- [SchemaCompressor Implementation](https://github.com/JacobHuang91/prompt-refiner/blob/main/src/prompt_refiner/tools/schema_compressor.py)
- [ResponseCompressor Implementation](https://github.com/JacobHuang91/prompt-refiner/blob/main/src/prompt_refiner/tools/response_compressor.py)
