"""Dataset loading and management for benchmarking."""

import json
from pathlib import Path
from typing import List, Dict, Any


def load_squad_samples(n: int = 15) -> List[Dict[str, Any]]:
    """
    Load SQuAD-style Q&A samples.

    Args:
        n: Number of samples to load (default: 15, max: 15)

    Returns:
        List of dictionaries with keys: id, question, context, expected_answer
    """
    data_file = Path(__file__).parent / "data" / "squad_samples.json"

    with open(data_file, "r") as f:
        samples = json.load(f)

    return samples[:n]


def load_rag_scenarios(n: int = 15) -> List[Dict[str, Any]]:
    """
    Load custom RAG scenarios.

    Args:
        n: Number of scenarios to load (default: 15, max: 15)

    Returns:
        List of dictionaries with keys: scenario, query, context, expected_content
    """
    data_file = Path(__file__).parent / "data" / "rag_scenarios.json"

    with open(data_file, "r") as f:
        scenarios = json.load(f)

    return scenarios[:n]


def create_test_dataset(
    n_squad: int = 15,
    n_rag: int = 15
) -> List[Dict[str, Any]]:
    """
    Create a combined test dataset from SQuAD and RAG scenarios.

    Args:
        n_squad: Number of SQuAD samples (default: 15)
        n_rag: Number of RAG scenarios (default: 15)

    Returns:
        List of test cases with unified format:
        {
            "type": "squad" or "rag",
            "id": unique identifier,
            "query": question or query,
            "context": context text (may contain HTML, extra whitespace),
            "expected": expected answer/content
        }
    """
    test_cases = []

    # Add SQuAD samples
    squad_samples = load_squad_samples(n_squad)
    for sample in squad_samples:
        test_cases.append({
            "type": "squad",
            "id": sample["id"],
            "query": sample["question"],
            "context": sample["context"],
            "expected": sample["expected_answer"]
        })

    # Add RAG scenarios
    rag_scenarios = load_rag_scenarios(n_rag)
    for i, scenario in enumerate(rag_scenarios):
        test_cases.append({
            "type": "rag",
            "id": f"rag_{i+1:03d}",
            "query": scenario["query"],
            "context": scenario["context"],
            "expected": scenario["expected_content"],
            "scenario_name": scenario["scenario"]
        })

    return test_cases


def get_dataset_stats() -> Dict[str, Any]:
    """
    Get statistics about available datasets.

    Returns:
        Dictionary with dataset statistics
    """
    squad_samples = load_squad_samples()
    rag_scenarios = load_rag_scenarios()

    return {
        "squad_samples": len(squad_samples),
        "rag_scenarios": len(rag_scenarios),
        "total": len(squad_samples) + len(rag_scenarios)
    }


if __name__ == "__main__":
    # Test dataset loading
    print("=== Dataset Statistics ===")
    stats = get_dataset_stats()
    print(f"SQuAD samples: {stats['squad_samples']}")
    print(f"RAG scenarios: {stats['rag_scenarios']}")
    print(f"Total test cases: {stats['total']}")

    print("\n=== Sample Test Case ===")
    test_cases = create_test_dataset(n_squad=1, n_rag=1)
    print(json.dumps(test_cases[0], indent=2))
