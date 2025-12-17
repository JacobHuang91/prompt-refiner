"""Benchmark module for evaluating prompt-refiner cost-effectiveness."""

from .benchmark import Benchmark
from .datasets import create_test_dataset, get_dataset_stats, load_rag_scenarios, load_squad_samples
from .evaluators import CosineEvaluator, LLMJudgeEvaluator, evaluate_responses
from .visualizer import (
    create_all_visualizations,
    plot_cost_vs_quality,
    plot_savings_distribution,
    plot_strategy_comparison,
)

__all__ = [
    "Benchmark",
    "load_squad_samples",
    "load_rag_scenarios",
    "create_test_dataset",
    "get_dataset_stats",
    "CosineEvaluator",
    "LLMJudgeEvaluator",
    "evaluate_responses",
    "plot_cost_vs_quality",
    "plot_savings_distribution",
    "plot_strategy_comparison",
    "create_all_visualizations",
]
