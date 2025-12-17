# Prompt Refiner

A lightweight Python library for building production LLM applications. **Save 5-70% on API costs** - from function calling optimization to RAG context management.

## Overview

Prompt Refiner solves three core problems for production LLM applications:

1. **Function Calling Optimization** - Compress tool schemas by **57% on average** with 100% lossless compression
2. **Token Optimization** - Clean dirty inputs (HTML, whitespace, PII) to reduce API costs by 5-15%
3. **Context Management** - Pack system prompts, RAG docs, and chat history with smart priority-based selection

Perfect for AI agents, RAG applications, chatbots, and any production system that uses function calling or needs to manage LLM context windows efficiently.

!!! success "Proven Effectiveness"
    **Function Calling**: Tested on 20 real-world API schemas (Stripe, Salesforce, HubSpot, Slack), achieving **56.9% average token reduction** with 100% protocol field preservation and **100% callable (20/20 validated)** with OpenAI function calling. Enterprise APIs see **70%+ reduction**. A medium agent (10 tools, 500 calls/day) saves **$541/month** on GPT-4.

    **RAG & Text**: Benchmarked on 30 real-world test cases, achieving **5-15% token reduction** while maintaining 96-99% quality.

    **Performance**: Processing overhead is **< 0.5ms per 1k tokens** - negligible compared to network and LLM latency.

    [See comprehensive benchmark results →](benchmark.md)

## Quick Start

### Option 1: Preset Strategies (Easiest)

**New in v0.1.5**: Use benchmark-tested preset strategies for instant token optimization:

```python
from prompt_refiner.strategy import MinimalStrategy, AggressiveStrategy

# Minimal: 4.3% reduction, 98.7% quality
refiner = MinimalStrategy().create_refiner()
cleaned = refiner.run("<div>Your HTML content</div>")

# Aggressive: 15% reduction, 96.4% quality
refiner = AggressiveStrategy(max_tokens=150).create_refiner()
cleaned = refiner.run(long_context)
```

[Learn more about strategies →](api-reference/strategy.md){ .md-button }

### Option 2: Custom Pipelines (Flexible)

Build custom cleaning pipelines with the pipe operator:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace, TruncateTokens

# Define a cleaning pipeline
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | TruncateTokens(max_tokens=1000, strategy="middle_out")
)

raw_input = "<div>  User input with <b>lots</b> of   spaces... </div>"
clean_prompt = pipeline.run(raw_input)
# Output: "User input with lots of spaces..."
```

!!! tip "Alternative: Fluent API"
    Prefer method chaining? Use `Refiner().pipe()`:
    ```python
    from prompt_refiner import Refiner

    pipeline = Refiner().pipe(StripHTML()).pipe(NormalizeWhitespace())
    ```

## 6 Core Modules

Prompt Refiner is organized into 6 specialized modules:

### Text Processing Operations

#### 1. Cleaner - Clean Dirty Data
- **StripHTML()** - Remove HTML tags, convert to Markdown
- **NormalizeWhitespace()** - Collapse excessive whitespace
- **FixUnicode()** - Remove zero-width spaces and problematic Unicode
- **JsonCleaner()** - Strip nulls/empties from JSON, minify

[Learn more about Cleaner →](modules/cleaner.md){ .md-button }

#### 2. Compressor - Reduce Size
- **TruncateTokens()** - Smart truncation with sentence boundaries
    - Strategies: `"head"`, `"tail"`, `"middle_out"`
- **Deduplicate()** - Remove similar content (great for RAG)

[Learn more about Compressor →](modules/compressor.md){ .md-button }

#### 3. Scrubber - Security & Privacy
- **RedactPII()** - Automatically redact emails, phones, IPs, credit cards, URLs, SSNs

[Learn more about Scrubber →](modules/scrubber.md){ .md-button }

### AI Agent & Function Calling

#### 4. Tools - Function Calling Optimization (v0.1.6+)

Dramatically reduce token costs for AI agents by compressing tool schemas and responses:

- **SchemaCompressor()** - Compress tool/function schemas by **57% on average**
    - 100% lossless - all protocol fields preserved
    - Works with OpenAI and Anthropic function calling
    - Enterprise APIs: 70%+ reduction
- **ResponseCompressor()** - Compress verbose API responses by 30-70%
    - Removes debug/trace/logs fields
    - Truncates long strings and lists
    - Preserves essential data structure

```python
from prompt_refiner import SchemaCompressor, ResponseCompressor
from pydantic import BaseModel

# Compress tool schema (saves tokens on every request)
class SearchInput(BaseModel):
    query: str
    max_results: int = 10

tool_schema = pydantic_function_tool(SearchInput, name="search")
compressed = SchemaCompressor().process(tool_schema)
# Use compressed schema in OpenAI/Anthropic function calling

# Compress tool responses (saves tokens on responses)
verbose_response = {"results": [...], "debug_info": {...}}
compact = ResponseCompressor().process(verbose_response)
```

[Learn more about Tools →](modules/tools.md){ .md-button }

### Context Budget Management

#### 5. Packer - Intelligent Context Packing (v0.1.3+)

For RAG applications and chatbots, the Packer module manages context budgets with priority-based selection:

- **MessagesPacker()** - For chat completion APIs (OpenAI, Anthropic). Returns `List[Dict]`
- **TextPacker()** - For text completion APIs (Llama Base, GPT-3). Returns `str`

**Key Features:**
- Smart priority-based selection (auto-prioritizes: system > query > context > history)
- JIT refinement with `refine_with` parameter
- Automatic format overhead calculation
- Semantic roles for clear intent

```python
from prompt_refiner import MessagesPacker, StripHTML

packer = MessagesPacker(max_tokens=1000)
packer.add("You are helpful.", role="system")

# Clean RAG documents on-the-fly
packer.add(
    "<div>RAG doc...</div>",
    role="context",
    refine_with=StripHTML()
)

packer.add("User question?", role="query")

messages = packer.pack()  # Returns List[Dict] ready for chat APIs
```

[Learn more about Packer →](modules/packer.md){ .md-button }

#### 5. Strategy - Preset Strategies (v0.1.5+)

For quick setup, use benchmark-tested preset strategies:

- **MinimalStrategy** - 4.3% reduction, 98.7% quality (HTML + Whitespace)
- **StandardStrategy** - 4.8% reduction, 98.4% quality (+ Deduplication)
- **AggressiveStrategy** - 15% reduction, 96.4% quality (+ Truncation)

```python
from prompt_refiner.strategy import StandardStrategy

# Quick setup with preset
refiner = StandardStrategy().create_refiner()
cleaned = refiner.run("<div>Your HTML content</div>")

# Extend with additional operations
refiner.pipe(RedactPII(redact_types={"email"}))
```

[Learn more about Strategy →](api-reference/strategy.md){ .md-button }

---

## Measurement & Analysis

Track optimization impact without transforming prompts:

- **CountTokens()** - Calculate token savings and ROI
  - **Estimation mode** (default): Character-based approximation
  - **Precise mode** (with tiktoken): Exact token counts

[Learn more about Analyzer →](modules/analyzer.md){ .md-button }

---

## Complete Example

```python
from prompt_refiner import (
    # Core Modules
    StripHTML, NormalizeWhitespace, FixUnicode, JsonCleaner,  # Cleaner
    Deduplicate, TruncateTokens,  # Compressor
    RedactPII,  # Scrubber
    # Measurement
    CountTokens
)

original_text = """Your messy input here..."""

counter = CountTokens(original_text=original_text)

pipeline = (
    # Clean
    StripHTML(to_markdown=True)
    | NormalizeWhitespace()
    | FixUnicode()
    # Compress
    | Deduplicate(similarity_threshold=0.85)
    | TruncateTokens(max_tokens=500, strategy="head")
    # Secure
    | RedactPII(redact_types={"email", "phone"})
    # Analyze
    | counter
)

result = pipeline.run(original_text)
print(counter.format_stats())  # Shows token savings
```

## Next Steps

<div class="grid cards" markdown>

-   __Get Started__

    ---

    Install Prompt Refiner and build your first pipeline in minutes

    [:octicons-arrow-right-24: Getting Started](getting-started.md)

-   __API Reference__

    ---

    Complete API documentation for all operations and modules

    [:octicons-arrow-right-24: API Reference](api-reference/index.md)

-   __Examples__

    ---

    Browse practical examples for each module

    [:octicons-arrow-right-24: Examples](examples/index.md)

-   __Contributing__

    ---

    Learn how to contribute to the project

    [:octicons-arrow-right-24: Contributing Guide](contributing.md)

</div>
