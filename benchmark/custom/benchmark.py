"""Main benchmark orchestrator for evaluating prompt-refiner effectiveness."""

import os
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd
from tqdm import tqdm

from datasets import create_test_dataset
from evaluators import CosineEvaluator, LLMJudgeEvaluator, evaluate_responses
from visualizer import create_all_visualizations

# Import prompt_refiner from project root
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from prompt_refiner import Refiner
from prompt_refiner.cleaner import StripHTML, NormalizeWhitespace
from prompt_refiner.compressor import TruncateTokens, Deduplicate


class Benchmark:
    """
    Orchestrates the cost-effectiveness benchmark for prompt-refiner.

    Tests multiple refining strategies to measure:
    - Token reduction (cost savings)
    - Response quality maintenance (cosine similarity + LLM judge)
    """

    def __init__(
        self,
        openai_api_key: str,
        model: str = "gpt-4o-mini",
        strategies: Optional[List[str]] = None
    ):
        """
        Initialize the benchmark.

        Args:
            openai_api_key: OpenAI API key for LLM calls
            model: Model to use for Q&A testing (default: gpt-4o-mini for cost)
            strategies: List of strategies to test (default: all 3)
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package is required for benchmarking. "
                "Install with: pip install openai"
            )

        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.strategies = strategies or ["minimal", "standard", "aggressive"]

        # Initialize evaluators
        self.cosine_evaluator = CosineEvaluator(api_key=openai_api_key)
        self.judge_evaluator = LLMJudgeEvaluator(api_key=openai_api_key)

        # Setup refining strategies
        self.refiners = self._setup_refining_strategies()

        # Results storage
        self.results = []

    def _setup_refining_strategies(self) -> Dict[str, Refiner]:
        """
        Define refining strategies with different aggressiveness levels.

        Returns:
            Dictionary mapping strategy name to Refiner instance
        """
        return {
            "minimal": Refiner()
                .pipe(StripHTML())
                .pipe(NormalizeWhitespace()),

            "standard": Refiner()
                .pipe(StripHTML())
                .pipe(NormalizeWhitespace())
                .pipe(Deduplicate(similarity_threshold=0.8, granularity="sentence")),

            "aggressive": Refiner()
                .pipe(StripHTML())
                .pipe(NormalizeWhitespace())
                .pipe(Deduplicate(similarity_threshold=0.7, granularity="sentence"))
                .pipe(TruncateTokens(max_tokens=150))
        }

    def _query_llm(
        self,
        query: str,
        context: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Query the LLM with a prompt and return response + token count.

        Args:
            query: User question/query
            context: Context information (raw or refined)
            max_retries: Number of retry attempts on failure

        Returns:
            Dictionary with response, prompt_tokens, completion_tokens
        """
        prompt = f"""Answer the following question based on the provided context.

Context:
{context}

Question: {query}

Answer:"""

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0  # Deterministic for consistency
                )

                return {
                    "response": response.choices[0].message.content,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }

            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"  ⚠️  API error (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff

        raise RuntimeError("Failed to query LLM after retries")

    def run_single_test(
        self,
        test_case: Dict[str, Any],
        strategy: str
    ) -> Dict[str, Any]:
        """
        Run a single test case with one refining strategy.

        Args:
            test_case: Test case dictionary with query, context, expected
            strategy: Refining strategy name

        Returns:
            Dictionary with results for this test
        """
        # Get context (raw and refined)
        context_raw = test_case["context"]
        refiner = self.refiners[strategy]
        context_refined = refiner.run(context_raw)

        # Calculate token counts
        from prompt_refiner.analyzer import CountTokens

        counter_raw = CountTokens()
        counter_raw.process(context_raw)
        stats_raw = counter_raw.get_stats()

        counter_refined = CountTokens()
        counter_refined.process(context_refined)
        stats_refined = counter_refined.get_stats()

        token_reduction = (
            (stats_raw["tokens"] - stats_refined["tokens"]) / stats_raw["tokens"] * 100
            if stats_raw["tokens"] > 0 else 0
        )

        # Query LLM with both versions
        result_raw = self._query_llm(test_case["query"], context_raw)
        result_refined = self._query_llm(test_case["query"], context_refined)

        # Evaluate quality
        evaluation = evaluate_responses(
            question=test_case["query"],
            response_raw=result_raw["response"],
            response_refined=result_refined["response"],
            cosine_evaluator=self.cosine_evaluator,
            judge_evaluator=self.judge_evaluator
        )

        return {
            "test_id": test_case["id"],
            "test_type": test_case["type"],
            "strategy": strategy,
            "context_tokens_raw": stats_raw["tokens"],
            "context_tokens_refined": stats_refined["tokens"],
            "token_reduction": token_reduction,
            "prompt_tokens_raw": result_raw["prompt_tokens"],
            "prompt_tokens_refined": result_refined["prompt_tokens"],
            "total_tokens_raw": result_raw["total_tokens"],
            "total_tokens_refined": result_refined["total_tokens"],
            "response_raw": result_raw["response"],
            "response_refined": result_refined["response"],
            "quality_cosine": evaluation.get("cosine", {}).get("similarity", None),
            "quality_equivalent_cosine": evaluation.get("cosine", {}).get("equivalent", None),
            "quality_equivalent_judge": evaluation.get("judge", {}).get("equivalent", None),
            "quality_confidence_judge": evaluation.get("judge", {}).get("confidence", None),
            "overall_equivalent": evaluation.get("overall_equivalent", None)
        }

    def run_benchmark(
        self,
        n_squad: int = 15,
        n_rag: int = 15
    ) -> pd.DataFrame:
        """
        Run the complete benchmark across all test cases and strategies.

        Args:
            n_squad: Number of SQuAD samples to test
            n_rag: Number of RAG scenarios to test

        Returns:
            DataFrame with all results
        """
        print("🚀 Starting Prompt Refiner Benchmark\n")
        print(f"Model: {self.model}")
        print(f"Strategies: {', '.join(self.strategies)}")
        print(f"Test cases: {n_squad} SQuAD + {n_rag} RAG = {n_squad + n_rag} total\n")

        # Load test dataset
        test_cases = create_test_dataset(n_squad=n_squad, n_rag=n_rag)

        # Calculate total iterations
        total_tests = len(test_cases) * len(self.strategies)

        # Run all combinations with progress bar
        with tqdm(total=total_tests, desc="Running tests") as pbar:
            for test_case in test_cases:
                for strategy in self.strategies:
                    try:
                        result = self.run_single_test(test_case, strategy)
                        self.results.append(result)
                        pbar.set_postfix({
                            "test": test_case["id"],
                            "strategy": strategy,
                            "tokens_saved": f"{result['token_reduction']:.1f}%"
                        })
                    except Exception as e:
                        print(f"\n❌ Error on {test_case['id']} ({strategy}): {e}")
                        # Continue with other tests

                    pbar.update(1)

        # Convert to DataFrame
        df = pd.DataFrame(self.results)
        return df

    def calculate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Calculate summary statistics by strategy.

        Args:
            df: Results DataFrame

        Returns:
            Dictionary mapping strategy to metrics
        """
        summary = {}

        for strategy in self.strategies:
            strategy_data = df[df["strategy"] == strategy]

            if len(strategy_data) == 0:
                continue

            summary[strategy] = {
                "token_reduction": strategy_data["token_reduction"].mean(),
                "quality_cosine": strategy_data["quality_cosine"].mean(),
                "quality_judge": strategy_data["quality_equivalent_judge"].sum() / len(strategy_data) * 100,
                "overall_equivalent": strategy_data["overall_equivalent"].sum() / len(strategy_data) * 100,
                "n_tests": len(strategy_data)
            }

        return summary

    def generate_report(
        self,
        df: pd.DataFrame,
        output_dir: str = "."
    ) -> None:
        """
        Generate comprehensive benchmark report.

        Args:
            df: Results DataFrame
            output_dir: Directory to save report and visualizations
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print("\n📊 Generating Report...\n")

        # Calculate summary statistics
        summary = self.calculate_summary_stats(df)

        # Create visualizations
        create_all_visualizations(df, summary, str(output_path))

        # Generate markdown report
        report_path = output_path / "BENCHMARK_RESULTS.md"

        with open(report_path, "w") as f:
            f.write("# Prompt Refiner Benchmark Results\n\n")
            f.write(f"**Model:** {self.model}\n")
            f.write(f"**Test Cases:** {len(df) // len(self.strategies)} total\n")
            f.write(f"**Strategies Tested:** {', '.join(self.strategies)}\n\n")

            f.write("## Summary Statistics\n\n")
            f.write("| Strategy | Token Reduction | Quality (Cosine) | Judge Approval | Overall Equivalent |\n")
            f.write("|----------|----------------|------------------|----------------|--------------------|\n")

            for strategy, stats in summary.items():
                f.write(f"| {strategy.capitalize()} | "
                       f"{stats['token_reduction']:.1f}% | "
                       f"{stats['quality_cosine']:.3f} | "
                       f"{stats['quality_judge']:.1f}% | "
                       f"{stats['overall_equivalent']:.1f}% |\n")

            f.write("\n## Key Findings\n\n")

            # Find best strategy
            best_strategy = max(summary.items(),
                              key=lambda x: x[1]['token_reduction'] if x[1]['overall_equivalent'] >= 80 else 0)

            f.write(f"### 🏆 Best Strategy: **{best_strategy[0].capitalize()}**\n\n")
            f.write(f"- Token Reduction: **{best_strategy[1]['token_reduction']:.1f}%**\n")
            f.write(f"- Quality Maintenance: **{best_strategy[1]['quality_cosine']:.3f}** cosine similarity\n")
            f.write(f"- Judge Approval: **{best_strategy[1]['quality_judge']:.1f}%**\n\n")

            f.write("### 💰 Cost Savings\n\n")
            f.write(f"For **1,000 API calls** using GPT-4 ($0.03/1k input tokens):\n\n")

            for strategy, stats in summary.items():
                avg_tokens_saved = stats['token_reduction'] / 100 * 1000  # Assume 1000 token avg
                cost_saved = avg_tokens_saved * 0.03 / 1000
                f.write(f"- **{strategy.capitalize()}**: Save ~${cost_saved * 1000:.2f} "
                       f"({stats['token_reduction']:.1f}% reduction)\n")

            f.write("\n## Visualizations\n\n")
            f.write("![Cost vs Quality](benchmark_results.png)\n\n")
            f.write("![Token Savings Distribution](token_savings_dist.png)\n\n")
            f.write("![Strategy Comparison](strategy_comparison.png)\n\n")

            f.write("## Detailed Results\n\n")
            f.write("Full results saved to `benchmark_results.csv`\n")

        # Save detailed results
        df.to_csv(output_path / "benchmark_results.csv", index=False)

        print(f"✅ Report saved to {report_path}")
        print(f"✅ Detailed results saved to {output_path / 'benchmark_results.csv'}")
        print(f"✅ Visualizations saved to {output_path}/")


def main():
    """Run the benchmark with command-line arguments."""
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv is optional

    import argparse

    parser = argparse.ArgumentParser(description="Run Prompt Refiner benchmark")
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model to use for testing (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--strategies",
        nargs="+",
        default=["minimal", "standard", "aggressive"],
        help="Strategies to test (default: all)"
    )
    parser.add_argument(
        "--n-squad",
        type=int,
        default=15,
        help="Number of SQuAD samples (default: 15)"
    )
    parser.add_argument(
        "--n-rag",
        type=int,
        default=15,
        help="Number of RAG scenarios (default: 15)"
    )
    parser.add_argument(
        "--output-dir",
        default="./results",
        help="Output directory for results (default: ./results)"
    )

    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("OpenAI API key required. Set OPENAI_API_KEY or use --api-key")

    # Run benchmark
    benchmark = Benchmark(
        openai_api_key=args.api_key,
        model=args.model,
        strategies=args.strategies
    )

    df = benchmark.run_benchmark(
        n_squad=args.n_squad,
        n_rag=args.n_rag
    )

    benchmark.generate_report(df, output_dir=args.output_dir)

    print("\n🎉 Benchmark complete!")


if __name__ == "__main__":
    main()
