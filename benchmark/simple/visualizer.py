"""Visualization tools for benchmark results."""

from typing import Dict, Any, List
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import pandas as pd


def plot_cost_vs_quality(
    results_df: pd.DataFrame,
    output_path: str = "benchmark_results.png"
) -> None:
    """
    Create scatter plot showing token reduction vs quality score.

    Args:
        results_df: DataFrame with columns: strategy, token_reduction, quality_score
        output_path: Path to save the plot
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Color map for strategies
    strategy_colors = {
        "minimal": "#2ecc71",
        "standard": "#3498db",
        "aggressive": "#e74c3c"
    }

    # Plot each strategy
    for strategy in results_df["strategy"].unique():
        strategy_data = results_df[results_df["strategy"] == strategy]
        ax.scatter(
            strategy_data["token_reduction"],
            strategy_data["quality_cosine"],
            c=strategy_colors.get(strategy, "#95a5a6"),
            label=strategy.capitalize(),
            alpha=0.6,
            s=100
        )

    # Add mean points
    for strategy in results_df["strategy"].unique():
        strategy_data = results_df[results_df["strategy"] == strategy]
        mean_reduction = strategy_data["token_reduction"].mean()
        mean_quality = strategy_data["quality_cosine"].mean()
        ax.scatter(
            mean_reduction,
            mean_quality,
            c=strategy_colors.get(strategy, "#95a5a6"),
            marker="*",
            s=400,
            edgecolors="black",
            linewidths=2,
            label=f"{strategy.capitalize()} (Mean)"
        )

    # Target zones
    ax.axhline(y=0.95, color="green", linestyle="--", alpha=0.3, label="Quality Target (0.95)")
    ax.axvline(x=15, color="blue", linestyle="--", alpha=0.3, label="Token Reduction Target (15%)")

    # Labels and formatting
    ax.set_xlabel("Token Reduction (%)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Quality Score (Cosine Similarity)", fontsize=12, fontweight="bold")
    ax.set_title("Cost Reduction vs Quality Maintenance", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.2)
    ax.legend(loc="best", fontsize=10)

    # Set axis limits
    ax.set_xlim(0, max(results_df["token_reduction"]) * 1.1)
    ax.set_ylim(min(0.85, results_df["quality_cosine"].min() - 0.02), 1.02)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Saved cost vs quality plot to {output_path}")


def plot_savings_distribution(
    results_df: pd.DataFrame,
    output_path: str = "token_savings_dist.png"
) -> None:
    """
    Create histogram showing distribution of token savings.

    Args:
        results_df: DataFrame with columns: strategy, token_reduction
        output_path: Path to save the plot
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    strategies = ["minimal", "standard", "aggressive"]
    colors = ["#2ecc71", "#3498db", "#e74c3c"]

    for idx, strategy in enumerate(strategies):
        ax = axes[idx]
        strategy_data = results_df[results_df["strategy"] == strategy]

        if len(strategy_data) == 0:
            continue

        # Histogram
        ax.hist(
            strategy_data["token_reduction"],
            bins=10,
            color=colors[idx],
            alpha=0.7,
            edgecolor="black"
        )

        # Mean line
        mean_reduction = strategy_data["token_reduction"].mean()
        ax.axvline(
            mean_reduction,
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Mean: {mean_reduction:.1f}%"
        )

        # Labels
        ax.set_title(f"{strategy.capitalize()} Strategy", fontweight="bold")
        ax.set_xlabel("Token Reduction (%)")
        ax.set_ylabel("Frequency")
        ax.legend()
        ax.grid(True, alpha=0.2, axis="y")

    plt.suptitle("Token Savings Distribution by Strategy", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Saved savings distribution plot to {output_path}")


def plot_strategy_comparison(
    summary_stats: Dict[str, Dict[str, float]],
    output_path: str = "strategy_comparison.png"
) -> None:
    """
    Create bar chart comparing strategies across metrics.

    Args:
        summary_stats: Dict with structure {strategy: {metric: value}}
        output_path: Path to save the plot
    """
    strategies = list(summary_stats.keys())
    metrics = ["token_reduction", "quality_cosine", "quality_judge"]
    metric_labels = ["Token Reduction (%)", "Quality (Cosine)", "Judge Approval (%)"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = {"minimal": "#2ecc71", "standard": "#3498db", "aggressive": "#e74c3c"}

    for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
        ax = axes[idx]

        values = [summary_stats[s].get(metric, 0) for s in strategies]
        bars = ax.bar(
            strategies,
            values,
            color=[colors[s] for s in strategies],
            alpha=0.7,
            edgecolor="black"
        )

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.1f}",
                ha="center",
                va="bottom",
                fontweight="bold"
            )

        ax.set_title(label, fontweight="bold")
        ax.set_ylabel(label.split("(")[0].strip())
        ax.grid(True, alpha=0.2, axis="y")

        # Set y-axis limits based on metric
        if "Reduction" in label:
            ax.set_ylim(0, max(values) * 1.2)
        else:
            ax.set_ylim(0, max(1.0, max(values)) * 1.1)

    plt.suptitle("Strategy Comparison", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Saved strategy comparison plot to {output_path}")


def create_all_visualizations(
    results_df: pd.DataFrame,
    summary_stats: Dict[str, Dict[str, float]],
    output_dir: str = "."
) -> None:
    """
    Create all benchmark visualizations.

    Args:
        results_df: Full results DataFrame
        summary_stats: Summary statistics by strategy
        output_dir: Directory to save plots
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("\n📊 Generating visualizations...")

    plot_cost_vs_quality(
        results_df,
        str(output_path / "benchmark_results.png")
    )

    plot_savings_distribution(
        results_df,
        str(output_path / "token_savings_dist.png")
    )

    plot_strategy_comparison(
        summary_stats,
        str(output_path / "strategy_comparison.png")
    )

    print("✅ All visualizations created successfully!")


if __name__ == "__main__":
    print("Visualizer module loaded successfully")
    print("Available functions: plot_cost_vs_quality, plot_savings_distribution, plot_strategy_comparison")
