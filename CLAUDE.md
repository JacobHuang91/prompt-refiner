# Prompt Groomer - Project Context

This document provides context for Claude Code and developers working on this project.

## Project Purpose

Prompt Groomer is a Python library designed to optimize LLM prompts by cleaning and reducing unnecessary tokens. This helps users:

- Lower API costs by reducing token count
- Improve prompt quality through normalization
- Maintain consistent input formatting

## Architecture

The library is organized into 4 core modules:

- **Cleaner**: Operations for cleaning dirty data (HTML, whitespace, Unicode)
- **Compressor**: Operations for reducing prompt size (truncation, deduplication)
- **Scrubber**: Operations for security and privacy (PII redaction)
- **Analyzer**: Operations for analyzing and reporting on optimization (token counting)

Each module contains specialized operations that can be composed into pipelines using the `Groomer` class.

## Development Philosophy

- Keep it lightweight - minimal dependencies
- Focus on performance - cleaning should be fast
- Make it configurable - users should control cleaning behavior
- Start simple - add features incrementally

## Key Considerations

1. **Unicode handling**: Be careful with non-ASCII characters
2. **Whitespace**: Different types (spaces, tabs, newlines) need different handling
3. **Performance**: Process large prompts efficiently
4. **Backward compatibility**: Don't break existing functionality when adding features

## Technology Stack

- Python 3.9+
- uv for package management
- pytest for testing
- ruff for linting and formatting

## Code Style

- Follow PEP 8
- Use type hints
- Keep functions small and focused
- Write clear docstrings

## Project Structure

```
src/prompt_groomer/
├── __init__.py          # Main exports
├── groomer.py           # Pipeline builder
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
└── analyzer/            # Analyzer module
    └── counter.py

tests/
├── test_groomer.py      # Pipeline tests
├── test_cleaner.py      # Cleaner module tests
├── test_compressor.py   # Compressor module tests
├── test_scrubber.py     # Scrubber module tests
└── test_analyzer.py     # Analyzer module tests

examples/
├── cleaner/             # Cleaner examples
├── compressor/          # Compressor examples
├── scrubber/            # Scrubber examples
├── analyzer/            # Analyzer examples
└── all_modules_demo.py  # Complete demo
```

## Testing

- Unit tests for all operations organized by module
- Edge case testing (empty strings, Unicode, very long inputs)
- Performance benchmarks for large inputs
- Tests are separated by module for better organization

## Future Vision

This will eventually become a product offering prompt optimization as a service. The library is the foundation for that product.
