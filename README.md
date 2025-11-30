# Prompt Refiner

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/llm-prompt-refiner.svg)](https://pypi.org/project/llm-prompt-refiner/)
[![Python Versions](https://img.shields.io/pypi/pyversions/llm-prompt-refiner.svg)](https://pypi.org/project/llm-prompt-refiner/)
[![Downloads](https://img.shields.io/pypi/dm/llm-prompt-refiner.svg)](https://pypi.org/project/llm-prompt-refiner/)
[![GitHub Stars](https://img.shields.io/github/stars/JacobHuang91/prompt-refiner)](https://github.com/JacobHuang91/prompt-refiner)
[![CI Status](https://github.com/JacobHuang91/prompt-refiner/workflows/CI/badge.svg)](https://github.com/JacobHuang91/prompt-refiner/actions)
[![codecov](https://codecov.io/gh/JacobHuang91/prompt-refiner/branch/main/graph/badge.svg)](https://codecov.io/gh/JacobHuang91/prompt-refiner)
[![License](https://img.shields.io/github/license/JacobHuang91/prompt-refiner)](https://github.com/JacobHuang91/prompt-refiner/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jacobhuang91.github.io/prompt-refiner/)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Xinghao91/prompt-refiner)

</div>

> 🧹 **A lightweight Python library for optimizing and cleaning LLM inputs.**
> **Save 10-20% on API costs** by removing invisible tokens, stripping HTML, and redacting PII.

<div align="center">

⭐ **If you find this useful, please star us on GitHub!** ⭐

</div>

---

### 🎯 Perfect for:

**RAG Applications** • **Chatbots** • **Document Processing** • **Production LLM Apps** • **Cost Optimization**

---

## Why use Prompt Refiner?

Stop paying for invisible tokens and dirty data.

| Feature | Before (Dirty Input) | After (Refined) |
| :--- | :--- | :--- |
| **HTML Cleaning** | `<div><b>Hello</b> world</div>` | `Hello world` |
| **Whitespace** | `User    input\n\n\n  here` | `User input here` |
| **PII Redaction** | `Call me at 555-0199` | `Call me at [PHONE]` |
| **Deduplication** | `Same text.\n\nSame text.\n\nDifferent.` | `Same text.\n\nDifferent.` |
| **Token Cost** | ❌ **150 Tokens** | ✅ **85 Tokens** (Saved 43%) |

### 📦 It's this easy:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace

cleaned = (StripHTML() | NormalizeWhitespace()).run(dirty_input)
```

### ✨ Key Features

- **🪶 Zero Dependencies** - Lightweight core with no external dependencies
- **⚡ Blazing Fast** - < 0.5ms per 1k tokens overhead, negligible impact on API latency
- **🔧 Modular Design** - 5 focused modules: Cleaner, Compressor, Scrubber, Analyzer, Packer
- **🚀 Production Ready** - Battle-tested operations with comprehensive test coverage
- **🎯 Type Safe** - Full type hints for better IDE support and fewer bugs
- **📦 Easy to Use** - Modern pipe operator syntax (`|`), compose operations like LEGO blocks

## Overview

Prompt Refiner helps you clean and optimize prompts before sending them to LLM APIs. By removing unnecessary whitespace, duplicate characters, and other inefficiencies, you can:

- Reduce token usage and API costs
- Improve prompt quality and consistency
- Process inputs more efficiently

## Status

This project is in early development. Features are being added iteratively.

## Installation

```bash
# Basic installation (lightweight, zero dependencies)
pip install llm-prompt-refiner

# With precise token counting (optional, installs tiktoken)
pip install llm-prompt-refiner[token]
```

### Installation Modes

- **Default (Lightweight)**: Zero dependencies, uses character-based token estimation
- **Precise Mode**: Installs `tiktoken` for accurate token counting with no safety buffer

To use precise mode, pass a `model` parameter:
```python
from prompt_refiner import CountTokens, ContextPacker

# Default: estimation mode (no model parameter)
counter = CountTokens()
packer = ContextPacker(max_tokens=1000)

# Opt-in: precise mode with tiktoken
counter = CountTokens(model="gpt-4")
packer = ContextPacker(max_tokens=1000, model="gpt-4")
```

## 🎉 What's New in v0.1.3

**New Architecture: Separated MessagesPacker and TextPacker**

We've refactored the packer architecture following the Single Responsibility Principle:

- **`MessagesPacker`**: Optimized for chat completion APIs (OpenAI, Anthropic)
  - Returns `List[Dict[str, str]]` directly - no wrapper needed!
  - Accurate ChatML overhead calculation (4 tokens per message)
  - 100% token budget utilization with precise mode

- **`TextPacker`**: Optimized for text completion APIs (Llama Base, GPT-3)
  - Returns `str` directly - no wrapper needed!
  - Multiple text formats: RAW, MARKDOWN, XML
  - Accurate delimiter overhead calculation

- **Better Type Safety**: Clear return types, no complex `PackedResult` wrapper
- **Better Accuracy**: Each packer only calculates its own overhead

```python
# MessagesPacker for Chat APIs (OpenAI, Anthropic)
from prompt_refiner import MessagesPacker, PRIORITY_SYSTEM, PRIORITY_USER

packer = MessagesPacker(max_tokens=1000)
packer.add("You are helpful.", role="system", priority=PRIORITY_SYSTEM)
packer.add("Hello!", role="user", priority=PRIORITY_USER)

messages = packer.pack()  # Returns List[Dict] directly!
# Use directly: openai.chat.completions.create(messages=messages)

# TextPacker for Completion APIs (Llama Base, GPT-3)
from prompt_refiner import TextPacker, TextFormat

packer = TextPacker(max_tokens=1000, text_format=TextFormat.MARKDOWN)
packer.add("You are helpful.", role="system", priority=PRIORITY_SYSTEM)
packer.add("Context doc", priority=PRIORITY_HIGH)

prompt = packer.pack()  # Returns str directly!
# Use directly: completion.create(prompt=prompt)
```


## Quick Start

```python
from prompt_refiner import StripHTML, NormalizeWhitespace, TruncateTokens

# ✨ The Pythonic "Pipe" Syntax (Recommended)
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | TruncateTokens(max_tokens=1000)
)

raw_input = "<div>  User input with <b>lots</b> of   spaces... </div>"
clean_prompt = pipeline.run(raw_input)
# Output: "User input with lots of spaces..."
```

<details>
<summary><b>Alternative: Fluent API</b></summary>

Prefer method chaining? Use the traditional fluent API:

```python
from prompt_refiner import Refiner, StripHTML, NormalizeWhitespace, TruncateTokens

pipeline = (
    Refiner()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(TruncateTokens(max_tokens=1000))
)

clean_prompt = pipeline.run(raw_input)
```

</details>

> 💡 **Why pipe operator?** More concise, Pythonic, and familiar to LangChain/LangGraph users.

## 📊 Proven Effectiveness

We benchmarked Prompt Refiner on 30 real-world test cases (SQuAD + RAG scenarios) to measure token reduction and response quality:

<div align="center">

| Strategy | Token Reduction | Quality (Cosine) | Judge Approval | Overall Equivalent |
|----------|----------------|------------------|----------------|--------------------|
| **Minimal** | 4.3% | 0.987 | 86.7% | 86.7% |
| **Standard** | 4.8% | 0.984 | 90.0% | 86.7% |
| **Aggressive** | **15.0%** | 0.964 | 80.0% | 66.7% |

</div>

**Key Insights:**
- **Aggressive strategy achieves 3x more savings (15%) vs Minimal** while maintaining 96.4% quality
- Individual RAG tests showed **17-74% token savings** with aggressive strategy
- **Deduplicate** (Standard) shows minimal gains on typical RAG contexts
- **TruncateTokens** (Aggressive) provides the largest cost reduction for long contexts
- **Trade-off**: More aggressive = more savings but slightly lower judge approval

**Example: RAG with duplicates**
- Minimal (HTML + Whitespace): 17% reduction
- Standard (+ Deduplicate): 31% reduction
- **Aggressive (+ Truncate 150 tokens): 49% reduction** 🎉

<div align="center">

![Token Reduction vs Quality](benchmark/custom/results/benchmark_results.png)

</div>

> 💰 **Cost Savings:** At scale (1M tokens/month), 15% reduction saves **~$54/month** on GPT-4 input tokens.
>
> 📖 **See full benchmark:** [benchmark/custom/README.md](benchmark/custom/README.md)

## ⚡ Performance & Latency

**"What's the latency overhead?"** - Negligible. Prompt Refiner adds **< 0.5ms per 1k tokens** of overhead.

<div align="center">

| Strategy | @ 1k tokens | @ 10k tokens | @ 50k tokens | Overhead per 1k tokens |
|----------|------------|--------------|--------------|------------------------|
| **Minimal** (HTML + Whitespace) | 0.05ms | 0.48ms | 2.39ms | **0.05ms** |
| **Standard** (+ Deduplicate) | 0.26ms | 2.47ms | 12.27ms | **0.25ms** |
| **Aggressive** (+ Truncate) | 0.26ms | 2.46ms | 12.38ms | **0.25ms** |

</div>

**Key Insights:**
- ⚡ **Minimal strategy**: Only 0.05ms per 1k tokens (faster than a network packet)
- 🎯 **Standard strategy**: 0.25ms per 1k tokens - adds ~2.5ms to a 10k token prompt
- 📊 **Context**: Network + LLM TTFT is typically 600ms+, refining adds < 0.5% overhead
- 🚀 **Individual operations** (HTML, whitespace) are < 0.5ms per 1k tokens

**Real-world impact:**
```
10k token RAG context refining: ~2.5ms overhead
Network latency: ~100ms
LLM Processing (TTFT): ~500ms+
Total overhead: < 0.5% of request time
```

> 🔬 **Run yourself:** `python benchmark/latency/benchmark.py` (no API keys needed)

## 🎮 Interactive Demo

Try prompt-refiner in your browser - no installation required!

<div align="center">

[![Open in Spaces](https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-sm.svg)](https://huggingface.co/spaces/Xinghao91/prompt-refiner)

**[🚀 Launch Interactive Demo →](https://huggingface.co/spaces/Xinghao91/prompt-refiner)**

</div>

Play with different strategies, see real-time token savings, and find the perfect configuration for your use case. Features:

- 🎯 6 preset examples (e-commerce, support tickets, docs, RAG, etc.)
- ⚡ Quick strategy presets (Minimal, Standard, Aggressive)
- 💰 Real-time cost savings calculator
- 🔧 All 7 operations configurable
- 📊 Visual metrics dashboard

## 5 Core Modules

Prompt Refiner is organized into 5 specialized modules:

### 1. **Cleaner** - Clean Dirty Data
- `StripHTML()` - Remove HTML tags, convert to Markdown
- `NormalizeWhitespace()` - Collapse excessive whitespace
- `FixUnicode()` - Remove zero-width spaces and problematic Unicode

### 2. **Compressor** - Reduce Size
- `TruncateTokens()` - Smart truncation with sentence boundaries
  - Strategies: `"head"`, `"tail"`, `"middle_out"`
- `Deduplicate()` - Remove similar content (great for RAG)

### 3. **Scrubber** - Security & Privacy
- `RedactPII()` - Automatically redact emails, phones, IPs, credit cards, URLs, SSNs

### 4. **Analyzer** - Show Value
- `CountTokens()` - Track token savings and optimization impact
  - **Estimation mode** (default): Character-based approximation (1 token ≈ 4 chars)
  - **Precise mode** (with tiktoken): Exact token counts using OpenAI's tokenizer

### 5. **Packer** - Context Budget Management (v0.1.3+)
- **`MessagesPacker()`** - For chat completion APIs (OpenAI, Anthropic)
  - Returns `List[Dict[str, str]]` ready for chat APIs
  - Accurate ChatML overhead (4 tokens per message)
  - Perfect for RAG chatbots and conversation history

- **`TextPacker()`** - For text completion APIs (Llama Base, GPT-3)
  - Returns `str` ready for completion APIs
  - Multiple text formats: `TextFormat.RAW`, `TextFormat.MARKDOWN`, `TextFormat.XML`
  - Accurate delimiter overhead calculation

- **Common features**:
  - Priority-based greedy selection: `PRIORITY_SYSTEM`, `PRIORITY_USER`, `PRIORITY_HIGH`, `PRIORITY_MEDIUM`, `PRIORITY_LOW`
  - JIT refinement with `refine_with` parameter
  - **Estimation mode**: 10% safety buffer (default)
  - **Precise mode**: 100% budget utilization (with tiktoken)

## Complete Example

```python
from prompt_refiner import (
    # Cleaner
    StripHTML, NormalizeWhitespace, FixUnicode,
    # Compressor
    Deduplicate, TruncateTokens,
    # Scrubber
    RedactPII,
    # Analyzer
    CountTokens,
    # Packer (v0.1.3+)
    MessagesPacker, PRIORITY_SYSTEM, PRIORITY_USER, PRIORITY_HIGH
)

# Example 1: Clean and optimize text
original_text = """<div>Your messy input here...</div>"""

counter = CountTokens(original_text=original_text)

# Build pipeline with all modules
pipeline = (
    StripHTML(to_markdown=True)
    | NormalizeWhitespace()
    | FixUnicode()
    | Deduplicate(similarity_threshold=0.85)
    | TruncateTokens(max_tokens=500, strategy="head")
    | RedactPII(redact_types={"email", "phone"})
)

result = pipeline.run(original_text)
counter.process(result)
print(counter.format_stats())

# Example 2: Pack messages for chat API
packer = MessagesPacker(max_tokens=1000)
packer.add("You are helpful.", role="system", priority=PRIORITY_SYSTEM)
packer.add("Context from RAG...", priority=PRIORITY_HIGH, refine_with=StripHTML())
packer.add("User question", role="user", priority=PRIORITY_USER)

messages = packer.pack()  # Returns List[Dict]
# Use with: openai.chat.completions.create(messages=messages)
```

## Examples

Check out the [`examples/`](examples/) folder for detailed examples organized by module:
- `cleaner/` - HTML cleaning, whitespace normalization, Unicode fixing
- `compressor/` - Smart truncation, deduplication
- `scrubber/` - PII redaction
- `analyzer/` - Token counting and cost savings
- `packer/` - Context budget management with priorities for RAG
- `all_modules_demo.py` - Complete demonstration

## Development

This project uses `uv` for dependency management and `make` for common tasks.

```bash
# Install dependencies
make install

# Run tests
make test

# Format code
make format
```

## License

MIT