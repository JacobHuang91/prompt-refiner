# Prompt Refiner Benchmarks

This directory contains different benchmarking approaches to validate the cost-effectiveness of prompt-refiner.

## 📊 Available Benchmarks

### [`latency/`](latency/) - Latency & Performance

Measures the processing overhead of prompt refining operations:
- Tests individual operations and complete strategies
- Measures latency at 1k, 10k, and 50k token scales
- Reports average, median, and P95 latency
- Zero cost - no API calls needed

**Cost**: $0 (runs locally)

**When to use**: Performance validation, answering "what's the overhead?", optimizing for latency-critical applications

[→ See latency benchmark documentation](latency/README.md)

### [`custom/`](custom/) - Custom A/B Testing

A custom A/B testing approach that compares raw vs refined prompts:
- Tests 3 refining strategies (minimal, standard, aggressive)
- Uses 30 curated test cases (SQuAD + RAG scenarios)
- Measures token reduction and response quality
- Quality evaluation via cosine similarity + LLM-as-a-judge

**Cost**: ~$2-5 per full run (using gpt-4o-mini)

**When to use**: Quality validation, proving cost savings, establishing baseline metrics

[→ See custom benchmark documentation](custom/README.md)

---

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   uv sync --group dev
   ```

2. **Set up API key** (for custom benchmark):
   ```bash
   cd benchmark/custom
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run a benchmark**:
   ```bash
   # Latency benchmark (no API key needed)
   cd benchmark/latency
   python benchmark.py

   # Quality/cost benchmark (requires OpenAI API key)
   cd benchmark/custom
   python benchmark.py
   ```

## 📈 Choosing a Benchmark

| Benchmark | Speed | Cost | What It Measures | Best For |
|-----------|-------|------|------------------|----------|
| **latency** | Very Fast | $0 | Processing overhead, execution time | Performance validation, latency analysis |
| **custom** | Fast | ~$3 | Token reduction, response quality | Quality & cost savings validation |
| **ragas** | - | - | - | *(coming soon)* |

## 🤝 Contributing

Have ideas for new benchmarking approaches? Open an issue or PR!

Potential future benchmarks:
- Industry-standard benchmarks (MMLU, HellaSwag, etc.)
- Production traffic replay
- Multi-model comparison
- Cost/latency optimization analysis
