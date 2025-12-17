"""
Benchmark SchemaCompressor on real-world tool schemas.

Tests SchemaCompressor effectiveness on 20 tool schemas from
OpenAI, Anthropic, and popular APIs. Measures token reduction
while verifying protocol field preservation.

Usage:
    python benchmark_schemas.py [--output OUTPUT_DIR]
"""

import argparse
import json
from glob import glob
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import tiktoken

from prompt_refiner.tools import SchemaCompressor


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens using tiktoken."""
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))


def categorize_schema(tokens_original: int) -> str:
    """Categorize schema by complexity based on token count."""
    if tokens_original < 200:
        return "Simple"
    elif tokens_original < 500:
        return "Medium"
    elif tokens_original < 1000:
        return "Complex"
    else:
        return "Very Verbose"


def verify_protocol_fields(original: Dict, compressed: Dict) -> Dict[str, bool]:
    """Verify that protocol fields are preserved in compressed schema."""
    checks = {}

    # Check function name
    checks["name_preserved"] = (
        original.get("function", {}).get("name")
        == compressed.get("function", {}).get("name")
    )

    # Check parameters type
    checks["type_preserved"] = (
        original.get("function", {}).get("parameters", {}).get("type")
        == compressed.get("function", {}).get("parameters", {}).get("type")
    )

    # Check required fields
    orig_required = set(
        original.get("function", {}).get("parameters", {}).get("required", [])
    )
    comp_required = set(
        compressed.get("function", {}).get("parameters", {}).get("required", [])
    )
    checks["required_preserved"] = orig_required == comp_required

    # Check property types
    orig_props = original.get("function", {}).get("parameters", {}).get("properties", {})
    comp_props = compressed.get("function", {}).get("parameters", {}).get("properties", {})

    type_preserved = True
    for prop_name, prop_def in orig_props.items():
        if prop_name not in comp_props:
            type_preserved = False
            break
        if prop_def.get("type") != comp_props[prop_name].get("type"):
            type_preserved = False
            break
        if "enum" in prop_def:
            if prop_def["enum"] != comp_props[prop_name].get("enum"):
                type_preserved = False
                break

    checks["property_types_preserved"] = type_preserved
    checks["all_checks_passed"] = all(checks.values())

    return checks


def benchmark_single_schema(
    schema_path: str,
    compressor: SchemaCompressor
) -> Dict[str, Any]:
    """Benchmark SchemaCompressor on a single schema."""
    # Load original schema
    with open(schema_path) as f:
        schema_original = json.load(f)

    # Compress schema
    schema_compressed = compressor.process(schema_original)

    # Count tokens
    tokens_original = count_tokens(json.dumps(schema_original))
    tokens_compressed = count_tokens(json.dumps(schema_compressed))
    tokens_saved = tokens_original - tokens_compressed
    reduction_pct = (tokens_saved / tokens_original * 100) if tokens_original > 0 else 0

    # Verify protocol field preservation
    verification = verify_protocol_fields(schema_original, schema_compressed)

    # Categorize
    category = categorize_schema(tokens_original)

    return {
        "schema": Path(schema_path).stem,
        "category": category,
        "tokens_original": tokens_original,
        "tokens_compressed": tokens_compressed,
        "tokens_saved": tokens_saved,
        "reduction_percent": round(reduction_pct, 1),
        **verification
    }


def generate_before_after_examples(
    results_df: pd.DataFrame,
    schemas_dir: Path,
    output_dir: Path,
    top_n: int = 3
) -> None:
    """Generate before/after examples for top N schemas by reduction."""
    top_schemas = results_df.nlargest(top_n, "reduction_percent")

    examples_md = "# Schema Compression Examples\n\n"
    examples_md += "Top 3 schemas by token reduction percentage:\n\n"

    compressor = SchemaCompressor()

    for idx, row in top_schemas.iterrows():
        schema_name = row["schema"]
        schema_path = schemas_dir / f"{schema_name}.json"

        # Load original
        with open(schema_path) as f:
            original = json.load(f)

        # Compress
        compressed = compressor.process(original)

        examples_md += f"## {idx + 1}. {schema_name}\n\n"
        examples_md += f"**Token Reduction**: {row['tokens_original']} → {row['tokens_compressed']} "
        examples_md += f"({row['reduction_percent']}% reduction)\n\n"
        examples_md += f"**Category**: {row['category']}\n\n"

        # Show function description comparison
        orig_desc = original.get("function", {}).get("description", "")
        comp_desc = compressed.get("function", {}).get("description", "")

        examples_md += "**Original Description**:\n"
        examples_md += f"```\n{orig_desc[:200]}{'...' if len(orig_desc) > 200 else ''}\n```\n\n"
        examples_md += "**Compressed Description**:\n"
        examples_md += f"```\n{comp_desc[:200]}{'...' if len(comp_desc) > 200 else ''}\n```\n\n"

        # Show one parameter comparison
        orig_params = original.get("function", {}).get("parameters", {}).get("properties", {})
        comp_params = compressed.get("function", {}).get("parameters", {}).get("properties", {})

        if orig_params:
            first_param = list(orig_params.keys())[0]
            examples_md += f"**Example Parameter** (`{first_param}`):\n\n"
            examples_md += f"- Original description length: {len(orig_params[first_param].get('description', ''))} chars\n"
            examples_md += f"- Compressed description length: {len(comp_params[first_param].get('description', ''))} chars\n"
            examples_md += f"- Type preserved: {orig_params[first_param].get('type') == comp_params[first_param].get('type')}\n"

        examples_md += "\n---\n\n"

    # Save examples
    examples_path = output_dir / "before_after_examples.md"
    with open(examples_path, "w") as f:
        f.write(examples_md)

    print(f"✓ Generated before/after examples: {examples_path}")


def main():
    """Run schema compression benchmark."""
    parser = argparse.ArgumentParser(
        description="Benchmark SchemaCompressor on real-world tool schemas"
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
    schemas_dir = base_dir / "data" / "schemas"
    output_dir = base_dir / args.output
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Schema Compression Benchmark")
    print("=" * 60)
    print(f"Schemas directory: {schemas_dir}")
    print(f"Output directory: {output_dir}")
    print()

    # Find all schema files
    schema_files = sorted(glob(str(schemas_dir / "*.json")))
    print(f"Found {len(schema_files)} schema files")
    print()

    # Initialize compressor
    compressor = SchemaCompressor()

    # Benchmark each schema
    results = []
    print("Benchmarking schemas:")
    print("-" * 60)

    for schema_path in schema_files:
        schema_name = Path(schema_path).stem
        result = benchmark_single_schema(schema_path, compressor)
        results.append(result)

        status = "✓" if result["all_checks_passed"] else "✗"
        print(
            f"{status} {schema_name:40} | "
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
    print(f"Total schemas tested: {len(df)}")
    print(f"Average token reduction: {df['reduction_percent'].mean():.1f}%")
    print(f"Median token reduction: {df['reduction_percent'].median():.1f}%")
    print(f"Min reduction: {df['reduction_percent'].min():.1f}%")
    print(f"Max reduction: {df['reduction_percent'].max():.1f}%")
    print(f"Total tokens saved: {df['tokens_saved'].sum():,}")
    print(f"All protocol checks passed: {df['all_checks_passed'].all()}")
    print()

    # Save results to CSV
    csv_path = output_dir / "schema_compression_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ Results saved to: {csv_path}")
    print()

    # Generate before/after examples
    generate_before_after_examples(df, schemas_dir, output_dir, top_n=3)
    print()

    # Verification summary
    if df["all_checks_passed"].all():
        print("✓ All protocol fields preserved across all schemas!")
    else:
        failed = df[~df["all_checks_passed"]]
        print(f"✗ Protocol verification failed for {len(failed)} schemas:")
        for idx, row in failed.iterrows():
            print(f"  - {row['schema']}")

    print()
    print("=" * 60)
    print("Benchmark complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
