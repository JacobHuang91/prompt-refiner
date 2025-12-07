# Prompt Refiner

A lightweight Python library for building production LLM applications. Save 10-20% on API costs and manage context windows intelligently.

## Overview

Prompt Refiner solves two core problems for production LLM applications:

1. **Token Optimization** - Clean dirty inputs (HTML, whitespace, PII) to reduce API costs by 10-20%
2. **Context Management** - Pack system prompts, RAG docs, and chat history into token budgets with smart priority-based selection

Perfect for RAG applications, chatbots, and any production system that needs to manage LLM context windows efficiently.

!!! success "Proven Effectiveness"
    Benchmarked on 30 real-world test cases, Prompt Refiner achieves **4-15% token reduction** while maintaining 96-99% quality. Aggressive optimization can save up to **~$54/month** on GPT-4 at scale (1M tokens/month).

    Processing overhead is **< 0.5ms per 1k tokens** - negligible compared to network and LLM latency.

    [See benchmark results →](benchmark.md)

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

## 5 Core Modules

Prompt Refiner is organized into 5 specialized modules:

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

### Context Budget Management

#### 4. Packer - Intelligent Context Packing (v0.1.3+)

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
