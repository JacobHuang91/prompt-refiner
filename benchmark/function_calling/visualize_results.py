"""
Generate visualizations for function calling benchmark results.

Creates charts showing token reduction effectiveness.
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def create_category_chart(df: pd.DataFrame, output_path: Path):
    """Create bar chart showing average reduction by category."""
    # Calculate stats by category
    category_stats = df.groupby("category").agg({
        "reduction_percent": ["mean", "count"],
        "tokens_saved": "sum"
    }).round(1)

    category_stats.columns = ["avg_reduction", "count", "total_saved"]
    category_stats = category_stats.sort_values("avg_reduction", ascending=False)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Bar chart
    colors = ["#2ecc71", "#3498db", "#f39c12", "#e74c3c"]
    bars = ax.bar(
        range(len(category_stats)),
        category_stats["avg_reduction"],
        color=colors[:len(category_stats)],
        alpha=0.8,
        edgecolor="black",
        linewidth=1.5
    )

    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, category_stats["avg_reduction"])):
        height = bar.get_height()
        count = category_stats["count"].iloc[i]
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 1,
            f"{val:.1f}%\n(n={int(count)})",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold"
        )

    # Styling
    ax.set_xlabel("Schema Category", fontsize=12, fontweight="bold")
    ax.set_ylabel("Average Token Reduction (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        "SchemaCompressor: Token Reduction by Category",
        fontsize=14,
        fontweight="bold",
        pad=20
    )
    ax.set_xticks(range(len(category_stats)))
    ax.set_xticklabels(category_stats.index, fontsize=11)
    ax.set_ylim(0, max(category_stats["avg_reduction"]) * 1.15)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    # Add overall average line
    overall_avg = df["reduction_percent"].mean()
    ax.axhline(
        overall_avg,
        color="red",
        linestyle="--",
        linewidth=2,
        alpha=0.7,
        label=f"Overall Average: {overall_avg:.1f}%"
    )
    ax.legend(loc="upper right", fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Created category chart: {output_path}")
    plt.close()


def create_top_schemas_chart(df: pd.DataFrame, output_path: Path, top_n: int = 5):
    """Create horizontal bar chart showing top schemas by reduction."""
    top_schemas = df.nlargest(top_n, "reduction_percent")

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create bars
    y_pos = range(len(top_schemas))
    bars = ax.barh(
        y_pos,
        top_schemas["reduction_percent"],
        color="#3498db",
        alpha=0.8,
        edgecolor="black",
        linewidth=1.5
    )

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, top_schemas["reduction_percent"])):
        orig = top_schemas["tokens_original"].iloc[i]
        comp = top_schemas["tokens_compressed"].iloc[i]
        ax.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}% ({orig} → {comp})",
            va="center",
            fontsize=10,
            fontweight="bold"
        )

    # Styling
    ax.set_yticks(y_pos)
    ax.set_yticklabels(
        [name.replace("_", " ").title() for name in top_schemas["schema"]],
        fontsize=11
    )
    ax.set_xlabel("Token Reduction (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        f"Top {top_n} Schemas by Token Reduction",
        fontsize=14,
        fontweight="bold",
        pad=20
    )
    ax.set_xlim(0, max(top_schemas["reduction_percent"]) * 1.15)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Created top schemas chart: {output_path}")
    plt.close()


def create_cost_savings_chart(df: pd.DataFrame, output_path: Path):
    """Create cost savings visualization."""
    # Calculate savings for different scenarios
    scenarios = [
        {"name": "Small Agent\n(5 tools)", "tools": 5, "calls_per_day": 100},
        {"name": "Medium Agent\n(10 tools)", "tools": 10, "calls_per_day": 500},
        {"name": "Large Agent\n(20 tools)", "tools": 20, "calls_per_day": 1000},
        {"name": "Enterprise\n(50 tools)", "tools": 50, "calls_per_day": 5000},
    ]

    # Average tokens per schema
    avg_tokens_original = df["tokens_original"].mean()
    avg_reduction_pct = df["reduction_percent"].mean() / 100

    # GPT-4 pricing ($0.03 per 1K input tokens)
    price_per_1k_tokens = 0.03

    monthly_savings = []
    for scenario in scenarios:
        # Calculate monthly token usage
        tokens_per_call_original = avg_tokens_original * scenario["tools"]
        tokens_per_call_compressed = tokens_per_call_original * (1 - avg_reduction_pct)
        tokens_saved_per_call = tokens_per_call_original - tokens_per_call_compressed

        # Monthly savings (30 days)
        monthly_tokens_saved = tokens_saved_per_call * scenario["calls_per_day"] * 30
        monthly_cost_savings = (monthly_tokens_saved / 1000) * price_per_1k_tokens

        monthly_savings.append(monthly_cost_savings)

    # Create chart
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ["#27ae60", "#2ecc71", "#f39c12", "#e74c3c"]
    bars = ax.bar(
        range(len(scenarios)),
        monthly_savings,
        color=colors,
        alpha=0.8,
        edgecolor="black",
        linewidth=1.5
    )

    # Add value labels
    for bar, savings in zip(bars, monthly_savings):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + max(monthly_savings) * 0.02,
            f"${savings:,.0f}/mo\n(${savings * 12:,.0f}/yr)",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )

    # Styling
    ax.set_xticks(range(len(scenarios)))
    ax.set_xticklabels([s["name"] for s in scenarios], fontsize=11)
    ax.set_ylabel("Monthly Cost Savings (USD)", fontsize=12, fontweight="bold")
    ax.set_title(
        f"Estimated Cost Savings with SchemaCompressor\n"
        f"(GPT-4, {avg_reduction_pct * 100:.1f}% avg reduction)",
        fontsize=14,
        fontweight="bold",
        pad=20
    )
    ax.set_ylim(0, max(monthly_savings) * 1.2)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Created cost savings chart: {output_path}")
    plt.close()


def main():
    """Generate all visualizations."""
    parser = argparse.ArgumentParser(description="Generate benchmark visualizations")
    parser.add_argument(
        "--results",
        type=str,
        default="results/schema_compression_results.csv",
        help="Path to results CSV"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/plots",
        help="Output directory for plots"
    )
    args = parser.parse_args()

    # Paths
    base_dir = Path(__file__).parent
    results_path = base_dir / args.results
    output_dir = base_dir / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Generating Visualizations")
    print("=" * 60)
    print(f"Results: {results_path}")
    print(f"Output: {output_dir}")
    print()

    # Load results
    df = pd.DataFrame(pd.read_csv(results_path))
    print(f"Loaded {len(df)} schema results")
    print()

    # Generate charts
    create_category_chart(df, output_dir / "reduction_by_category.png")
    create_top_schemas_chart(df, output_dir / "top_schemas.png", top_n=5)
    create_cost_savings_chart(df, output_dir / "cost_savings.png")

    print()
    print("=" * 60)
    print("Visualization complete!")
    print("=" * 60)
    print(f"Generated 3 charts in {output_dir}/")


if __name__ == "__main__":
    main()
