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
- **Packer**: Context budget management with specialized packers (v0.1.3+)
  - **MessagesPacker**: For chat completion APIs (OpenAI, Anthropic)
  - **TextPacker**: For text completion APIs (Llama Base, GPT-3)
  - Priority-based greedy packing algorithm
  - Automatic ChatML format overhead accounting (~4 tokens per message)
  - Grouped MARKDOWN sections for base models
  - "Entrance fee" strategy for maximum token utilization
  - Context window management for RAG applications, chatbots, and conversation history

Each module contains specialized operations that can be composed into pipelines using the `Refiner` class. The `Packer` module provides higher-level functionality for managing complex context budgets with support for both plain text and structured message formats.

## Development Philosophy

- Keep it lightweight - minimal dependencies (zero by default, optional for advanced features)
- Focus on performance - cleaning should be fast
- Make it configurable - users should control cleaning behavior
- Start simple - add features incrementally
- Graceful degradation - advanced features degrade gracefully when optional dependencies unavailable

## Version History

### v0.1.3 (Current) - Separated Packer Architecture
**New Architecture:**
- **`MessagesPacker`**: For chat completion APIs (OpenAI, Anthropic)
  - Returns `List[Dict[str, str]]` directly
  - Accurate ChatML overhead (4 tokens per message)
  - 100% token budget utilization with precise mode

- **`TextPacker`**: For text completion APIs (Llama Base, GPT-3)
  - Returns `str` directly
  - Multiple text formats: RAW, MARKDOWN, XML
  - Grouped MARKDOWN sections (INSTRUCTIONS, CONTEXT, CONVERSATION, INPUT)
  - "Entrance fee" overhead strategy for maximum token utilization

**Key Benefits:**
- Single Responsibility Principle: Each packer handles only its format
- Better type safety: Direct return types (no wrapper)
- More accurate: Each packer calculates only its overhead
- Better capacity: Grouped format + entrance fee strategy fits more content

### v0.1.2 - Optional Tiktoken Support
- Added optional tiktoken dependency for precise token counting
- Graceful degradation to character-based estimation
- 10% safety buffer in estimation mode

### v0.1.1 - ContextPacker Module
- Initial release of ContextPacker for priority-based token budget management

## Key Considerations

1. **Unicode handling**: Be careful with non-ASCII characters
2. **Whitespace**: Different types (spaces, tabs, newlines) need different handling
3. **Performance**: Process large prompts efficiently (target: < 0.5ms per 1k tokens)
4. **API stability**: v0.1.3 enhanced ContextPacker API. Keep API stable in patch versions.

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
└── packer/              # Packer module (v0.1.3+)
    ├── base.py          # Abstract base class
    ├── messages_packer.py  # Chat completion APIs
    └── text_packer.py   # Text completion APIs

tests/
├── test_refiner.py      # Pipeline tests
├── test_cleaner.py      # Cleaner module tests
├── test_compressor.py   # Compressor module tests
├── test_scrubber.py     # Scrubber module tests
├── test_analyzer.py     # Analyzer module tests
├── test_messages_packer.py  # MessagesPacker tests
└── test_text_packer.py  # TextPacker tests

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
