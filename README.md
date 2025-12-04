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

> 🚀 **Lightweight Python library for building production LLM applications with smart context management and automatic token optimization.**
> **Save 10-20% on API costs** while fitting RAG docs, chat history, and prompts into your token budget.

---

### 🎯 Perfect for:

**RAG Applications** • **Chatbots** • **Document Processing** • **Production LLM Apps** • **Cost Optimization**

---

## Why use Prompt Refiner?

Build production RAG applications with automatic token optimization and smart context management. Here's a complete example showing a chatbot that saves tokens and fits within budget:

```python
from prompt_refiner import MessagesPacker, ROLE_SYSTEM, ROLE_QUERY, ROLE_CONTEXT, ROLE_USER, ROLE_ASSISTANT, StripHTML, NormalizeWhitespace, Deduplicate, RedactPII
from openai import OpenAI

# Set up MessagesPacker with token budget
packer = MessagesPacker(max_tokens=1000)
packer.add("You are a helpful AI assistant.", role=ROLE_SYSTEM)

# Add user query with composed cleaning pipeline (pipe operator |)
packer.add(
    "How do I    install   your library? How do I install your library? My email is john@example.com",
    role=ROLE_QUERY,
    refine_with=StripHTML() | NormalizeWhitespace() | Deduplicate(0.8) | RedactPII({"email"})
)

# Add RAG documents with JIT cleaning
rag_docs = [
    "<div><h2>Docs</h2><p>Our    AI   helps developers...</p></div>",
    "<article><p>Features:    context   management...</p></article>",
]
for doc in rag_docs:
    packer.add(doc, role=ROLE_CONTEXT, refine_with=[StripHTML(), NormalizeWhitespace()])

# Add conversation history (dropped first if over budget)
packer.add("What can you do?", role=ROLE_USER)
packer.add("I help with documentation.", role=ROLE_ASSISTANT)

# Pack and send to OpenAI
messages = packer.pack()  # Saved ~45 tokens (18%)!
response = OpenAI().chat.completions.create(model="gpt-4", messages=messages)
print(response.choices[0].message.content)
```

**This example demonstrates:**

- **Compose operations** with `|` - Chain multiple cleaners into a pipeline
- **Save 10-20% tokens** - Remove HTML, whitespace, duplicates, and redact PII automatically
- **Stay within budget** - MessagesPacker fits everything into 1000 tokens using priority-based selection
- **JIT cleaning** - Clean content on-the-fly with `refine_with` parameter
- **Production ready** - Output goes directly to OpenAI without extra steps

### ✨ Key Features

| Module | Description | Components |
|--------|-------------|------------|
| **Cleaner** | Remove noise and save tokens | `StripHTML()`, `NormalizeWhitespace()`, `FixUnicode()`, `JsonCleaner()` |
| **Compressor** | Reduce size aggressively | `TruncateTokens()`, `Deduplicate()` |
| **Scrubber** | Protect sensitive data | `RedactPII()` |
| **Packer** | Fit content within token budgets | `MessagesPacker` (chat APIs), `TextPacker` (completion APIs) |
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
- **`packer/`** - Context budget management with OpenAI integration
- **`analyzer/`** - Token counting and cost savings tracking
- **`custom_operation.py`** - Build your own custom operations

> 📖 **Full documentation:** [examples/README.md](examples/README.md)

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

## Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=JacobHuang91/prompt-refiner&type=Date)](https://star-history.com/#JacobHuang91/prompt-refiner&Date)

</div>

## License

MIT