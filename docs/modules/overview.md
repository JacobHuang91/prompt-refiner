# Modules Overview

Prompt Refiner is organized into 5 core modules plus measurement utilities.

## The 5 Core Modules

### 1. Cleaner - Clean Dirty Data

The Cleaner module removes unwanted artifacts from your text.

**Operations:**

- **[StripHTML](../api-reference/cleaner.md#striphtml)** - Remove or convert HTML tags
- **[NormalizeWhitespace](../api-reference/cleaner.md#normalizewhitespace)** - Collapse excessive whitespace
- **[FixUnicode](../api-reference/cleaner.md#fixunicode)** - Remove problematic Unicode characters
- **[JsonCleaner](../api-reference/cleaner.md#jsoncleaner)** - Strip nulls/empties from JSON, minify

**When to use:**

- Processing web-scraped content
- Cleaning user-generated text
- Compressing JSON from RAG APIs
- Normalizing text from various sources

[Learn more →](cleaner.md){ .md-button }

### 2. Compressor - Reduce Size

The Compressor module reduces token count while preserving meaning.

**Operations:**

- **[TruncateTokens](../api-reference/compressor.md#truncatetokens)** - Smart text truncation with sentence boundaries
- **[Deduplicate](../api-reference/compressor.md#deduplicate)** - Remove similar or duplicate content

**When to use:**

- Fitting content within context windows
- Optimizing RAG retrieval results
- Reducing API costs

[Learn more →](compressor.md){ .md-button }

### 3. Scrubber - Security & Privacy

The Scrubber module protects sensitive information.

**Operations:**

- **[RedactPII](../api-reference/scrubber.md#redactpii)** - Automatically redact personally identifiable information

**When to use:**

- Before sending data to external APIs
- Compliance with privacy regulations
- Protecting user data in logs

[Learn more →](scrubber.md){ .md-button }

### 4. Packer - Context Budget Management

The Packer module manages context budgets with intelligent priority-based item selection.

**Operations:**

- **[MessagesPacker](../api-reference/packer.md#messagespacker)** - Pack items for chat completion APIs
- **[TextPacker](../api-reference/packer.md#textpacker)** - Pack items for text completion APIs

**When to use:**

- RAG applications with multiple documents
- Chatbots with conversation history
- Managing context windows with size limits
- Combining system prompts, user input, and documents

[Learn more →](packer.md){ .md-button }

### 5. Strategy - Preset Strategies

The Strategy module provides benchmark-tested preset strategies for quick setup.

**Strategies:**

- **[MinimalStrategy](../api-reference/strategy.md#minimalstrategy)** - 4.3% reduction, 98.7% quality
- **[StandardStrategy](../api-reference/strategy.md#standardstrategy)** - 4.8% reduction, 98.4% quality
- **[AggressiveStrategy](../api-reference/strategy.md#aggressivestrategy)** - 15% reduction, 96.4% quality

**When to use:**

- Quick setup without manual configuration
- Benchmark-tested optimization presets
- Extending with additional custom operations

[Learn more →](../api-reference/strategy.md){ .md-button }

---

## Measurement Utilities

### Analyzer - Measure Impact

The Analyzer module **measures optimization impact but does not transform prompts**. Use it to track token savings and demonstrate ROI.

**Operations:**

- **[CountTokens](../api-reference/analyzer.md#counttokens)** - Measure token savings and calculate ROI

**When to use:**

- Demonstrating cost savings to stakeholders
- A/B testing optimization strategies
- Monitoring optimization impact over time
- Calculating ROI for prompt optimization

[Learn more →](analyzer.md){ .md-button }

---

## Combining Modules

The real power comes from combining modules:

### Pipeline Example

```python
from prompt_refiner import (
    Refiner,
    StripHTML, NormalizeWhitespace,  # Cleaner
    TruncateTokens,                  # Compressor
    RedactPII,                       # Scrubber
    CountTokens                      # Analyzer
)

original_text = "Your text here..."
counter = CountTokens(original_text=original_text)

pipeline = (
    Refiner()
    # Clean first
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    # Then compress
    .pipe(TruncateTokens(max_tokens=1000))
    # Secure
    .pipe(RedactPII())
    # Analyze
    .pipe(counter)
)

result = pipeline.run(original_text)
print(counter.format_stats())
```

### Packer Example

```python
from prompt_refiner import (
    MessagesPacker,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    PRIORITY_HIGH,
    StripHTML
)

# Manage RAG context budget for chat APIs
packer = MessagesPacker(max_tokens=1000)

packer.add(
    "You are a helpful assistant.",
    role="system",
    priority=PRIORITY_SYSTEM
)

packer.add(
    "What is prompt-refiner?",
    role="user",
    priority=PRIORITY_USER
)

# Clean documents before packing
for doc in retrieved_docs:
    packer.add(
        doc.content,
        role="system",
        priority=PRIORITY_HIGH,
        refine_with=StripHTML()
    )

messages = packer.pack()  # Returns List[Dict] directly
```

## Module Relationships

```mermaid
graph LR
    A[Raw Input] --> B[Cleaner]
    B --> C[Compressor]
    C --> D[Scrubber]
    D --> E[Optimized Output]
    E -.-> F[Analyzer<br/>Measurement Only]

    G[Multiple Items] --> H[Packer]
    H --> I[Packed Context]
```

**Note:** Analyzer (dotted line) measures but doesn't transform the output.

## Best Practices

1. **Order matters**: Clean before compressing, compress before redacting
2. **Use Packer for RAG**: When managing multiple documents with priorities
3. **Test your pipeline**: Different inputs may need different operations
4. **Measure, don't transform**: Use CountTokens to track savings without changing output
5. **Start simple**: Begin with one module and add more as needed
