# Prompt Refiner Benchmark

This benchmark validates the cost-effectiveness of prompt-refiner by measuring:
- **Token reduction** (cost savings)
- **Response quality maintenance** (semantic similarity)

## 🎯 What This Benchmark Does

The benchmark runs A/B tests comparing:
- **Raw prompts** (unprocessed context)
- **Refined prompts** (cleaned with different strategies)

For each strategy, it measures:
1. **Token Reduction**: Percentage of tokens saved
2. **Quality (Cosine Similarity)**: Semantic similarity of responses (0-1)
3. **Quality (LLM Judge)**: GPT-4 evaluation of response equivalence
4. **Overall Equivalence**: Both metrics agree responses are equivalent

## 📊 Test Dataset

The benchmark uses 30 carefully curated test cases:

### SQuAD Samples (15 cases)
- Question-answer pairs with context
- Topics: history, science, geography, literature, technology
- Examples: "When did Beyonce start becoming popular?", "What is DNA?"

### RAG Scenarios (15 cases)
- Realistic retrieval-augmented generation use cases
- Domains: e-commerce, documentation, customer support, code search, recipes
- Context includes messy HTML, extra whitespace, and duplicate content

## 🔧 Installation

Install dependencies:

```bash
# Using uv (recommended)
uv sync --group dev
```

This installs:
- `openai` - For LLM API calls and embeddings
- `pandas` - For results management
- `matplotlib` - For visualizations
- `scikit-learn` - For cosine similarity
- `tqdm` - For progress tracking
- `python-dotenv` - For loading .env files

## 🚀 Running the Benchmark

### Prerequisites

**Option 1: Using .env file (Recommended)**

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

The benchmark will automatically load variables from `.env`.

**Option 2: Using environment variable**

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

Run the full benchmark with default settings:

```bash
cd benchmark/custom
python benchmark.py
```

This will:
1. Test 30 cases with 3 strategies (90 total comparisons)
2. Generate detailed report with visualizations
3. Save results to `./results/` directory

### Advanced Options

```bash
# Use a different model
python benchmark.py --model gpt-4o

# Test specific strategies only
python benchmark.py --strategies minimal standard

# Use fewer test cases (faster, cheaper)
python benchmark.py --n-squad 5 --n-rag 5

# Custom output directory
python benchmark.py --output-dir ./my_results
```

### All Options

```bash
python benchmark.py --help
```

Available options:
- `--api-key`: OpenAI API key (or use `OPENAI_API_KEY` env var)
- `--model`: Model to use (default: `gpt-4o-mini`)
- `--strategies`: Strategies to test (default: all 3)
- `--n-squad`: Number of SQuAD samples (default: 15)
- `--n-rag`: Number of RAG scenarios (default: 15)
- `--output-dir`: Output directory (default: `./results`)

## 📈 Refining Strategies

The benchmark tests 3 strategies with increasing aggressiveness:

### Minimal
```python
StripHTML() | NormalizeWhitespace()
```
- Removes HTML tags
- Normalizes whitespace
- **Best for**: Clean inputs that need minor cleanup

### Standard
```python
StripHTML() | NormalizeWhitespace() | Deduplicate(similarity_threshold=0.8, granularity="sentence")
```
- All minimal operations
- Removes 80%+ similar sentences
- Uses sentence-level deduplication
- **Best for**: RAG contexts with some duplication

### Aggressive
```python
StripHTML() | NormalizeWhitespace() | Deduplicate(similarity_threshold=0.7, granularity="sentence") | TruncateTokens(max_tokens=150)
```
- All standard operations
- More aggressive deduplication (70%+ similarity)
- Hard limit at 150 tokens
- **Best for**: Very long contexts with lots of duplication

## 📊 Results

After running, you'll find in `./results/`:

### Files Generated

1. **`BENCHMARK_RESULTS.md`** - Human-readable summary report
   - Summary statistics by strategy
   - Key findings and best strategy
   - Cost savings calculations
   - Embedded visualizations

2. **`benchmark_results.csv`** - Full detailed results
   - Every test case result
   - Token counts (raw vs refined)
   - Quality metrics
   - Actual responses

3. **Visualizations** (PNG images):
   - `benchmark_results.png` - Token reduction vs quality scatter plot
   - `token_savings_dist.png` - Distribution of savings by strategy
   - `strategy_comparison.png` - Bar chart comparing all metrics

### Real Benchmark Results

Based on 30 test cases (15 SQuAD + 15 RAG scenarios) using gpt-4o-mini:

```
| Strategy   | Token Reduction | Quality (Cosine) | Judge Approval | Overall Equivalent |
|------------|----------------|------------------|----------------|-------------------|
| Minimal    | 4.3%           | 0.987            | 86.7%          | 86.7%             |
| Standard   | 4.8%           | 0.984            | 90.0%          | 86.7%             |
| Aggressive | 15.0%          | 0.964            | 80.0%          | 66.7%             |
```

**Key Insights:**
- **Aggressive strategy achieves 3x more savings (15%) vs Minimal (4.3%)**
- RAG scenarios with duplicates showed 17-74% savings per test with aggressive strategy
- Standard strategy (with deduplication) shows minimal improvement over basic cleaning
- Aggressive strategy maintains 96.4% quality while providing 15% cost reduction
- **Trade-off**: Aggressive saves more tokens but has lower judge approval (80% vs 90%)

**Strategy Differentiation on Individual Tests:**
- rag_001: Minimal 17% → Standard 31% → **Aggressive 49%**
- rag_005: Minimal 19% → Standard 19% → **Aggressive 48%**
- rag_015: Minimal 0% → Standard 0% → **Aggressive 74%** (long context truncation)

**Visualizations:**

![Token Reduction vs Quality](results/benchmark_results.png)

![Token Savings Distribution](results/token_savings_dist.png)

![Strategy Comparison](results/strategy_comparison.png)

## 💰 Cost Estimation

The benchmark itself costs approximately:
- **Model calls**: 60 calls (30 raw + 30 refined) × 3 strategies = 180 calls
- **Embeddings**: 60 pairs × 2 = 120 embedding calls
- **Judge evaluations**: 90 evaluation calls

**Total cost** (using gpt-4o-mini): ~$2-5 for full benchmark

## 🎓 Understanding Results

### Token Reduction
- Higher is better for cost savings
- 20%+ reduction is excellent
- 10-20% is good
- <10% may not be worth the refining overhead

### Quality Metrics

**Cosine Similarity**:
- 0.95+ = Excellent (nearly identical semantic meaning)
- 0.90-0.95 = Good (very similar)
- 0.85-0.90 = Acceptable (similar enough)
- <0.85 = Poor (significant difference)

**Judge Approval**:
- 90%+ = Excellent
- 80-90% = Good
- 70-80% = Acceptable
- <70% = Poor

**Overall Equivalent**:
- Requires BOTH metrics to pass
- Most conservative measure
- Use this for production decisions

## 🔍 Interpreting Trade-offs

The benchmark helps you choose the right strategy:

1. **Quality-first**: Choose strategy with highest quality above your threshold
2. **Cost-first**: Choose most aggressive strategy that meets your quality requirements
3. **Balanced**: Look for the "elbow" in the cost vs quality curve

Example decision:
- If Standard saves 25% with 98% quality
- And Aggressive saves 35% with 97% quality
- **Choose Standard** (diminishing returns for 10% more savings)

## 🛠️ Customization

### Add Your Own Test Cases

Edit `data/rag_scenarios.json` or `data/squad_samples.json`:

```json
{
  "scenario": "Your Use Case",
  "query": "Your question",
  "context": "Your context with <html> and   extra spaces",
  "expected_content": "What the answer should contain"
}
```

### Test Your Own Strategy

Modify `benchmark.py`:

```python
def _setup_refining_strategies(self):
    return {
        "custom": Refiner()
            .pipe(YourOperation())
            .pipe(AnotherOperation())
    }
```

## 📝 Citation

If you use these benchmark results in your work, please cite:

```
Prompt Refiner Benchmark Results
https://github.com/JacobHuang91/prompt-refiner
```

## 🤝 Contributing

Found issues with test cases or have suggestions? Open an issue!
