# Contributing Guide

Thank you for your interest in contributing to Prompt Refiner!

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Getting Started

```bash
# Clone the repository
git clone https://github.com/JacobHuang91/prompt-refiner.git
cd prompt-refiner

# Install dependencies
make install

# Run tests
make test

# Format code
make format

# Run linter
make lint
```

## Project Structure

```
prompt-refiner/
├── src/prompt_refiner/     # Source code
│   ├── cleaner/           # Cleaner module
│   ├── compressor/        # Compressor module
│   ├── scrubber/          # Scrubber module
│   └── analyzer/          # Analyzer module
├── tests/                 # Test files
├── examples/              # Example scripts
└── docs/                  # Documentation
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following existing patterns
- Add tests for new functionality
- Update documentation if needed

### 3. Run Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_cleaner.py -v
```

### 4. Format Code

```bash
make format
```

### 5. Commit Changes

```bash
git add .
git commit -m "Add feature: description"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style

- Follow PEP 8
- Use type hints
- Write clear docstrings (Google style)
- Keep functions small and focused

### Example

```python
def process(self, text: str) -> str:
    """
    Process the input text.

    Args:
        text: The input text to process

    Returns:
        The processed text
    """
    return text.strip()
```

## Testing

- Write tests for all new features
- Aim for high test coverage
- Test edge cases

```python
def test_strip_html():
    operation = StripHTML()
    result = operation.process("<p>Hello</p>")
    assert result == "Hello"
```

## Documentation

- Update relevant documentation files
- Add examples for new features
- Keep API reference up to date (auto-generated from docstrings)

### Building Docs Locally

```bash
make docs-serve
```

Then visit http://127.0.0.1:8000

## Questions?

- [Open an issue](https://github.com/JacobHuang91/prompt-refiner/issues)
- [Start a discussion](https://github.com/JacobHuang91/prompt-refiner/discussions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
