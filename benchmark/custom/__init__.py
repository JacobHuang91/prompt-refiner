"""Benchmark module for evaluating prompt-refiner cost-effectiveness."""

from .benchmark import Benchmark
from .datasets import (
    load_squad_samples,
    load_rag_scenarios,
    create_test_dataset,
    get_dataset_stats
)
from .evaluators import (
    CosineEvaluator,
    LLMJudgeEvaluator,
    evaluate_responses
)
from .visualizer import (
    plot_cost_vs_quality,
    plot_savings_distribution,
    plot_strategy_comparison,
    create_all_visualizations
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
