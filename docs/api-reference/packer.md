# Packer Module

The Packer module provides high-level operations for managing context budgets with priority-based item selection.

## ContextPacker

Intelligently pack text items into a token budget using a greedy algorithm that respects priorities and maintains insertion order.

::: prompt_refiner.packer.ContextPacker
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Priority Constants

```python
from prompt_refiner import (
    PRIORITY_SYSTEM,   # 0 - Absolute must-have (system prompts)
    PRIORITY_USER,     # 10 - Critical user input
    PRIORITY_HIGH,     # 20 - Important context (core RAG documents)
    PRIORITY_MEDIUM,   # 30 - Normal priority (general RAG documents)
    PRIORITY_LOW,      # 40 - Optional content (old conversation history)
)
```

### Token Counting Modes

!!! info "Estimation vs Precise Mode"
    ContextPacker uses the same token counting as CountTokens:

    **Estimation Mode (Default)**
    - Uses character-based approximation: ~1 token ≈ 4 characters
    - Applies **10% safety buffer** to prevent context overflow
    - Example: `max_tokens=1000` → `effective_max_tokens=900`

    ```python
    packer = ContextPacker(max_tokens=1000)  # 900 effective tokens
    ```

    **Precise Mode (Optional)**
    - Requires `tiktoken`: `pip install llm-prompt-refiner[token]`
    - Exact token counting, **no safety buffer** (100% capacity)
    - Opt-in by passing a `model` parameter

    ```python
    packer = ContextPacker(max_tokens=1000, model="gpt-4")  # 1000 effective tokens
    ```

    **Recommendation**: Use precise mode in production when you need maximum token utilization.

### Examples

#### Basic Usage

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER

packer = ContextPacker(max_tokens=500)

packer.add_item(
    "You are a helpful assistant.",
    priority=PRIORITY_SYSTEM
)

packer.add_item(
    "What is prompt-refiner?",
    priority=PRIORITY_USER
)

result = packer.pack()
```

#### RAG Application

```python
from prompt_refiner import (
    ContextPacker,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW
)

# Create packer for RAG context
packer = ContextPacker(max_tokens=1000)

# System prompt (highest priority)
packer.add_item(
    "You are a QA assistant. Answer based on the provided context.",
    priority=PRIORITY_SYSTEM
)

# User query (must include)
packer.add_item(
    "What are the main features of prompt-refiner?",
    priority=PRIORITY_USER
)

# Retrieved documents with different relevance scores
packer.add_item(
    "Prompt-refiner is a library for optimizing LLM prompts...",
    priority=PRIORITY_HIGH  # Most relevant document
)

packer.add_item(
    "The library includes 5 modules: Cleaner, Compressor...",
    priority=PRIORITY_MEDIUM  # Moderately relevant
)

packer.add_item(
    "Installation instructions and setup details...",
    priority=PRIORITY_LOW  # Less critical, may be dropped
)

# Pack into final context
final_context = packer.pack(separator="\n\n---\n\n")
```

#### JIT Refinement

Clean items before adding them for accurate token counting:

```python
from prompt_refiner import (
    ContextPacker,
    PRIORITY_HIGH,
    StripHTML,
    NormalizeWhitespace
)

packer = ContextPacker(max_tokens=500)

# Clean HTML before packing
dirty_html = "<div><p>Product information with HTML</p></div>"
packer.add_item(
    dirty_html,
    priority=PRIORITY_HIGH,
    refine_with=StripHTML()
)

# Chain multiple operations
messy_text = "<p>  Multiple   spaces   here  </p>"
packer.add_item(
    messy_text,
    priority=PRIORITY_HIGH,
    refine_with=[StripHTML(), NormalizeWhitespace()]
)

result = packer.pack()
```

#### Method Chaining

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER, PRIORITY_HIGH

result = (
    ContextPacker(max_tokens=500)
    .add_item("System prompt", priority=PRIORITY_SYSTEM)
    .add_item("User query", priority=PRIORITY_USER)
    .add_item("Context document", priority=PRIORITY_HIGH)
    .pack()
)
```

#### Inspection and Reset

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER

packer = ContextPacker(max_tokens=1000)
packer.add_item("First item", priority=PRIORITY_SYSTEM)
packer.add_item("Second item", priority=PRIORITY_USER)

# Inspect items before packing
items = packer.get_items()
for item in items:
    print(f"Priority: {item['priority']}, Tokens: {item['tokens']}")

# Pack first batch
result1 = packer.pack()

# Reset and reuse
packer.reset()
packer.add_item("New batch", priority=PRIORITY_SYSTEM)
result2 = packer.pack()
```

## How the Algorithm Works

1. **Add Phase**: Items are added with priorities and optional JIT refinement
2. **Sort Phase**: Items are sorted by priority (lower number = higher priority)
3. **Greedy Packing**: Items are selected sequentially if they fit within the token budget
4. **Order Restoration**: Selected items are restored to insertion order for natural reading flow
5. **Join Phase**: Items are joined with the specified separator

## Common Use Cases

### Chatbot with Conversation History

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER, PRIORITY_LOW

packer = ContextPacker(max_tokens=2000)

# System prompt
packer.add_item(
    "You are a helpful chatbot...",
    priority=PRIORITY_SYSTEM
)

# Recent conversation (high priority)
packer.add_item(
    "User: What's the weather?\nBot: It's sunny.",
    priority=PRIORITY_USER
)

# Older history (low priority, may be dropped)
for old_message in old_messages:
    packer.add_item(old_message, priority=PRIORITY_LOW)

# Current user input (highest priority)
packer.add_item(current_input, priority=PRIORITY_USER)

context = packer.pack()
```

### Multi-Source RAG

```python
from prompt_refiner import (
    ContextPacker,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    StripHTML
)

packer = ContextPacker(max_tokens=1500)

# System instructions
packer.add_item(system_prompt, priority=PRIORITY_SYSTEM)

# User query
packer.add_item(user_query, priority=PRIORITY_USER)

# Vector database results (cleaned)
for doc in vector_results:
    packer.add_item(
        doc.content,
        priority=PRIORITY_HIGH,
        refine_with=StripHTML()
    )

# Keyword search results (lower priority)
for doc in keyword_results:
    packer.add_item(doc.content, priority=PRIORITY_MEDIUM)

final_prompt = packer.pack()
```

### Dynamic Context Budgeting

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER, PRIORITY_HIGH

def create_prompt(system, user, documents, max_tokens):
    """Create prompt with dynamic budget allocation."""
    packer = ContextPacker(max_tokens=max_tokens)

    packer.add_item(system, priority=PRIORITY_SYSTEM)
    packer.add_item(user, priority=PRIORITY_USER)

    # Add documents by relevance score
    for doc in documents:
        priority = PRIORITY_HIGH if doc.score > 0.8 else PRIORITY_MEDIUM
        packer.add_item(doc.content, priority=priority)

    return packer.pack()
```

## Tips

!!! tip "Choose the Right Priority"
    Use priority levels to reflect importance:

    - `PRIORITY_SYSTEM`: System prompts, critical instructions
    - `PRIORITY_USER`: User input, current queries
    - `PRIORITY_HIGH`: Core context, most relevant documents
    - `PRIORITY_MEDIUM`: Supporting context, moderately relevant
    - `PRIORITY_LOW`: Optional content, old history

!!! tip "Clean Before Packing"
    Use `refine_with` to clean items before token counting for accuracy:

    ```python
    packer.add_item(
        dirty_html,
        priority=PRIORITY_HIGH,
        refine_with=StripHTML()  # Clean first!
    )
    ```

!!! tip "Monitor Dropped Items"
    In production, log what gets dropped to tune your priorities:

    ```python
    items_before = len(packer.get_items())
    result = packer.pack()
    # Compare with actual items in result
    ```

!!! tip "Account for Separators"
    The packer accounts for separator tokens automatically, but choose separators wisely:

    ```python
    # More tokens
    packer.pack(separator="\n\n---\n\n")

    # Fewer tokens
    packer.pack(separator="\n\n")
    ```
