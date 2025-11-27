# Benchmark Results

Prompt Groomer's effectiveness has been validated through comprehensive A/B testing on 30 real-world test cases.

## Overview

The benchmark measures two critical factors:

- **Token Reduction** - How much we can reduce prompt size (cost savings)
- **Response Quality** - Whether responses remain semantically equivalent

Quality is evaluated using two methods:
1. **Cosine Similarity** - Semantic similarity of response embeddings (0-1 scale)
2. **LLM Judge** - GPT-4 evaluation of response equivalence

## Results Summary

We tested 3 optimization strategies on 30 test cases (15 SQuAD Q&A pairs + 15 RAG scenarios):

| Strategy | Token Reduction | Quality (Cosine) | Judge Approval | Overall Equivalent |
|----------|----------------|------------------|----------------|--------------------|
| **Minimal** | 4.3% | 0.987 | 86.7% | 86.7% |
| **Standard** | 4.8% | 0.984 | 90.0% | 86.7% |
| **Aggressive** | **15.0%** | 0.964 | 80.0% | 66.7% |

### Strategy Definitions

**Minimal** (Conservative cleaning):
```python
pipeline = StripHTML() | NormalizeWhitespace()
```

**Standard** (Recommended for most use cases):
```python
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | Deduplicate(similarity_threshold=0.85)
)
```

**Aggressive** (Maximum savings):
```python
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | Deduplicate(similarity_threshold=0.85)
    | TruncateTokens(max_tokens=150, strategy="head")
)
```

## Key Findings

### 🎯 Standard Strategy: Best Balance

The **Standard** strategy offers the best balance:
- **4.8% token reduction** with minimal quality impact
- **90% judge approval** - highest among all strategies
- **0.984 cosine similarity** - nearly perfect semantic preservation

### 💰 Cost Savings

Real-world cost savings for production applications:

=== "GPT-4 Turbo"
    **Input cost:** $0.01 per 1K tokens

    | Volume | Minimal (4.3%) | Standard (4.8%) | Aggressive (15%) |
    |--------|----------------|-----------------|------------------|
    | 100K tokens/month | **$4.30** | **$4.80** | **$15.00** |
    | 1M tokens/month | **$43** | **$48** | **$150** |
    | 10M tokens/month | **$430** | **$480** | **$1,500** |

=== "GPT-4"
    **Input cost:** $0.03 per 1K tokens

    | Volume | Minimal (4.3%) | Standard (4.8%) | Aggressive (15%) |
    |--------|----------------|-----------------|------------------|
    | 100K tokens/month | **$13** | **$14** | **$45** |
    | 1M tokens/month | **$129** | **$144** | **$450** |
    | 10M tokens/month | **$1,290** | **$1,440** | **$4,500** |

### 📊 Performance by Scenario

**RAG Scenarios** (with duplicates and HTML):
- Minimal: **17% reduction** on average
- Standard: **31% reduction** on average
- Aggressive: **49% reduction** on complex documents

**SQuAD Q&A** (clean academic text):
- All strategies: **2-5% reduction** (less messy data = less to clean)

!!! success "Key Insight"
    Token savings scale with input messiness. RAG contexts with HTML, duplicates, and whitespace see 3-10x more reduction than clean text.

## Visualizations

### Token Reduction vs Quality

![Benchmark Results](https://raw.githubusercontent.com/JacobHuang91/prompt-groomer/main/benchmark/custom/results/benchmark_results.png)

The scatter plot shows each strategy's position in the cost-quality tradeoff space. Standard strategy achieves near-optimal quality while maintaining solid savings.

## Test Dataset

The benchmark uses 30 carefully curated test cases:

### SQuAD Samples (15 cases)
Question-answer pairs with context covering:
- History ("When did Beyonce start becoming popular?")
- Science ("What is DNA?")
- Geography, literature, technology

### RAG Scenarios (15 cases)
Realistic retrieval-augmented generation use cases:
- E-commerce product catalogs with HTML
- Documentation with excessive whitespace
- Customer support tickets with duplicates
- Code search results
- Recipe collections

## Running the Benchmark

Want to validate these results yourself?

### Prerequisites

```bash
# Install benchmark dependencies
uv pip install -e ".[benchmark]"

# Set up OpenAI API key
cd benchmark/custom
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run the Benchmark

```bash
cd benchmark/custom
python benchmark.py
```

This will:
1. Test 30 cases with 3 strategies (90 total comparisons)
2. Generate detailed report with visualizations
3. Save results to `./results/` directory

**Estimated cost:** ~$2-5 per full run (using gpt-4o-mini)

### Advanced Options

```bash
# Use a different model
python benchmark.py --model gpt-4o

# Test specific strategies only
python benchmark.py --strategies minimal standard

# Use fewer test cases (faster, cheaper)
python benchmark.py --limit 10
```

## Recommendations

Based on benchmark results:

### For Production RAG Applications
Use **Standard strategy** - Best balance of savings and quality
```python
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | Deduplicate(similarity_threshold=0.85)
)
```

### For High-Volume, Cost-Sensitive Applications
Consider **Aggressive strategy** if 15% cost reduction outweighs slightly lower quality
```python
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | Deduplicate(similarity_threshold=0.85)
    | TruncateTokens(max_tokens=150)
)
```

### For Quality-Critical Applications
Use **Minimal strategy** for maximum quality preservation
```python
pipeline = StripHTML() | NormalizeWhitespace()
```

## Learn More

- [View Full Benchmark Documentation](https://github.com/JacobHuang91/prompt-groomer/tree/main/benchmark/custom)
- [Browse Test Cases](https://github.com/JacobHuang91/prompt-groomer/tree/main/benchmark/custom/data)
- [Examine Raw Results](https://github.com/JacobHuang91/prompt-groomer/blob/main/benchmark/custom/results/BENCHMARK_RESULTS.md)

## Contributing

Have ideas to improve the benchmark? We welcome:
- New test cases (especially domain-specific scenarios)
- Additional evaluation metrics
- Alternative grooming strategies
- Multi-model comparisons

[Open an issue](https://github.com/JacobHuang91/prompt-groomer/issues) or submit a PR!
