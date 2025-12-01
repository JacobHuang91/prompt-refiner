.PHONY: install test lint format clean build help docs-serve docs-build docs-deploy docs-deploy-version version

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies using uv"
	@echo "  make test       - Run tests with pytest"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with ruff"
	@echo "  make clean      - Remove build artifacts and cache"
	@echo "  make build      - Build the package"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-serve         - Start local documentation server"
	@echo "  make docs-build         - Build documentation site"
	@echo "  make docs-deploy        - Deploy latest docs to GitHub Pages"
	@echo "  make docs-deploy-version VERSION=x.y.z - Deploy specific version"
	@echo ""
	@echo "Release:"
	@echo "  make version            - Show current version"

install:
	uv pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=src/prompt_refiner --cov-report=term-missing

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/ || true

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type f -name "*.py,cover" -delete
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	uv build

# Documentation commands
docs-serve:
	@echo "Starting MkDocs dev server..."
	uv run mkdocs serve

docs-build:
	@echo "Building documentation..."
	uv run mkdocs build

docs-deploy:
	@echo "Deploying latest docs to GitHub Pages..."
	uv run mike deploy --push --update-aliases latest

docs-deploy-version:
	@echo "Usage: make docs-deploy-version VERSION=0.1.0"
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION not specified. Use: make docs-deploy-version VERSION=0.1.0"; \
		exit 1; \
	fi
	@echo "Deploying version $(VERSION)..."
	uv run mike deploy --push --update-aliases $(VERSION)

# Release commands
version:
	@echo "Current version:"
	@grep '^version = ' pyproject.toml | cut -d'"' -f2
