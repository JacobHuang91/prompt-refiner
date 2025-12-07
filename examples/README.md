# Prompt Refiner Examples

This directory contains examples demonstrating the 5 core transformation modules plus measurement utilities of Prompt Refiner.

## Core Module Examples

### 1. Cleaner Module

Clean and normalize dirty text data.

#### `cleaner/html_cleaning.py`
Demonstrates HTML tag removal and conversion to Markdown.
```bash
python examples/cleaner/html_cleaning.py
```

**What it shows:**
- Basic HTML stripping
- HTML to Markdown conversion
- Preserving semantic tags

#### `cleaner/whitespace_normalization.py`
Shows how to normalize excessive whitespace from web scraping.
```bash
python examples/cleaner/whitespace_normalization.py
```

**What it shows:**
- Collapsing multiple spaces
- Removing extra newlines
- Character count reduction

#### `cleaner/unicode_fixing.py`
Fixes problematic Unicode characters that can cause issues.
```bash
python examples/cleaner/unicode_fixing.py
```

**What it shows:**
- Zero-width space removal
- Control character cleanup
- Unicode normalization

#### `cleaner/json_cleaning.py`
Clean and compress JSON from API responses.
```bash
python examples/cleaner/json_cleaning.py
```

**What it shows:**
- Strip null values from JSON
- Remove empty containers (dicts, lists, strings)
- JSON minification
- RAG API response compression (50-60% token savings)

---

### 2. Compressor Module

Reduce token count intelligently.

#### `compressor/smart_truncation.py`
Demonstrates intelligent text truncation with sentence boundaries.
```bash
python examples/compressor/smart_truncation.py
```

**What it shows:**
- Head strategy (keep beginning)
- Tail strategy (keep end - for conversation history)
- Middle-out strategy (keep both ends)
- Sentence boundary respect

#### `compressor/deduplication.py`
Shows how to remove duplicate content (essential for RAG).
```bash
python examples/compressor/deduplication.py
```

**What it shows:**
- Jaccard similarity for fast deduplication
- Levenshtein distance for accurate matching
- Sentence vs paragraph granularity
- RAG context optimization

---

### 3. Scrubber Module

Protect sensitive information.

#### `scrubber/pii_redaction.py`
Demonstrates automatic PII detection and redaction.
```bash
python examples/scrubber/pii_redaction.py
```

**What it shows:**
- Email, phone, IP, credit card redaction
- Selective PII type filtering
- Custom patterns and keywords
- Enterprise data protection

---

### 4. Tools Module

Optimize LLM tool schemas and responses.

#### `tools/schema_compression.py`
Demonstrates compressing tool schemas for function calling.
```bash
python examples/tools/schema_compression.py
```

**What it shows:**
- Compress OpenAI/Anthropic function calling schemas
- Remove documentation overhead (titles, examples, markdown)
- Preserve all protocol fields (name, type, required, enum)
- Real-world OpenAI integration example with actual API calls
- Handle nested objects and array types
- 10-50% token savings depending on schema verbosity

#### `tools/response_compression.py`
Demonstrates compressing verbose API/tool responses.
```bash
python examples/tools/response_compression.py
```

**What it shows:**
- Compress verbose API responses before sending to LLM
- Remove debug/trace fields automatically
- Limit strings to 512 chars and lists to 16 items
- Real-world OpenAI integration proving LLM understanding
- 30-70% token savings on verbose responses
- Example shows 36% savings (4,818 → 3,079 tokens)

#### `tools/complete_workflow.py`
Complete tool calling workflow with both SchemaCompressor and ResponseCompressor.
```bash
python examples/tools/complete_workflow.py
```

**What it shows:**
- Real-world OpenAI tool calling workflow (search_books via Google Books API)
- Compress tool schema with SchemaCompressor (7.0% savings)
- Execute tool and get large JSON response (40 books, ~20,000 tokens)
- Compress response with ResponseCompressor (31.1% savings)
- Compare LLM understanding with original vs compressed
- Example shows 30.9% total savings (20,271 → 14,006 tokens)
- Standard OpenAI tool calling pattern with both compressions

---

## Measurement Utilities

### Analyzer Module

**Note:** The Analyzer module measures optimization impact but does not transform prompts.

#### `analyzer/token_counting.py`
Shows token counting and cost savings calculation.
```bash
python examples/analyzer/token_counting.py
```

**What it shows:**
- Token count comparison
- Optimization statistics
- Cost savings calculation
- Before/after analysis

---

## Custom Operations

### `custom_operation.py`
Learn how to create your own custom operations by extending the base `Operation` class.
```bash
python examples/custom_operation.py
```

**What it shows:**
- Creating custom operations
- Extending the Operation base class
- Using custom operations in pipelines
- Example: RemoveEmojis operation

---

### 5. Packer Module

Intelligently manage context budgets for RAG applications and chatbots.

#### `packer/messages.py`
Demonstrates MessagesPacker for chat completion APIs.
```bash
python examples/packer/messages.py
```

**What it shows:**
- Priority-based selection
- Semantic roles (ROLE_SYSTEM, ROLE_QUERY, ROLE_CONTEXT)
- RAG document integration with JIT cleaning
- Conversation history management
- Returns List[Dict] ready for OpenAI/Anthropic

#### `packer/text.py`
Demonstrates TextPacker for text completion APIs.
```bash
python examples/packer/text.py
```

**What it shows:**
- MARKDOWN format with grouped sections
- Multiple conversation history messages
- Budget-based message dropping
- Returns str ready for Llama/GPT-3 base models

---

## Running Examples

All examples can be run from the project root:

```bash
# Run module examples
python examples/cleaner/html_cleaning.py
python examples/cleaner/json_cleaning.py
python examples/compressor/smart_truncation.py
python examples/scrubber/pii_redaction.py
python examples/tools/schema_compression.py
python examples/tools/response_compression.py
python examples/tools/complete_workflow.py
python examples/analyzer/token_counting.py
python examples/packer/messages.py
python examples/packer/text.py
```

---

## Example Use Cases

### Web Scraping Pipeline
```python
from prompt_refiner import Refiner, StripHTML, NormalizeWhitespace, FixUnicode

refiner = (
    Refiner()
    .pipe(StripHTML(to_markdown=True))
    .pipe(NormalizeWhitespace())
    .pipe(FixUnicode())
)
```

### RAG Context Optimization
```python
from prompt_refiner import Refiner, Deduplicate, TruncateTokens

refiner = (
    Refiner()
    .pipe(Deduplicate(similarity_threshold=0.85))
    .pipe(TruncateTokens(max_tokens=500, strategy="head"))
)
```

### RAG JSON API Compression
```python
from prompt_refiner import Refiner, JsonCleaner, TruncateTokens

refiner = (
    Refiner()
    .pipe(JsonCleaner(strip_nulls=True, strip_empty=True))
    .pipe(TruncateTokens(max_tokens=500, strategy="head"))
)
```

### Enterprise Data Protection
```python
from prompt_refiner import Refiner, RedactPII, CountTokens

counter = CountTokens(original_text=original)
refiner = (
    Refiner()
    .pipe(RedactPII())
    .pipe(counter)
)
```

### Tool Schema Compression
```python
from prompt_refiner import SchemaCompressor

# Compress function calling schemas (all features enabled by default)
compressor = SchemaCompressor()

# Compress before sending to OpenAI/Anthropic (10-50% savings)
compressed_tool = compressor.process(tool)
```

### Complete Tool Calling Workflow
```python
from prompt_refiner import SchemaCompressor, ResponseCompressor
from openai import OpenAI

client = OpenAI()

# 1. Compress tool schema
schema_compressor = SchemaCompressor()
compressed_schema = schema_compressor.process(tool_schema)

# 2. Call OpenAI with compressed schema
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=[compressed_schema]
)

# 3. Execute tool
tool_call = response.choices[0].message.tool_calls[0]
tool_response = execute_tool(tool_call)

# 4. Compress tool response
response_compressor = ResponseCompressor()
compressed_response = response_compressor.process(tool_response)

# 5. Send compressed response to LLM (saves 30-70% tokens)
final_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages + [
        {"role": "assistant", "tool_calls": [...]},
        {"role": "tool", "content": json.dumps(compressed_response)}
    ]
)
```

---

## Tips

1. **Order matters**: Run Cleaner operations first, then Compressor, then Scrubber
2. **Measurement vs transformation**: Analyzer measures but doesn't transform - use it to track savings
3. **Test with real data**: These examples use simplified data - test with your actual use case
4. **Tune parameters**: Adjust thresholds and strategies based on your specific needs
5. **Combine strategically**: Not every operation is needed for every use case

---

## Learn More

- See `MODULES.md` for detailed API documentation
- See `README.md` for installation and quickstart
- See `tests/` for more usage patterns
