"""
Benchmark ResponseCompressor on real-world API responses.

Tests ResponseCompressor effectiveness on 20 API responses from
popular APIs and tools. Measures token reduction while verifying
essential data preservation and debug field removal.

Usage:
    python benchmark_responses.py [--output OUTPUT_DIR]
"""

import argparse
import json
from glob import glob
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import tiktoken

from prompt_refiner.tools import ResponseCompressor


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens using tiktoken."""
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))


def categorize_response(tokens_original: int) -> str:
    """Categorize response by verbosity based on token count."""
    if tokens_original < 200:
        return "Simple"
    elif tokens_original < 500:
        return "Medium"
    elif tokens_original < 1000:
        return "Complex"
    else:
        return "Very Verbose"


def verify_compression_quality(original: Dict, compressed: Dict) -> Dict[str, bool]:
    """Verify that compression preserves essential data and removes debug fields."""
    checks = {}

    # Check that debug fields matching ResponseCompressor's drop_keys are removed
    # ResponseCompressor default drop_keys: debug, trace, traces, stack, stacktrace, logs, logging
    default_drop_keys = {"debug", "trace", "traces", "stack", "stacktrace", "logs", "logging"}

    def has_droppable_fields(obj: Dict) -> bool:
        """Check if object contains any exact-match droppable keys."""
        for key in obj.keys():
            if key in default_drop_keys:
                return True
        return False

    checks["droppable_fields_removed"] = not has_droppable_fields(compressed)

    # Check that essential fields are preserved (at least some core keys remain)
    # We expect null values and empty containers to be removed, but core data should remain
    # Just verify that compressed still has keys (not completely empty)
    checks["has_data"] = len(compressed) > 0

    # Check that JSON structure is valid (already passed if we got here, but explicit check)
    checks["valid_json"] = isinstance(compressed, dict)

    # Check that compression actually reduced size
    checks["size_reduced"] = len(json.dumps(compressed)) < len(json.dumps(original))

    checks["all_checks_passed"] = all(checks.values())

    return checks


def benchmark_single_response(
    response_path: str,
    compressor: ResponseCompressor
) -> Dict[str, Any]:
    """Benchmark ResponseCompressor on a single API response."""
    # Load original response
    with open(response_path) as f:
        response_original = json.load(f)

    # Compress response
    response_compressed = compressor.process(response_original)

    # Count tokens
    tokens_original = count_tokens(json.dumps(response_original))
    tokens_compressed = count_tokens(json.dumps(response_compressed))
    tokens_saved = tokens_original - tokens_compressed
    reduction_pct = (tokens_saved / tokens_original * 100) if tokens_original > 0 else 0

    # Verify compression quality
    verification = verify_compression_quality(response_original, response_compressed)

    # Categorize
    category = categorize_response(tokens_original)

    return {
        "response": Path(response_path).stem,
        "category": category,
        "tokens_original": tokens_original,
        "tokens_compressed": tokens_compressed,
        "tokens_saved": tokens_saved,
        "reduction_percent": round(reduction_pct, 1),
        **verification
    }


def generate_before_after_examples(
    results_df: pd.DataFrame,
    responses_dir: Path,
    output_dir: Path,
    top_n: int = 3
) -> None:
    """Generate before/after examples for top N responses by reduction."""
    top_responses = results_df.nlargest(top_n, "reduction_percent")

    examples_md = "# Response Compression Examples\n\n"
    examples_md += "Top 3 API responses by token reduction percentage:\n\n"

    compressor = ResponseCompressor()

    for idx, row in top_responses.iterrows():
        response_name = row["response"]
        response_path = responses_dir / f"{response_name}.json"

        # Load original
        with open(response_path) as f:
            original = json.load(f)

        # Compress
        compressed = compressor.process(original)

        examples_md += f"## {idx + 1}. {response_name}\n\n"
        examples_md += f"**Token Reduction**: {row['tokens_original']} → {row['tokens_compressed']} "
        examples_md += f"({row['reduction_percent']}% reduction)\n\n"
        examples_md += f"**Category**: {row['category']}\n\n"

        # Show key statistics
        examples_md += "**Compression Results**:\n"
        examples_md += f"- Original keys: {len(original)}\n"
        examples_md += f"- Compressed keys: {len(compressed)}\n"
        examples_md += f"- Keys removed: {len(original) - len(compressed)}\n"
        examples_md += f"- Size reduction: {len(json.dumps(original))} → {len(json.dumps(compressed))} bytes\n\n"

        # Show removed debug fields
        removed_fields = [k for k in original.keys() if k not in compressed]
        if removed_fields:
            examples_md += f"**Removed Debug Fields**: {', '.join(removed_fields)}\n\n"

        # Show preserved essential fields (first 5)
        preserved_fields = [k for k in compressed.keys()][:5]
        examples_md += f"**Essential Fields Preserved** (showing first 5): {', '.join(preserved_fields)}\n\n"

        examples_md += "---\n\n"

    # Save examples
    examples_path = output_dir / "before_after_examples.md"
    with open(examples_path, "w") as f:
        f.write(examples_md)

    print(f"✓ Generated before/after examples: {examples_path}")


def main():
    """Run response compression benchmark."""
    parser = argparse.ArgumentParser(
        description="Benchmark ResponseCompressor on real-world API responses"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results",
        help="Output directory for results (default: results)"
    )
    args = parser.parse_args()

    # Paths
    base_dir = Path(__file__).parent
    responses_dir = base_dir / "data" / "responses"
    output_dir = base_dir / args.output
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Response Compression Benchmark")
    print("=" * 60)
    print(f"Responses directory: {responses_dir}")
    print(f"Output directory: {output_dir}")
    print()

    # Find all response files
    response_files = sorted(glob(str(responses_dir / "*.json")))
    print(f"Found {len(response_files)} response files")
    print()

    # Initialize compressor
    compressor = ResponseCompressor()

    # Benchmark each response
    results = []
    print("Benchmarking responses:")
    print("-" * 60)

    for response_path in response_files:
        response_name = Path(response_path).stem
        result = benchmark_single_response(response_path, compressor)
        results.append(result)

        status = "✓" if result["all_checks_passed"] else "✗"
        print(
            f"{status} {response_name:45} | "
            f"{result['tokens_original']:4} → {result['tokens_compressed']:4} | "
            f"{result['reduction_percent']:5.1f}% reduction"
        )

    print("-" * 60)
    print()

    # Create DataFrame
    df = pd.DataFrame(results)

    # Calculate statistics by category
    print("Results by Category:")
    print("-" * 60)
    category_stats = df.groupby("category")["reduction_percent"].agg([
        ("count", "count"),
        ("mean", "mean"),
        ("median", "median"),
        ("min", "min"),
        ("max", "max")
    ]).round(1)
    print(category_stats)
    print()

    # Overall statistics
    print("Overall Statistics:")
    print("-" * 60)
    print(f"Total responses tested: {len(df)}")
    print(f"Average token reduction: {df['reduction_percent'].mean():.1f}%")
    print(f"Median token reduction: {df['reduction_percent'].median():.1f}%")
    print(f"Min reduction: {df['reduction_percent'].min():.1f}%")
    print(f"Max reduction: {df['reduction_percent'].max():.1f}%")
    print(f"Total tokens saved: {df['tokens_saved'].sum():,}")
    print(f"All quality checks passed: {df['all_checks_passed'].all()}")
    print()

    # Save results to CSV
    csv_path = output_dir / "response_compression_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ Results saved to: {csv_path}")
    print()

    # Generate before/after examples
    generate_before_after_examples(df, responses_dir, output_dir, top_n=3)
    print()

    # Quality verification summary
    if df["all_checks_passed"].all():
        print("✓ All quality checks passed across all responses!")
        print("  - Droppable fields removed (debug, trace, logs, etc.)")
        print("  - Data preserved (non-empty result)")
        print("  - Valid JSON structure")
        print("  - Size reduced")
    else:
        failed = df[~df["all_checks_passed"]]
        print(f"✗ Quality verification failed for {len(failed)} responses:")
        for idx, row in failed.iterrows():
            print(f"  - {row['response']}")
            if not row.get("droppable_fields_removed"):
                print("    • Droppable fields not removed")
            if not row.get("has_data"):
                print("    • No data remaining after compression")
            if not row.get("size_reduced"):
                print("    • Size not reduced")

    print()
    print("=" * 60)
    print("Benchmark complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
