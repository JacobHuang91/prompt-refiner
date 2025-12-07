# Examples

Practical examples for each module in Prompt Refiner.

## By Module

### Cleaner Examples

- **[HTML Cleaning](html-cleaning.md)** - Strip HTML tags and convert to Markdown
- **[JSON Cleaning](json-cleaning.md)** - Strip nulls/empties from JSON for RAG APIs
- See more in: [Cleaner Module](../modules/cleaner.md)

### Compressor Examples

- **[Deduplication](deduplication.md)** - Remove duplicate content from RAG results
- See more in: [Compressor Module](../modules/compressor.md)

### Scrubber Examples

- **[PII Redaction](pii-redaction.md)** - Redact sensitive information
- See more in: [Scrubber Module](../modules/scrubber.md)

### Analyzer Examples

- **[Token Analysis](token-analysis.md)** - Calculate token savings and ROI
- See more in: [Analyzer Module](../modules/analyzer.md)

### Packer Examples (Advanced)

- **[Context Budget Management](packer.md)** - RAG applications, chatbots, and conversation history
- See more in: [Packer Module](../modules/packer.md)

### Complete Examples

- **[Complete Pipeline](complete-pipeline.md)** - Full optimization with all modules

## Running Examples Locally

All examples are available in the [`examples/`](https://github.com/JacobHuang91/prompt-refiner/tree/main/examples) directory:

```bash
# Clone the repository
git clone https://github.com/JacobHuang91/prompt-refiner.git
cd prompt-refiner

# Install dependencies
make install

# Run an example
python examples/packer/messages.py
```

## Need Help?

- [Getting Started Guide](../getting-started.md)
- [API Reference](../api-reference/index.md)
- [Report Issues](https://github.com/JacobHuang91/prompt-refiner/issues)
