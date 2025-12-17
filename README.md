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

> 🚀 **Lightweight Python library for AI Agents, RAG apps, and chatbots with smart context management and automatic token optimization.**
> **Save 5-70% on API costs** - 57% average reduction on function calling, 5-15% on RAG contexts.

---

### 🎯 Perfect for:

**RAG Applications** • **AI Agents** • **Chatbots** • **Document Processing** • **Cost Optimization**

---

## Why use Prompt Refiner?

Build AI agents, RAG applications, and chatbots with automatic token optimization and smart context management. Here's a complete example (see [`examples/quickstart.py`](examples/quickstart.py) for full code):

```python
from prompt_refiner import MessagesPacker, SchemaCompressor, ResponseCompressor, StripHTML, NormalizeWhitespace

# 1. Pack messages (automatic refining with default strategies)
packer = MessagesPacker(
    track_tokens=True,
    system="<p>You are a helpful AI assistant.</p>",
    context=(["<div>Installation Guide...</div>"], StripHTML() | NormalizeWhitespace()),
    query="<span>Search for Python books.</span>"
)
messages = packer.pack()

# 2. Compress tool schema
tool_schema = pydantic_function_tool(SearchBooksInput, name="search_books")
compressed_schema = SchemaCompressor().process(tool_schema)

# 3. Call LLM with compressed schema
response = client.chat.completions.create(
    model="gpt-4o-mini", messages=messages, tools=[compressed_schema]
)

# 4. Compress tool response
tool_response = search_books(**json.loads(tool_call.function.arguments))
compressed_response = ResponseCompressor().process(tool_response)
```

**Default refining strategies:**
- `system`/`query`: MinimalStrategy (StripHTML + NormalizeWhitespace)
- `context`/`history`: StandardStrategy (StripHTML + NormalizeWhitespace + Deduplicate)
- Override with tuple: `context=(docs, StripHTML() | NormalizeWhitespace())`

> 💡 Run `python examples/quickstart.py` to see the complete workflow with real OpenAI API verification.

**Key benefits:**

- **Default strategies** - Automatic refining (MinimalStrategy for system/query, StandardStrategy for context/history)
- **Tool schema compression** - Save **10-70% tokens** on AI agent function definitions (avg: 57%)
- **Tool response compression** - Save 30-70% tokens on agent tool outputs
- **Compose operations** with `|` - Chain multiple cleaners into a pipeline
- **Save 5-15% tokens** on RAG contexts - Remove HTML, whitespace, duplicates automatically
- **All items included** - No token budget limits, let LLM APIs handle final truncation
- **Track savings** - Measure token optimization impact with built-in savings tracking
- **Production ready** - Output goes directly to OpenAI without extra steps

### ✨ Key Features

| Module | Description | Components |
|--------|-------------|------------|
| **Cleaner** | Remove noise and save tokens | `StripHTML()`, `NormalizeWhitespace()`, `FixUnicode()`, `JsonCleaner()` |
| **Compressor** | Reduce size aggressively | `TruncateTokens()`, `Deduplicate()` |
| **Scrubber** | Protect sensitive data | `RedactPII()` |
| **Tools** | Optimize AI agent function calling (tool schemas & responses) | `SchemaCompressor()`, `ResponseCompressor()` |
| **Packer** | Smart message composition with priority-based ordering | `MessagesPacker` (chat APIs), `TextPacker` (completion APIs) |
| **Strategy** | Benchmark-tested presets for quick setup | `MinimalStrategy`, `StandardStrategy`, `AggressiveStrategy` |

## Installation

```bash
# Basic installation (lightweight, zero dependencies)
pip install llm-prompt-refiner

# With precise token counting (optional, installs tiktoken)
pip install llm-prompt-refiner[token]
```

## Examples

Check out the [`examples/`](examples/) folder for detailed examples:

- **`strategy/`** - Preset strategies (Minimal, Standard, Aggressive) with benchmark results
- **`cleaner/`** - HTML cleaning, JSON compression, whitespace normalization, Unicode fixing
- **`compressor/`** - Smart truncation, deduplication
- **`scrubber/`** - PII redaction (emails, phones, credit cards, etc.)
- **`tools/`** - Tool/API output cleaning for agent systems
- **`packer/`** - Context budget management with OpenAI integration
- **`analyzer/`** - Token counting and cost savings tracking

> 📖 **Full documentation:** [examples/README.md](examples/README.md)

## 📊 Proven Effectiveness

Prompt Refiner has been rigorously tested across **3 comprehensive benchmark suites** covering function calling, RAG applications, and performance. Here's what the data shows:

### 🎯 Function Calling Benchmark: 57% Average Token Reduction

**SchemaCompressor** was tested on **20 real-world API schemas** from Stripe, Salesforce, HubSpot, Slack, OpenAI, Anthropic, and more:

<div align="center">

| Category | Schemas | Avg Reduction | Top Performer |
|----------|---------|---------------|---------------|
| **Very Verbose** (Enterprise APIs) | 11 | **67.4%** | HubSpot: 73.2% |
| **Complex** (Rich APIs) | 6 | **61.7%** | Slack: 70.8% |
| **Medium** (Standard APIs) | 2 | **13.1%** | Weather: 20.1% |
| **Simple** (Minimal APIs) | 1 | **0.0%** | Calculator (already minimal) |
| **Overall Average** | **20** | **56.9%** | — |

</div>

**Key Highlights:**
- ✨ **56.9% average reduction** across all schemas (15,342 tokens saved)
- 🔒 **100% lossless compression** - all protocol fields preserved (name, type, required, enum)
- ✅ **100% callable (20/20 validated)** - all compressed schemas work correctly with OpenAI function calling
- 🏢 **Enterprise APIs see 70%+ reduction** - HubSpot, Salesforce, OpenAI File Search
- 📊 **Real-world schemas** from production APIs, not synthetic examples
- ⚡ **Zero API cost** - local processing with tiktoken

<div align="center">

![Token Reduction by Category](benchmark/function_calling/results/plots/reduction_by_category.png)
*SchemaCompressor achieves 60%+ reduction on complex APIs*

![Cost Savings Projection](benchmark/function_calling/results/plots/cost_savings.png)
*Estimated monthly savings for different agent sizes (GPT-4 pricing)*

</div>

**✅ Functional Validation:**

We tested all 20 compressed schemas with real OpenAI function calling to prove they work correctly:

- **100% callable (20/20)**: Every compressed schema successfully triggers function calls
- **60% identical (12/20)**: Majority produce exactly the same arguments as original schemas
- **40% different but valid (8/20)**: Compressed descriptions may influence LLM's choice among valid options (e.g., default values, placeholders)
- **Bottom line**: Compression is safe for production - schemas remain functionally correct

> 💰 **Cost Savings Example:** A medium agent (10 tools, 500 calls/day) saves **$541/month** with SchemaCompressor.
>
> 📖 **See full benchmark:** [benchmark/README.md#function-calling-benchmark](benchmark/README.md#function-calling-benchmark)

---

### 📚 RAG & Text Optimization Benchmark: 5-15% Token Reduction

Tested on **30 real-world test cases** (SQuAD + RAG scenarios) to measure token reduction and quality preservation:

<div align="center">

| Strategy | Token Reduction | Quality (Cosine) | Judge Approval |
|----------|----------------|------------------|----------------|
| **Minimal** | 4.3% | 0.987 | 86.7% |
| **Standard** | 4.8% | 0.984 | 90.0% |
| **Aggressive** | **15.0%** | 0.964 | 80.0% |

</div>

**Key Insights:**
- ✅ **Standard strategy**: 5% reduction with 98.4% cosine similarity and 90% judge approval
- 🚀 **Aggressive strategy**: 15% reduction while maintaining 96.4% semantic quality
- 📊 **Individual tests**: Up to 74% token savings on contexts with HTML and duplicates

> 💰 **Cost Savings:** At 1M tokens/month, 15% reduction saves **$54/month** on GPT-4 input tokens.
>
> 📖 **See full benchmark:** [benchmark/README.md#rag-quality-benchmark](benchmark/README.md#rag-quality-benchmark)

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

## Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=JacobHuang91/prompt-refiner&type=Date)](https://star-history.com/#JacobHuang91/prompt-refiner&Date)

</div>

## License

MIT