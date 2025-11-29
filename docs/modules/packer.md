# Packer Module

Intelligently manage context budgets with priority-based item packing for RAG applications and context window management.

## ContextPacker Operation

Pack text items into a token budget using a greedy algorithm that respects priorities and maintains insertion order.

### Basic Usage

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER, PRIORITY_HIGH

# Create packer with token budget
packer = ContextPacker(max_tokens=1000)

# Add items with priorities
packer.add_item(
    "You are a helpful assistant.",
    priority=PRIORITY_SYSTEM
)

packer.add_item(
    "What are the key features?",
    priority=PRIORITY_USER
)

packer.add_item(
    "Product documentation: Feature A, B, C...",
    priority=PRIORITY_HIGH
)

# Pack items into budget
result = packer.pack(separator="\n\n")
```

### Priority Constants

```python
from prompt_refiner import (
    PRIORITY_SYSTEM,   # 0 - Absolute must-have (system prompts)
    PRIORITY_USER,     # 10 - Critical user input
    PRIORITY_HIGH,     # 20 - Important context (core RAG docs)
    PRIORITY_MEDIUM,   # 30 - Normal priority (general RAG docs)
    PRIORITY_LOW,      # 40 - Optional content (old history)
)
```

### RAG Example

```python
from prompt_refiner import (
    ContextPacker,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    StripHTML
)

packer = ContextPacker(max_tokens=500)

# System prompt (must include)
packer.add_item(
    "Answer based on the provided context.",
    priority=PRIORITY_SYSTEM
)

# User query (must include)
packer.add_item(
    "What is prompt-refiner?",
    priority=PRIORITY_USER
)

# Retrieved documents with cleaning
packer.add_item(
    "<p>Prompt-refiner is a library...</p>",
    priority=PRIORITY_HIGH,
    refine_with=StripHTML()  # Clean before packing
)

packer.add_item(
    "Additional context about features...",
    priority=PRIORITY_MEDIUM
)

# Pack into final context
context = packer.pack()
```

### JIT Refinement

Apply operations to items before adding them to the packer:

```python
from prompt_refiner import (
    ContextPacker,
    PRIORITY_HIGH,
    StripHTML,
    NormalizeWhitespace
)

packer = ContextPacker(max_tokens=200)

dirty_html = "<div>  Lots   of   spaces  </div>"

# Clean before packing for accurate token counting
packer.add_item(
    dirty_html,
    priority=PRIORITY_HIGH,
    refine_with=[StripHTML(), NormalizeWhitespace()]
)

result = packer.pack()
```

### Method Chaining

```python
result = (
    ContextPacker(max_tokens=500)
    .add_item("System prompt", priority=PRIORITY_SYSTEM)
    .add_item("User query", priority=PRIORITY_USER)
    .add_item("Context doc", priority=PRIORITY_HIGH)
    .pack()
)
```

### Inspection

Check what items were added before packing:

```python
packer = ContextPacker(max_tokens=1000)
packer.add_item("Item 1", priority=PRIORITY_SYSTEM)
packer.add_item("Item 2", priority=PRIORITY_USER)

items = packer.get_items()
for item in items:
    print(f"Priority: {item['priority']}, Tokens: {item['tokens']}")
```

### Reset

Clear all items and reuse the packer:

```python
packer = ContextPacker(max_tokens=1000)
packer.add_item("First batch", priority=PRIORITY_HIGH)
result1 = packer.pack()

# Clear and reuse
packer.reset()
packer.add_item("Second batch", priority=PRIORITY_HIGH)
result2 = packer.pack()
```

## How It Works

1. **Add items** with priorities and optional JIT refinement
2. **Sort by priority** (lower number = higher priority)
3. **Greedy packing** - select items that fit within budget
4. **Restore insertion order** for natural reading flow
5. **Join with separator** and return packed text

## Use Cases

- **RAG Applications**: Pack retrieved documents into context budget
- **Chatbots**: Manage conversation history with priorities
- **Context Window Management**: Fit critical information within model limits
- **Multi-source Data**: Combine system prompts, user input, and documents

[Full API Reference →](../api-reference/packer.md){ .md-button }
[View Examples](https://github.com/JacobHuang91/prompt-refiner/tree/main/examples/packer){ .md-button }
