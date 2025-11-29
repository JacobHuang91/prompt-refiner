# Prompt Refiner - Project Context

This document provides context for Claude Code and developers working on this project.

## Project Purpose

Prompt Refiner is a Python library designed to optimize LLM prompts by cleaning and reducing unnecessary tokens. This helps users:

- Lower API costs by reducing token count
- Improve prompt quality through normalization
- Maintain consistent input formatting

## Architecture

The library is organized into 5 core modules:

- **Cleaner**: Operations for cleaning dirty data (HTML, whitespace, Unicode)
- **Compressor**: Operations for reducing prompt size (truncation, deduplication)
- **Scrubber**: Operations for security and privacy (PII redaction)
- **Analyzer**: Operations for analyzing and reporting on optimization (token counting)
- **Packer**: High-level context budget management (context window packing with priorities for RAG)

Each module contains specialized operations that can be composed into pipelines using the `Refiner` class. The `Packer` module provides higher-level functionality for managing complex context budgets with priority-based selection.

## Development Philosophy

- Keep it lightweight - minimal dependencies (zero by default, optional for advanced features)
- Focus on performance - cleaning should be fast
- Make it configurable - users should control cleaning behavior
- Start simple - add features incrementally
- Graceful degradation - advanced features degrade gracefully when optional dependencies unavailable

## Key Considerations

1. **Unicode handling**: Be careful with non-ASCII characters
2. **Whitespace**: Different types (spaces, tabs, newlines) need different handling
3. **Performance**: Process large prompts efficiently (target: < 0.5ms per 1k tokens)
4. **Backward compatibility**: Don't break existing functionality when adding features

## Technology Stack

- Python 3.9+
- uv for package management
- pytest for testing
- ruff for linting and formatting

### Optional Dependencies

- **tiktoken** (optional): For precise token counting
  - Install with: `pip install llm-prompt-refiner[token]`
  - Opt-in by passing `model` parameter to CountTokens or ContextPacker
  - Falls back to character-based estimation if unavailable

## Code Style

- Follow PEP 8
- Use type hints
- Keep functions small and focused
- Write clear docstrings

## Project Structure

```
src/prompt_refiner/
├── __init__.py          # Main exports
├── refiner.py           # Pipeline builder
├── operation.py         # Base operation class
├── cleaner/             # Cleaner module
│   ├── html.py
│   ├── whitespace.py
│   └── unicode.py
├── compressor/          # Compressor module
│   ├── truncate.py
│   └── deduplicate.py
├── scrubber/            # Scrubber module
│   └── pii.py
├── analyzer/            # Analyzer module
│   └── counter.py
└── packer/              # Packer module
    └── context_packer.py

tests/
├── test_refiner.py      # Pipeline tests
├── test_cleaner.py      # Cleaner module tests
├── test_compressor.py   # Compressor module tests
├── test_scrubber.py     # Scrubber module tests
├── test_analyzer.py     # Analyzer module tests
└── test_packer.py       # Packer module tests

examples/
├── cleaner/             # Cleaner examples
├── compressor/          # Compressor examples
├── scrubber/            # Scrubber examples
├── analyzer/            # Analyzer examples
├── packer/              # Packer examples
└── all_modules_demo.py  # Complete demo

benchmark/
├── README.md            # Index of all benchmarks
├── latency/             # Latency/performance benchmark
│   ├── benchmark.py     # Performance measurement script
│   └── README.md        # Latency benchmark documentation
└── custom/              # Quality/cost A/B testing benchmark
    ├── benchmark.py     # Main orchestrator
    ├── datasets.py      # Test data loader
    ├── evaluators.py    # Quality metrics (cosine + LLM judge)
    ├── visualizer.py    # Matplotlib plots
    ├── data/            # 30 curated test cases
    │   ├── squad_samples.json
    │   └── rag_scenarios.json
    └── README.md        # Full benchmark documentation
```

## Testing & Benchmarking

### Unit Tests
- Unit tests for all operations organized by module
- Edge case testing (empty strings, Unicode, very long inputs)
- Tests are separated by module for better organization

### Benchmarks
- **Latency Benchmark**: Measures processing overhead (< 0.5ms per 1k tokens)
- **Quality/Cost Benchmark**: Measures token reduction (4-15%) and response quality (96-99%)

## Future Vision

This will eventually become a product offering prompt optimization as a service. The library is the foundation for that product.
