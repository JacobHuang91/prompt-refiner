# Project Archived

**Date**: April 2026  
**Last Version**: v0.2.3

---

## Why Archived

Token optimization for LLM inputs is no longer a priority because:

### 1. Token Costs Dropped Dramatically
- GPT-4: $30/M tokens (2023) → $2.50/M tokens (2026) = **12x cheaper**
- GPT-4o-mini: $0.15/M tokens = **200x cheaper than original GPT-4**

### 2. Context Windows Expanded Massively  
- GPT-4: 8K → 128K tokens = **16x larger**
- Claude 3: 200K tokens
- Gemini 1.5: 1M tokens

### 3. Better Alternatives Exist
- **Caching** (GPTCache, Anthropic prompt caching): 90%+ cost reduction vs. our 5-15%
- **ML-based compression** (LLMLingua): 20x compression vs. our 1.15x
- **Model routing** (Portkey, Merge): Use cheap models for simple tasks

### 4. Rule-Based Optimization Has Limits
This library achieves 5-15% token reduction through HTML cleaning, whitespace normalization, and deduplication. That's near the ceiling for rule-based approaches without sacrificing quality. Modern alternatives deliver better results.

---

## When This Library Is Still Useful

The code still works and is useful for:
- ✅ **Web scraping** - Clean heavy HTML content
- ✅ **PII redaction** - Remove sensitive data before sending to LLMs  
- ✅ **High-volume production** - Small savings add up at scale
- ✅ **Tool-heavy agents** - Schema compression (57% reduction)

---

## Thank You

Thanks to everyone who used, starred, or contributed to this project. The library successfully achieved its technical goals (fast, reliable, well-tested), but the problem space evolved.

The code remains available and functional. Fork it if you need it!

---

**Repository**: https://github.com/JacobHuang91/prompt-refiner  
**Package**: `pip install llm-prompt-refiner` (still works)  
**Status**: No longer maintained (no bug fixes or new features)
