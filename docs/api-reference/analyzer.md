# Analyzer Module

The Analyzer module provides utilities for measuring optimization impact and tracking token savings.

## TokenTracker

Context manager for tracking token usage before and after refinement operations.

::: prompt_refiner.analyzer.TokenTracker
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Basic Usage

```python
from prompt_refiner import TokenTracker, StripHTML, character_based_counter

refiner = StripHTML()

with TokenTracker(refiner, character_based_counter) as tracker:
    result = tracker.process("<div>Hello World</div>")

print(tracker.stats)
# {'original_tokens': 6, 'refined_tokens': 3, 'saved_tokens': 3, 'saving_percent': '50.0%'}
```

### Pipeline Tracking

```python
from prompt_refiner import (
    TokenTracker,
    StripHTML,
    NormalizeWhitespace,
    character_based_counter,
)

# Track entire pipeline
pipeline = StripHTML() | NormalizeWhitespace()

with TokenTracker(pipeline, character_based_counter) as tracker:
    result = tracker.process("<p>Hello    World   </p>")

stats = tracker.stats
print(f"Saved {stats['saved_tokens']} tokens ({stats['saving_percent']})")
# Saved 4 tokens (66.7%)
```

### Strategy Tracking

```python
from prompt_refiner import (
    TokenTracker,
    StandardStrategy,
    character_based_counter,
)

# Track preset strategies
strategy = StandardStrategy()

with TokenTracker(strategy, character_based_counter) as tracker:
    result = tracker.process("<div>Messy    input   text</div>")

print(tracker.stats)
```

## Token Counter Functions

Built-in token counting functions for different use cases.

### character_based_counter

::: prompt_refiner.analyzer.character_based_counter
    options:
      show_source: true
      heading_level: 4

Fast approximation using ~1 token ≈ 4 characters. Good for general use.

```python
from prompt_refiner import character_based_counter

tokens = character_based_counter("Hello World")
print(tokens)  # 3
```

### word_based_counter

::: prompt_refiner.analyzer.word_based_counter
    options:
      show_source: true
      heading_level: 4

Simple approximation using ~1 token ≈ 1 word. Reasonable for English text.

```python
from prompt_refiner import word_based_counter

tokens = word_based_counter("Hello World")
print(tokens)  # 2
```

### create_tiktoken_counter

::: prompt_refiner.analyzer.create_tiktoken_counter
    options:
      show_source: true
      heading_level: 4

Precise token counting using OpenAI's tiktoken. Requires optional dependency.

```python
from prompt_refiner import create_tiktoken_counter

# Requires: pip install llm-prompt-refiner[token]
counter = create_tiktoken_counter(model="gpt-4")

tokens = counter("Hello World")
print(tokens)  # Exact token count for GPT-4
```

!!! info "Optional Dependency"
    `create_tiktoken_counter` requires tiktoken to be installed:

    ```bash
    pip install llm-prompt-refiner[token]
    ```

    If tiktoken is not available, use `character_based_counter` or `word_based_counter` instead.

## Common Use Cases

### ROI Demonstration

Track token savings to demonstrate optimization value:

```python
from prompt_refiner import (
    TokenTracker,
    StandardStrategy,
    character_based_counter,
)

# Your messy input
original = "<div>Lots of HTML and   extra   whitespace</div>"

# Track optimization
strategy = StandardStrategy()
with TokenTracker(strategy, character_based_counter) as tracker:
    result = tracker.process(original)

# Show ROI
stats = tracker.stats
print(f"Original: {stats['original_tokens']} tokens")
print(f"Refined: {stats['refined_tokens']} tokens")
print(f"Saved: {stats['saved_tokens']} tokens ({stats['saving_percent']})")

# Calculate cost savings (example: $0.03 per 1K tokens)
cost_per_token = 0.03 / 1000
savings = stats['saved_tokens'] * cost_per_token
print(f"Cost savings: ${savings:.4f} per request")
```

### A/B Testing Different Strategies

Compare multiple optimization approaches:

```python
from prompt_refiner import (
    TokenTracker,
    MinimalStrategy,
    StandardStrategy,
    AggressiveStrategy,
    character_based_counter,
)

original = "Your test text here..."

# Test different strategies
strategies = {
    "Minimal": MinimalStrategy(),
    "Standard": StandardStrategy(),
    "Aggressive": AggressiveStrategy(),
}

for name, strategy in strategies.items():
    with TokenTracker(strategy, character_based_counter) as tracker:
        result = tracker.process(original)

    stats = tracker.stats
    print(f"{name}: {stats['saved_tokens']} tokens saved ({stats['saving_percent']})")
```

### Monitoring and Logging

Track optimization in production:

```python
import logging
from prompt_refiner import (
    TokenTracker,
    StandardStrategy,
    character_based_counter,
)

logger = logging.getLogger(__name__)

def process_user_input(text: str) -> str:
    strategy = StandardStrategy()

    with TokenTracker(strategy, character_based_counter) as tracker:
        result = tracker.process(text)

    stats = tracker.stats
    logger.info(
        f"Processed input: "
        f"original={stats['original_tokens']} tokens, "
        f"refined={stats['refined_tokens']} tokens, "
        f"saved={stats['saved_tokens']} tokens ({stats['saving_percent']})"
    )

    return result
```

### Packer Token Tracking

Packers have built-in token tracking support:

```python
from prompt_refiner import MessagesPacker, character_based_counter

packer = MessagesPacker(
    track_tokens=True,
    token_counter=character_based_counter,
    system="<div>You are helpful.</div>",
    context=["<p>Doc 1</p>", "<p>Doc 2</p>"],
    query="<span>What's the weather?</span>",
)

messages = packer.pack()

# Get token savings from automatic cleaning
stats = packer.token_stats
print(f"Saved {stats['saved_tokens']} tokens through automatic refinement")
```

## Choosing a Token Counter

!!! tip "Which Counter Should I Use?"

    **For development and testing:**
    - Use `character_based_counter` - fast and no dependencies

    **For production cost estimation:**
    - Use `create_tiktoken_counter(model="gpt-4")` for precise costs
    - Requires: `pip install llm-prompt-refiner[token]`

    **For simple approximation:**
    - Use `word_based_counter` for English text

## Tips

!!! tip "Context Manager Best Practice"
    Always use TokenTracker as a context manager with `with` statement:

    ```python
    with TokenTracker(refiner, counter) as tracker:
        result = tracker.process(text)
    # Stats available after processing
    stats = tracker.stats
    ```

!!! tip "Custom Token Counters"
    You can provide any callable that takes a string and returns an int:

    ```python
    def my_custom_counter(text: str) -> int:
        # Your custom logic here
        return len(text) // 3  # Example: 1 token ≈ 3 chars

    with TokenTracker(refiner, my_custom_counter) as tracker:
        result = tracker.process(text)
    ```

!!! tip "Access to Original and Result"
    TokenTracker provides properties to access the original and refined text:

    ```python
    with TokenTracker(refiner, counter) as tracker:
        result = tracker.process(text)

    print(tracker.original_text)  # Original input
    print(tracker.result)         # Refined output
    ```
