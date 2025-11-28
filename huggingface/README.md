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

Stop paying for invisible tokens. Optimize your LLM inputs to save costs, improve context usage, and enhance security.

## ✨ Features

- 🎯 **Interactive Playground** - Experiment with different optimization strategies
- 💰 **Real-time Token Savings** - See exactly how many tokens and dollars you save
- 🔧 **Configurable Operations** - Toggle between 7 different operations
- 📊 **Visual Metrics** - Cost analysis and performance tracking
- 🎭 **Preset Examples** - 6 real-world scenarios (e-commerce, support, docs, RAG, etc.)
- ⚡ **Quick Presets** - Minimal, Standard, Aggressive, or Custom strategies

## 🚀 Quick Start

1. **Choose a preset example** from the dropdown (or enter your own text)
2. **Select a strategy** in the sidebar (Minimal, Standard, Aggressive, or Custom)
3. **Configure operations** to match your use case
4. **See results** with real-time token counting and cost savings

## 📦 Installation

Try it live here, then install for your project:

```bash
pip install llm-prompt-refiner
```

## 💻 Example Usage

```python
from prompt_refiner import (
    StripHTML,
    NormalizeWhitespace,
    TruncateTokens
)

# Use pipe operator to chain operations
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | TruncateTokens(max_tokens=1000)
)

cleaned = pipeline.run(dirty_text)
```

## 🔗 Links

- 📖 [Documentation](https://jacobhuang91.github.io/prompt-refiner/)
- 💻 [GitHub Repository](https://github.com/JacobHuang91/prompt-refiner)
- 📦 [PyPI Package](https://pypi.org/project/llm-prompt-refiner/)

## 📊 Proven Effectiveness

Benchmarked on 30 real-world test cases:
- **4-15% token reduction** on average
- **96-99% quality maintained** (verified)
- **Up to ~$54/month saved** at scale (1M tokens/month, GPT-4)

## 🛠️ Operations Available

### 🧼 Cleaner
- Strip HTML tags
- Normalize whitespace
- Fix Unicode issues

### 🗜️ Compressor
- Deduplicate similar content
- Truncate to token limits

### 🔒 Scrubber
- Redact PII (email, phone, IP, credit cards, SSN, URLs)

### 📊 Analyzer
- Count tokens
- Calculate cost savings

---

Made with ❤️ by [Xinghao Huang](https://github.com/JacobHuang91)
