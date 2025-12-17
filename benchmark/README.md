# Prompt Refiner Benchmarks

This directory contains comprehensive benchmarks validating prompt-refiner's effectiveness across four critical dimensions: **function calling optimization**, **context packing**, **RAG quality preservation**, and **performance overhead**.

## 📊 Benchmark Overview

| Benchmark | What It Tests | Key Results | Runtime | Cost |
|-----------|--------------|-------------|---------|------|
| **[Function Calling](#function-calling-benchmark)** ⭐ | Tool schema & response compression | 56.9% avg schema reduction<br>25.8% avg response reduction<br>100% callable (20/20 validated) | < 2 min | $0 (+$2-3 for validation) |
| **[Packer](#packer-benchmark)** | MessagesPacker & TextPacker functionality | Token tracking accuracy<br>Priority ordering<br>Default strategies | < 1 min | $0 |
| **[RAG Quality](#rag-quality-benchmark)** | Text optimization with quality preservation | 5-15% reduction<br>86-90% quality | ~ 5 min | $2-5 |
| **[Latency](#latency-benchmark)** | Processing overhead measurement | < 0.5ms per 1k tokens | ~ 1 min | $0 |

---

## Function Calling Benchmark

Tests SchemaCompressor and ResponseCompressor on 20 real-world API tools from Stripe, Salesforce, HubSpot, Slack, OpenAI, Anthropic, and popular APIs.

### Results Summary

#### Schema Compression
- **Average reduction: 56.9%** (median: 59.1%)
- **Total tokens saved: 15,342** across 20 schemas
- **100% protocol field preservation** (lossless compression)

**By Category:**
- **Very Verbose** (Enterprise APIs): 67.4% reduction
- **Complex** (Rich APIs): 61.7% reduction
- **Medium** (Standard APIs): 13.1% reduction
- **Simple** (Basic APIs): 0% reduction

**Top Performers:**
1. SendGrid Email: 74.0% (1540 → 400 tokens)
2. HubSpot Contact: 73.5% (1426 → 378 tokens)
3. Salesforce Account: 72.5% (1327 → 365 tokens)

#### Response Compression
- **Average reduction: 25.8%** (median: 24.0%)
- **Total tokens saved: 5,172** across 20 responses
- **All quality checks passed**: droppable fields removed, data preserved

**By Category:**
- **Complex** (500-1000 tokens): 31.4% reduction
- **Very Verbose** (1000+ tokens): 20.3% reduction

**Top Performers:**
1. Stripe Payment: 52.7% (923 → 437 tokens)
2. Slack Message: 34.9% (608 → 396 tokens)
3. OpenAI Calculator: 33.4% (521 → 347 tokens)

### Running the Benchmark

```bash
cd benchmark/function_calling

# Schema compression
python benchmark_schemas.py

# Response compression
python benchmark_responses.py

# Generate visualizations
python visualize_results.py
```

### What Gets Compressed

**SchemaCompressor (Lossless):**
- ✅ Optimizes: `description` fields, verbose docs, redundant phrases
- ❌ Never modifies: `name`, `type`, `required`, `enum`, `default`, JSON structure

**ResponseCompressor:**
- ✅ Removes: debug/trace/logs fields (exact matches: debug, trace, logs, stack, stacktrace)
- ✅ Truncates: long strings (>512 chars), long lists (>16 items)
- ✅ Drops: null values, empty containers
- ❌ Preserves: essential data fields, JSON structure, data types

### Functional Equivalence Validation

**Validates that compressed schemas work correctly with real OpenAI API calls.**

Tested **all 20 schemas** across all complexity levels with real function calling:

**Results Summary:**

| Category | Schemas | Identical Calls | Different Args (Valid) | Callable Rate |
|----------|---------|-----------------|----------------------|---------------|
| **Simple** | 1 | 1 (100%) | 0 | 100% |
| **Medium** | 4 | 4 (100%) | 0 | 100% |
| **Complex** | 6 | 4 (67%) | 2 (33%) | 100% |
| **Very Verbose** | 9 | 3 (33%) | 6 (67%) | 100% |
| **Overall** | **20** | **12 (60%)** | **8 (40%)** | **100%** |

**Key Findings:**
- ✅ **100% callable (20/20)**: All compressed schemas successfully trigger function calls
- ✅ **100% structurally valid**: Function names, types, required fields all preserved
- ✅ **60% identical (12/20)**: Majority produce exactly the same function call
- ⚠️ **40% different but valid (8/20)**: Compressed descriptions influence LLM choices
  - Different default values chosen (num_results: 10 → 5, time_range: past_month → any)
  - Different placeholder values (database: 'production' → 'your_database_name')
  - Different optional fields populated (location: 'Zoom' → 'Conference Room A')
  - **All differences use valid enum/type values** - schemas remain functionally correct

**Examples of Different But Valid:**
- `anthropic_web_search`: num_results changed from 10 to 5 (both valid integers)
- `sendgrid_email`: from.name changed from "Support Team" to "Example Team" (both valid strings)
- `openai_file_search`: search_path changed from './' to '.' (both valid paths)

**Bottom Line:** Compression doesn't break schemas - it may influence LLM's choice among valid options.

**Run the test yourself:**
```bash
cd benchmark/function_calling
python test_functional_equivalence.py
```

**Cost**: ~$2-3 (40 API calls with gpt-4o-mini: 20 original + 20 compressed)

### Cost Savings Example

**Medium Agent** (10 tools, 500 calls/day):
- Before: 10 tools × 800 tokens × $0.003/1k = $0.024/call
- After (57% reduction): 10 tools × 344 tokens = $0.010/call
- **Monthly savings**: $210 (58% cost reduction)

---

## Packer Benchmark

Validates MessagesPacker and TextPacker functionality to ensure correct behavior in production RAG and chatbot applications.

### Results Summary

Based on 5 comprehensive test cases:

| Test | What It Validates | Result |
|------|------------------|--------|
| **Token Tracking Accuracy** | Packer's token savings calculation accuracy | ✅ Within 40% (accounts for ChatML overhead) |
| **Priority Ordering** | System > Query > Context > History ordering | ✅ Correct ordering maintained |
| **Default Refining Strategies** | Automatic HTML/whitespace/deduplication | ✅ All strategies applied correctly |
| **TextPacker MARKDOWN** | Grouped sections for base models | ✅ Correct format and ordering |
| **Real-World RAG** | Production scenario with messy HTML/duplicates | ✅ 59.9% token reduction |

### Key Findings

1. ✅ **Token Tracking Works**: Packer tracks content tokens accurately (within 40% including ChatML overhead)
2. ✅ **Priority System Reliable**: System messages always first, query always last, proper grouping
3. ✅ **Default Strategies Effective**: Automatic HTML removal, whitespace normalization, and deduplication work as expected
4. ✅ **Production-Ready**: Real-world RAG scenario shows 59.9% token reduction with all components properly handled
5. ✅ **Format Support**: TextPacker correctly generates MARKDOWN format with grouped sections

### Test Details

#### Test 1: Token Tracking Accuracy
Validates that token savings tracking is reasonably accurate:
- **Raw tokens**: Tracked 41 vs Actual 59 (30.5% difference)
- **Refined tokens**: Tracked 27 vs Actual 43 (37.2% difference)
- **Note**: Difference expected because packer tracks content tokens only, not ChatML overhead (~4 tokens per message)

#### Test 2: Priority Ordering
Validates correct message ordering:
- ✅ System message appears first
- ✅ Query appears in last user message
- ✅ History messages present and correctly positioned
- ✅ All 6 messages in correct priority order

#### Test 3: Default Refining Strategies
Validates automatic refinement:
- ✅ System/query: MinimalStrategy (HTML removed, whitespace normalized)
- ✅ Context: StandardStrategy (HTML removed, whitespace normalized, duplicates removed)
- ✅ Deduplication working (duplicate context items reduced to 1)

#### Test 4: TextPacker MARKDOWN Format
Validates text formatting for base models:
- ✅ Correct sections: `## INSTRUCTIONS`, `## CONTEXT`, `## INPUT`
- ✅ Sections in correct order
- ✅ Token savings tracked (0.0% on clean input)

#### Test 5: Real-World RAG Scenario
Validates production-ready RAG application:
- ✅ All components present (system, context, history, query)
- ✅ HTML cleaned from messy web-scraped content
- ✅ Duplicate content removed
- ✅ **59.9% token reduction** (237 → 95 tokens)

### Running the Benchmark

```bash
cd benchmark/packer
python benchmark.py
```

**Cost**: $0 (local processing only, no API calls)
**Duration**: < 1 minute
**Output**: CSV results saved to `results/packer_benchmark_results.csv`

### What This Validates

**MessagesPacker**:
- Token tracking accuracy (content tokens)
- Priority-based ordering (system > query > context > history)
- Default refining strategies (MinimalStrategy for system/query, StandardStrategy for context)
- Real-world RAG scenarios with HTML and duplicates

**TextPacker**:
- MARKDOWN format generation
- Grouped sections (INSTRUCTIONS, CONTEXT, INPUT)
- Token savings tracking

---

## RAG Quality Benchmark

A/B testing comparing raw vs refined prompts on 30 real-world scenarios (15 SQuAD + 15 RAG).

### Results Summary

Based on 30 test cases using gpt-4o-mini:

| Strategy   | Token Reduction | Quality (Cosine) | Judge Approval | Overall Equivalent |
|------------|----------------|------------------|----------------|-------------------|
| Minimal    | 4.3%           | 0.987            | 86.7%          | 86.7%             |
| Standard   | 4.8%           | 0.984            | 90.0%          | 86.7%             |
| Aggressive | 15.0%          | 0.964            | 80.0%          | 66.7%             |

### Key Findings

- **Aggressive strategy: 3× more savings** (15% vs 4.3%) while maintaining 96.4% quality
- RAG scenarios with duplicates showed **17-74% savings** per test
- **Trade-off**: Aggressive saves more but has lower judge approval (80% vs 90%)

**Strategy Differentiation:**
- rag_001: Minimal 17% → Standard 31% → **Aggressive 49%**
- rag_005: Minimal 19% → Standard 19% → **Aggressive 48%**
- rag_015: Minimal 0% → Standard 0% → **Aggressive 74%** (long context truncation)

### Test Dataset

**SQuAD Samples (15 cases):**
- Question-answer pairs with context
- Topics: history, science, geography, literature, technology

**RAG Scenarios (15 cases):**
- Realistic retrieval-augmented generation use cases
- Domains: e-commerce, documentation, customer support, code search, recipes
- Context includes messy HTML, extra whitespace, and duplicate content

### Refining Strategies

#### Minimal
```python
StripHTML() | NormalizeWhitespace()
```
- Best for: Clean inputs needing minor cleanup

#### Standard
```python
StripHTML() | NormalizeWhitespace() | Deduplicate(similarity_threshold=0.8, granularity="sentence")
```
- Best for: RAG contexts with some duplication

#### Aggressive
```python
StripHTML() | NormalizeWhitespace() | Deduplicate(similarity_threshold=0.7, granularity="sentence") | TruncateTokens(max_tokens=150)
```
- Best for: Very long contexts with lots of duplication

### Running the Benchmark

```bash
cd benchmark/rag_quality

# Set up API key
cp ../.env.example ../.env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# Run full benchmark
python benchmark.py

# Or with options
python benchmark.py --model gpt-4o --strategies minimal standard --n-squad 5 --n-rag 5
```

### Quality Metrics

**Cosine Similarity:**
- 0.95+ = Excellent (nearly identical semantic meaning)
- 0.90-0.95 = Good (very similar)
- 0.85-0.90 = Acceptable (similar enough)
- <0.85 = Poor (significant difference)

**Judge Approval:**
- 90%+ = Excellent
- 80-90% = Good
- 70-80% = Acceptable
- <70% = Poor

**Overall Equivalent:**
- Requires BOTH metrics to pass
- Most conservative measure
- Use this for production decisions

### Output Files

Results saved to `rag_quality/results/`:
- `BENCHMARK_RESULTS.md` - Human-readable summary with visualizations
- `benchmark_results.csv` - Full detailed results
- `benchmark_results.png` - Token reduction vs quality scatter plot
- `token_savings_dist.png` - Distribution of savings by strategy
- `strategy_comparison.png` - Bar chart comparing all metrics

---

## Latency Benchmark

Measures processing overhead of Prompt Refiner operations to validate negligible performance impact.

### Results Summary

For a typical 10k token context:
- **Minimal strategy**: 0.48ms (0.05ms per 1k tokens)
- **Standard strategy**: 2.47ms (0.25ms per 1k tokens)
- **Aggressive strategy**: 2.46ms (0.25ms per 1k tokens)

**Real-World Context:**
- Refining overhead: ~2.5ms
- Network latency: ~100ms
- LLM TTFT: ~500ms+
- **Total overhead: < 0.5% of request time**

### Individual Operations

Fast operations (< 0.1ms per 1k tokens):
- `StripHTML`: 0.04ms per 1k tokens
- `NormalizeWhitespace`: 0.01ms per 1k tokens
- `Deduplicate`: < 0.01ms per 1k tokens
- `TruncateTokens`: 0.08ms per 1k tokens

Moderate operations:
- `FixUnicode`: 0.56ms per 1k tokens

### Scaling Behavior

All strategies scale linearly (O(n)) with input size:

| Strategy | 1k tokens | 10k tokens | 50k tokens |
|----------|-----------|------------|------------|
| Minimal | 0.05ms | 0.48ms | 2.39ms |
| Standard | 0.26ms | 2.47ms | 12.27ms |
| Aggressive | 0.26ms | 2.46ms | 12.38ms |

### Running the Benchmark

```bash
cd benchmark/latency
python benchmark.py
```

No dependencies or API keys needed. Takes about 30-60 seconds.

### Sample Output

```
================================================================================
PROMPT REFINER - LATENCY BENCHMARK
================================================================================

📊 INDIVIDUAL OPERATIONS
--------------------------------------------------------------------------------

Test data: ~10,000 tokens

  StripHTML           :   0.38ms avg  |  0.04ms per 1k tokens
  NormalizeWhitespace :   0.12ms avg  |  0.01ms per 1k tokens
  FixUnicode          :   5.58ms avg  |  0.56ms per 1k tokens
  Deduplicate         :   0.04ms avg  |  0.00ms per 1k tokens
  TruncateTokens      :   0.81ms avg  |  0.08ms per 1k tokens

================================================================================
📦 REFINING STRATEGIES
--------------------------------------------------------------------------------

  Minimal (HTML + Whitespace)   :  0.48ms avg  |  0.05ms per 1k tokens
  Standard (+ Deduplication)    :  2.47ms avg  |  0.25ms per 1k tokens
  Aggressive (+ Truncate)       :  2.46ms avg  |  0.25ms per 1k tokens
```

### When to Optimize Latency

Consider refining latency only if:
- Processing > 100k tokens in a tight loop
- Total pipeline budget is < 10ms
- Real-time client-side processing on mobile devices

For 99% of use cases, the token cost savings (5-57%) far outweigh the < 0.5% latency overhead.

---

## 🚀 Quick Start

### Prerequisites

1. **Install dependencies:**
   ```bash
   cd /path/to/prompt-refiner
   uv sync --group dev
   ```

2. **Set up API key** (for RAG quality benchmark only):
   ```bash
   cd benchmark
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

### Run All Benchmarks

```bash
# Function calling (no API key, ~2 min, $0)
cd benchmark/function_calling
python benchmark_schemas.py
python benchmark_responses.py
python visualize_results.py

# Optional: Validate all 20 compressed schemas work with OpenAI (requires API key, ~2 min, ~$2-3)
python test_functional_equivalence.py

# Packer (no API key, ~1 min, $0)
cd benchmark/packer
python benchmark.py

# RAG quality (requires API key, ~5 min, ~$3)
cd benchmark/rag_quality
python benchmark.py

# Latency (no API key, ~1 min, $0)
cd benchmark/latency
python benchmark.py
```

---

## 📁 Directory Structure

```
benchmark/
├── function_calling/          # Tool schema & response compression (⭐ primary benchmark)
│   ├── benchmark_schemas.py   # SchemaCompressor benchmark
│   ├── benchmark_responses.py # ResponseCompressor benchmark
│   ├── test_functional_equivalence.py  # Validates compressed schemas work with OpenAI
│   ├── visualize_results.py   # Generate charts
│   ├── data/
│   │   ├── schemas/           # 20 tool schemas (JSON)
│   │   └── responses/         # 20 API responses (JSON)
│   └── results/               # Generated results (CSV, MD, PNG)
│
├── packer/                    # MessagesPacker & TextPacker validation
│   ├── benchmark.py           # Comprehensive packer benchmark
│   └── results/               # Generated results (CSV)
│
├── rag_quality/               # RAG & text optimization quality
│   ├── benchmark.py           # Main benchmark orchestrator
│   ├── datasets.py            # Test data loader
│   ├── evaluators.py          # Quality metrics (cosine + judge)
│   ├── visualizer.py          # Result visualizations
│   ├── data/
│   │   ├── squad_samples.json # 15 SQuAD test cases
│   │   └── rag_scenarios.json # 15 RAG test cases
│   └── results/               # Generated results (CSV, MD, PNG)
│
├── latency/                   # Performance overhead measurement
│   └── benchmark.py           # Latency measurement script
│
└── README.md                  # This file
```

---

## 📈 Choosing the Right Benchmark

| Use Case | Recommended Benchmark | Why |
|----------|----------------------|-----|
| Prove function calling cost savings | Function Calling | Highest reduction (57%), lossless, $0 cost |
| Validate packer functionality | Packer | Ensures MessagesPacker/TextPacker work correctly |
| Validate RAG quality preservation | RAG Quality | Measures quality metrics, realistic scenarios |
| Answer "what's the overhead?" | Latency | Shows negligible impact (< 0.5ms per 1k tokens) |
| Demonstrate to stakeholders | Function Calling + RAG Quality | Comprehensive cost + quality proof |
| Quick validation | Function Calling | Fast, free, impressive results |

---

## 🎓 Interpreting Results

### Token Reduction

- **50%+**: Excellent (verbose APIs, function calling)
- **20-50%**: Very good (complex schemas, APIs with debug info)
- **10-20%**: Good (standard RAG, text optimization)
- **5-10%**: Acceptable (clean text with minor optimizations)
- **<5%**: May not be worth the overhead

### Quality Preservation

- **95%+**: Excellent (nearly identical responses)
- **90-95%**: Very good (minimal semantic drift)
- **85-90%**: Good (acceptable for most use cases)
- **80-85%**: Acceptable (review critical applications)
- **<80%**: Poor (not recommended for production)

### Cost vs Quality Trade-off

1. **Quality-first**: Choose highest quality strategy above your threshold
2. **Cost-first**: Choose most aggressive strategy meeting quality requirements
3. **Balanced**: Look for the "elbow" in the cost vs quality curve

---

## 💰 Cost Estimation

### Function Calling Benchmark
- **Cost**: $0 (local processing only)
- **Runtime**: < 2 minutes total
- **Output**: CSV results + visualizations

### RAG Quality Benchmark
- **Cost**: ~$2-5 per full run
  - 90 LLM calls (30 raw + 30 refined for 3 strategies)
  - 120 embedding calls
  - 90 judge evaluations
- **Runtime**: ~5 minutes
- **Output**: CSV + MD report + 3 visualizations

### Latency Benchmark
- **Cost**: $0 (no API calls)
- **Runtime**: ~1 minute
- **Output**: Console output only

---

## 🛠️ Customization

### Add Your Own Test Cases

**Function Calling:**
- Add schemas to `function_calling/data/schemas/`
- Add responses to `function_calling/data/responses/`
- Run benchmarks to see results

**RAG Quality:**
- Edit `rag_quality/data/squad_samples.json` or `rag_scenarios.json`:
  ```json
  {
    "scenario": "Your Use Case",
    "query": "Your question",
    "context": "Your context with <html> and   extra spaces",
    "expected_content": "What the answer should contain"
  }
  ```

### Test Your Own Strategy

Modify `rag_quality/benchmark.py`:
```python
def _setup_refining_strategies(self):
    return {
        "custom": Refiner()
            .pipe(YourOperation())
            .pipe(AnotherOperation())
    }
```

---

## 📊 Visualization Examples

### Function Calling

![Reduction by Category](function_calling/results/reduction_by_category.png)
![Top Schemas](function_calling/results/top_schemas.png)
![Cost Savings](function_calling/results/cost_savings.png)

### RAG Quality

![Token Reduction vs Quality](rag_quality/results/benchmark_results.png)
![Token Savings Distribution](rag_quality/results/token_savings_dist.png)
![Strategy Comparison](rag_quality/results/strategy_comparison.png)

---

## 🤝 Contributing

Have ideas for new benchmarking approaches? Open an issue or PR!

Potential future enhancements:
- Multi-model comparison (Claude, Llama, Gemini)
- Industry-standard datasets (MMLU, GSM8K)
- Production traffic replay
- Real-time latency profiling
- Cost/latency optimization analysis

---

## 📝 Citation

If you use these benchmark results in your work, please cite:

```
Prompt Refiner Benchmark Results
GitHub: https://github.com/JacobHuang91/prompt-refiner
```

---

## 📞 Support

- **Issues**: https://github.com/JacobHuang91/prompt-refiner/issues
- **Documentation**: https://jacobhuang91.github.io/prompt-refiner/
- **Discussions**: https://github.com/JacobHuang91/prompt-refiner/discussions
