# Latency Benchmark

This benchmark measures the processing overhead of Prompt Refiner operations.

## What It Measures

- **Individual operations**: HTML stripping, whitespace normalization, Unicode fixing, deduplication, truncation
- **Complete strategies**: Minimal, Standard, and Aggressive refining pipelines
- **Multiple input sizes**: 1k, 10k, and 50k tokens

For each operation and strategy, the benchmark reports:
- **Average latency** (mean across 100 iterations)
- **Median latency** (p50)
- **P95 latency** (95th percentile)
- **Per-1k-token overhead** (normalized metric)

## Running the Benchmark

No API keys or external dependencies needed:

```bash
python benchmark/latency_benchmark.py
```

The benchmark takes about 30-60 seconds to complete.

## Sample Results

```
================================================================================
PROMPT REFINER - LATENCY BENCHMARK
================================================================================

📊 INDIVIDUAL OPERATIONS
--------------------------------------------------------------------------------

Test data: ~10,000 tokens
Actual size: 10,010 tokens (40,040 characters)

  StripHTML           :   0.38ms avg  |    0.38ms median  |    0.41ms p95  |  0.04ms per 1k tokens
  NormalizeWhitespace :   0.12ms avg  |    0.12ms median  |    0.12ms p95  |  0.01ms per 1k tokens
  FixUnicode          :   5.58ms avg  |    5.56ms median  |    5.71ms p95  |  0.56ms per 1k tokens
  Deduplicate         :   0.04ms avg  |    0.04ms median  |    0.06ms p95  |  0.00ms per 1k tokens
  TruncateTokens      :   0.81ms avg  |    0.80ms median  |    0.89ms p95  |  0.08ms per 1k tokens

================================================================================
📦 REFINING STRATEGIES
--------------------------------------------------------------------------------

Test data: ~10,000 tokens
Actual size: 10,010 tokens (40,040 characters)

  Minimal (HTML + Whitespace)   :    0.48ms avg  |     0.47ms median  |     0.55ms p95  |  0.05ms per 1k tokens
  Standard (+ Deduplication)    :    2.47ms avg  |     2.45ms median  |     2.59ms p95  |  0.25ms per 1k tokens
  Aggressive (+ Truncate)       :    2.46ms avg  |     2.44ms median  |     2.57ms p95  |  0.25ms per 1k tokens
```

## Key Findings

### Negligible Overhead

- **Minimal strategy**: 0.05ms per 1k tokens
- **Standard strategy**: 0.25ms per 1k tokens
- **Aggressive strategy**: 0.25ms per 1k tokens

### Real-World Context

For a typical RAG application with 10k token context:
- Refining overhead: **~2.5ms** (Standard strategy)
- Network latency: **~100ms**
- LLM Processing (TTFT): **~500ms+**
- **Total overhead: < 0.5% of request time**

### Operation Performance

Fast operations (< 0.1ms per 1k tokens):
- `StripHTML`: 0.04ms per 1k tokens
- `NormalizeWhitespace`: 0.01ms per 1k tokens
- `Deduplicate`: < 0.01ms per 1k tokens
- `TruncateTokens`: 0.08ms per 1k tokens

Moderate operations:
- `FixUnicode`: 0.56ms per 1k tokens (still very fast)

### Scaling Behavior

The benchmark tests three input sizes to verify linear scaling:

| Strategy | 1k tokens | 10k tokens | 50k tokens |
|----------|-----------|------------|------------|
| Minimal | 0.05ms | 0.48ms | 2.39ms |
| Standard | 0.26ms | 2.47ms | 12.27ms |
| Aggressive | 0.26ms | 2.46ms | 12.38ms |

All strategies scale linearly with input size, confirming O(n) complexity.

## Methodology

### Test Data Generation

The benchmark generates synthetic test data that simulates real-world prompts:
- HTML tags and formatting
- Extra whitespace (multiple spaces, newlines)
- Repeated content (for deduplication testing)

Test data is generated to match target token counts (using 1 token ≈ 4 characters).

### Measurement Approach

1. **Warmup**: 10 iterations to warm up Python's JIT and caches
2. **Measurement**: 100 iterations (50 for strategies) using `time.perf_counter()`
3. **Statistics**: Calculate mean, median, and P95 from collected samples

### Why These Metrics?

- **Mean**: Overall average performance
- **Median**: Typical performance (not skewed by outliers)
- **P95**: Worst-case performance for production planning
- **Per-1k-token**: Normalized metric for comparing operations

## Interpreting Results

### When Latency Matters

Refining overhead is negligible compared to:
- Network roundtrip (50-100ms)
- LLM Time-To-First-Token (TTFT) (300-1000ms)
- Full response generation (1000-5000ms)

### When to Optimize

Consider refining latency only if:
- You're processing > 100k tokens in a tight loop
- Your total pipeline budget is < 10ms
- You're doing real-time client-side processing on mobile devices

For 99% of use cases, the token cost savings (10-20%) far outweigh the < 0.5% latency overhead.

## Technical Details

### Token Estimation

The benchmark uses a rough approximation of **1 token ≈ 4 characters** for GPT models. This is used to normalize results but does not affect actual measurements.

### Python Performance

Results may vary based on:
- Python version (3.9+ recommended)
- CPU architecture and speed
- System load and background processes

Run the benchmark multiple times to get stable results.

## Related Benchmarks

- **Quality Benchmark**: See [custom/README.md](custom/README.md) for token reduction and response quality metrics
- **Cost Analysis**: See main [README.md](../README.md) for cost savings calculations
