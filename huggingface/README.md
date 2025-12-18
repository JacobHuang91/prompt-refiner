---
title: Prompt Refiner Demo
emoji: 🧹
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---

# 🧹 Prompt Refiner - Interactive Demo

Live demonstration of [prompt-refiner](https://github.com/JacobHuang91/prompt-refiner) library capabilities.

**Stop paying for invisible tokens.** Optimize your LLM inputs with benchmark-tested strategies to save 5-70% on API costs.

## ✨ Features

### 📝 Tab 1: Text Optimization
- **3 Preset Strategies** - Minimal, Standard, Aggressive (benchmark-tested)
- **Real-time Token Savings** - See exactly how many tokens and dollars you save
- **3 Real-world Examples** - E-commerce RAG, support tickets, technical docs
- **Visual Metrics** - Cost analysis and performance tracking
- **Proven Results** - 4-15% token reduction, 96-99% quality maintained

### 🔧 Tab 2: Function Calling Optimization
- **Schema Compression** - Compress OpenAI/Anthropic tool schemas by 57% on average
- **100% Lossless** - Protocol fields preserved, 100% callable validation
- **3 Schema Examples** - Simple, complex, and very verbose APIs
- **Cost Calculator** - See savings for small, medium, and large AI agents
- **Production Ready** - Tested on 20 real-world APIs

## 🚀 Quick Start

### Text Optimization
1. **Select Tab 1** - Text Optimization
2. **Choose an example** - E-commerce, support ticket, or docs
3. **Pick a strategy** - Minimal, Standard, or Aggressive
4. **See results** - Real-time token counting and cost savings

### Function Calling Compression
1. **Select Tab 2** - Function Calling
2. **Choose a schema** - Weather API, Stripe Payment, or HubSpot
3. **View compression** - See before/after token counts
4. **Calculate ROI** - Cost savings for your agent workload

## 📦 Installation

Try it live here, then install for your project:

```bash
pip install llm-prompt-refiner
```

## 💻 Example Usage

### Text Optimization with Preset Strategies
```python
from prompt_refiner import StandardStrategy

# Use benchmark-tested preset strategies
strategy = StandardStrategy()
cleaned = strategy.run(dirty_text)
```

### Function Calling Schema Compression
```python
from prompt_refiner import SchemaCompressor

# Compress tool schema (57% average reduction)
compressor = SchemaCompressor()
compressed_schema = compressor.process(tool_schema)
```

### Smart Context Packing
```python
from prompt_refiner import MessagesPacker

# Pack messages with automatic refining
packer = MessagesPacker(
    system="You are a helpful assistant.",
    context=(["<div>Doc 1</div>", "Doc 2"], StripHTML() | NormalizeWhitespace()),
    query="Search for Python books"
)
messages = packer.pack()
```

## 🔗 Links

- 📖 [Documentation](https://jacobhuang91.github.io/prompt-refiner/)
- 💻 [GitHub Repository](https://github.com/JacobHuang91/prompt-refiner)
- 📦 [PyPI Package](https://pypi.org/project/llm-prompt-refiner/)
- 📊 [Benchmark Results](https://github.com/JacobHuang91/prompt-refiner/tree/main/benchmark)

## 📊 Benchmark Results

**Function Calling (Primary Focus):**
- **57% average token reduction** on tool schemas
- **100% callable validation** with OpenAI
- Tested on **20 real-world APIs**

**Text Optimization:**
- **4-15% token reduction** on RAG contexts
- **96-99% quality maintained** (cosine similarity + LLM judge)
- Tested on **30 real-world test cases**

**Cost Savings:**
- Medium agent (10 tools, 500 calls/day): **~$128/month saved**
- RAG app (1M tokens/month): **~$54/month saved**

## 🛠️ What's Inside

### Preset Strategies
- **MinimalStrategy** - Light cleaning (4.3% reduction, 98.7% quality)
- **StandardStrategy** - Balanced optimization (4.8% reduction, 98.4% quality)
- **AggressiveStrategy** - Maximum compression (15.0% reduction, 96.4% quality)

### Tools Module
- **SchemaCompressor** - Compress OpenAI/Anthropic tool schemas
- **ResponseCompressor** - Compress verbose API/tool responses

### Core Operations
- **Cleaner** - Strip HTML, normalize whitespace, fix Unicode
- **Compressor** - Deduplicate content, truncate to token limits
- **Scrubber** - Redact PII (email, phone, SSN, credit cards)
- **Packer** - Smart context management with priority-based ordering

---

Made with ❤️ by [Xinghao Huang](https://github.com/JacobHuang91)
