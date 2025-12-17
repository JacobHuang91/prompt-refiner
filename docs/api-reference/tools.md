# Tools Module

The Tools module optimizes AI agent function calling by compressing tool schemas and responses. Achieves **57% average token reduction** with 100% lossless compression.

## SchemaCompressor

Compress tool/function schemas (OpenAI, Anthropic format) while preserving 100% of protocol fields.

::: prompt_refiner.tools.SchemaCompressor
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Key Features

- **57% average reduction** across 20 real-world API schemas
- **100% lossless** - all protocol fields preserved (name, type, required, enum)
- **100% callable (20/20 validated)** - all compressed schemas work correctly with OpenAI function calling
- **70%+ reduction** on enterprise APIs (HubSpot, Salesforce, OpenAI)
- Works with OpenAI and Anthropic function calling format

### Examples

```python
from prompt_refiner import SchemaCompressor

# Basic usage
tool_schema = {
    "type": "function",
    "function": {
        "name": "search_products",
        "description": "Search for products in the e-commerce catalog...",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query..."}
            },
            "required": ["query"]
        }
    }
}

compressor = SchemaCompressor()
compressed = compressor.process(tool_schema)
# Result: 30-70% smaller, functionally identical
```

```python
# With Pydantic
from pydantic import BaseModel, Field
from openai.pydantic_function_tool import pydantic_function_tool
from prompt_refiner import SchemaCompressor

class SearchInput(BaseModel):
    query: str = Field(description="The search query...")
    category: str | None = Field(default=None, description="Filter by category...")

# Generate and compress schema
tool_schema = pydantic_function_tool(SearchInput, name="search")
compressed = SchemaCompressor().process(tool_schema)

# Use with OpenAI
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    tools=[compressed]  # Compressed but functionally identical
)
```

```python
# Batch compression
tools = [search_schema, create_schema, update_schema, delete_schema]
compressor = SchemaCompressor()
compressed_tools = [compressor.process(tool) for tool in tools]

# Use all compressed tools
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    tools=compressed_tools
)
```

### What Gets Compressed

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

!!! success "100% Lossless"
    SchemaCompressor never modifies protocol fields. The compressed schema is functionally identical to the original - LLMs will call the function with the same arguments.

---

## ResponseCompressor

Compress verbose API/tool responses before sending back to the LLM.

::: prompt_refiner.tools.ResponseCompressor
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Key Features

- **25.8% average reduction** on 20 real-world API responses (range: 14-53%)
- Removes debug/trace/logs fields automatically
- Truncates long strings (> 512 chars) and lists (> 16 items)
- Preserves essential data structure
- **52.7% reduction** on verbose responses like Stripe Payment API

### Examples

```python
from prompt_refiner import ResponseCompressor

# Basic usage
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
    "logs": ["Started query", "Fetched from DB", ...]
}

compressor = ResponseCompressor()
compact = compressor.process(api_response)
# Result: Essential data kept, debug/trace/logs removed, long lists truncated
```

```python
# In agent workflow
from prompt_refiner import SchemaCompressor, ResponseCompressor
import openai
import json

# 1. Compress tool schema
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

# 4. Compress response before sending to LLM
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

ResponseCompressor uses sensible hardcoded limits:

- **String limit**: 512 characters
- **List limit**: 16 items
- **Max depth**: 10 levels
- **Drop nulls**: True (automatic)
- **Drop empty containers**: True (automatic)

!!! tip "No Configuration Needed"
    ResponseCompressor uses hardcoded sensible defaults that work well for most API responses. No configuration required.

---

## Cost Savings

Typical savings for different agent sizes using GPT-4 ($0.03/1k input tokens):

| Agent Size | Tools | Calls/Day | Monthly Savings | Annual Savings |
|------------|-------|-----------|-----------------|----------------|
| **Small** | 5 | 100 | $44 | $528 |
| **Medium** | 10 | 500 | $541 | $6,492 |
| **Large** | 20 | 1,000 | $3,249 | $38,988 |
| **Enterprise** | 50 | 5,000 | $40,664 | $487,968 |

*Based on 56.9% average schema reduction*

---

## Best Practices

### 1. Compress Schemas Once, Reuse

```python
# At application startup
compressor = SchemaCompressor()
COMPRESSED_TOOLS = [
    compressor.process(search_schema),
    compressor.process(create_schema),
    compressor.process(update_schema)
]

# In agent loop - reuse compressed schemas
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=COMPRESSED_TOOLS  # Reuse
)
```

### 2. Always Compress Responses

```python
# Always compress before sending to LLM
tool_response = api.search(query)
compact = ResponseCompressor().process(tool_response)
messages.append({"role": "tool", "content": json.dumps(compact)})
```

### 3. Monitor Token Savings

```python
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4")

original_tokens = len(encoder.encode(json.dumps(original_schema)))
compressed_tokens = len(encoder.encode(json.dumps(compressed_schema)))

print(f"Saved {original_tokens - compressed_tokens} tokens")
print(f"Reduction: {(1 - compressed_tokens/original_tokens)*100:.1f}%")
```

---

## Benchmark Results

See [comprehensive benchmark results](../benchmark.md#function-calling-benchmark) for detailed performance on 20 real-world API schemas.

## Learn More

- [Tools Module Guide](../modules/tools.md)
- [Tools Examples (GitHub)](https://github.com/JacobHuang91/prompt-refiner/tree/main/examples/tools)
- [Benchmark Results](../benchmark.md#function-calling-benchmark)
