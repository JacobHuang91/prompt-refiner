# Packer Module API Reference

The Packer module provides specialized packers for managing context budgets with priority-based item selection. **Version 0.1.3+** introduces two specialized packers following the Single Responsibility Principle.

## MessagesPacker

Optimized for chat completion APIs (OpenAI, Anthropic). Returns `List[Dict[str, str]]` directly.

::: prompt_refiner.packer.MessagesPacker
    options:
      show_source: true
      members_order: source
      heading_level: 3

## TextPacker

Optimized for text completion APIs (Llama Base, GPT-3). Returns `str` directly with multiple text formats.

::: prompt_refiner.packer.TextPacker
    options:
      show_source: true
      members_order: source
      heading_level: 3

## BasePacker

Abstract base class providing common packer functionality. You typically won't use this directly.

::: prompt_refiner.packer.BasePacker
    options:
      show_source: true
      members_order: source
      heading_level: 3

## Constants

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

### Overhead Constants

```python
from prompt_refiner import (
    PER_MESSAGE_OVERHEAD,  # 4 tokens - ChatML format overhead per message
    PER_REQUEST_OVERHEAD,  # 3 tokens - Base request overhead (reserved for future use)
)
```

These constants reflect the approximate token overhead for OpenAI's ChatML format (`<|im_start|>role\n...\n<|im_end|>`).

## TextFormat Enum

```python
from prompt_refiner import TextFormat

TextFormat.RAW       # No delimiters, simple concatenation
TextFormat.MARKDOWN  # Use ### ROLE: headers (grouped sections in v0.1.3+)
TextFormat.XML       # Use <role>content</role> tags
```

## Token Counting Modes

!!! info "Estimation vs Precise Mode"
    Both MessagesPacker and TextPacker use the same token counting as CountTokens:

    **Estimation Mode (Default)**
    - Uses character-based approximation: ~1 token ≈ 4 characters
    - Applies **10% safety buffer** to prevent context overflow
    - Example: `max_tokens=1000` → `effective_max_tokens=900`

    ```python
    packer = MessagesPacker(max_tokens=1000)  # 900 effective tokens
    ```

    **Precise Mode (Optional)**
    - Requires `tiktoken`: `pip install llm-prompt-refiner[token]`
    - Exact token counting, **no safety buffer** (100% capacity)
    - Opt-in by passing a `model` parameter

    ```python
    packer = MessagesPacker(max_tokens=1000, model="gpt-4")  # 1000 effective tokens
    ```

    **Recommendation**: Use precise mode in production when you need maximum token utilization.

## MessagesPacker Examples

### Basic Usage

```python
from prompt_refiner import MessagesPacker, PRIORITY_SYSTEM, PRIORITY_USER

packer = MessagesPacker(max_tokens=500)

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

messages = packer.pack()  # List[Dict[str, str]]
# Use directly: openai.chat.completions.create(messages=messages)
```

### RAG with Conversation History

```python
from prompt_refiner import (
    MessagesPacker,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    StripHTML
)

packer = MessagesPacker(max_tokens=1000)

# System prompt (must include)
packer.add(
    "Answer based on provided context.",
    role="system",
    priority=PRIORITY_SYSTEM
)

# RAG documents with JIT cleaning
packer.add(
    "<p>Prompt-refiner is a library...</p>",
    role="system",
    priority=PRIORITY_HIGH,
    refine_with=StripHTML()
)

# Old conversation history (can be dropped if needed)
old_messages = [
    {"role": "user", "content": "What is this library?"},
    {"role": "assistant", "content": "It's a tool for optimizing prompts."}
]
packer.add_messages(old_messages, priority=PRIORITY_LOW)

# Current query (must include)
packer.add(
    "How does it reduce costs?",
    role="user",
    priority=PRIORITY_USER
)

messages = packer.pack()
```

## TextPacker Examples

### Basic Usage

```python
from prompt_refiner import TextPacker, TextFormat, PRIORITY_SYSTEM, PRIORITY_USER

packer = TextPacker(
    max_tokens=500,
    text_format=TextFormat.MARKDOWN
)

packer.add(
    "You are a QA assistant.",
    role="system",
    priority=PRIORITY_SYSTEM
)

packer.add(
    "Context: Prompt-refiner is a library...",
    priority=PRIORITY_HIGH
)

packer.add(
    "What is prompt-refiner?",
    role="user",
    priority=PRIORITY_USER
)

prompt = packer.pack()  # str
# Use with: completion.create(prompt=prompt)
```

### Text Format Comparison

```python
from prompt_refiner import TextPacker, TextFormat, PRIORITY_SYSTEM, PRIORITY_USER

# RAW format (simple concatenation)
packer = TextPacker(max_tokens=200, text_format=TextFormat.RAW)
packer.add("System prompt", role="system", priority=PRIORITY_SYSTEM)
packer.add("User query", role="user", priority=PRIORITY_USER)
prompt = packer.pack()
# Output:
# System prompt
#
# User query

# MARKDOWN format (grouped sections in v0.1.3+)
packer = TextPacker(max_tokens=200, text_format=TextFormat.MARKDOWN)
packer.add("System prompt", role="system", priority=PRIORITY_SYSTEM)
packer.add("Doc 1", priority=PRIORITY_HIGH)
packer.add("Doc 2", priority=PRIORITY_HIGH)
packer.add("User query", role="user", priority=PRIORITY_USER)
prompt = packer.pack()
# Output:
# ### INSTRUCTIONS:
# System prompt
#
# ### CONTEXT:
# - Doc 1
# - Doc 2
#
# ### INPUT:
# User query

# XML format
packer = TextPacker(max_tokens=200, text_format=TextFormat.XML)
packer.add("System prompt", role="system", priority=PRIORITY_SYSTEM)
packer.add("User query", role="user", priority=PRIORITY_USER)
prompt = packer.pack()
# Output:
# <system>
# System prompt
# </system>
#
# <user>
# User query
# </user>
```

## Common Features

### JIT Refinement

Both packers support Just-In-Time refinement:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace

# Single operation
packer.add(
    "<div>HTML content</div>",
    priority=PRIORITY_HIGH,
    refine_with=StripHTML()
)

# Multiple operations
packer.add(
    "<p>  Messy   HTML  </p>",
    priority=PRIORITY_HIGH,
    refine_with=[StripHTML(), NormalizeWhitespace()]
)
```

### Method Chaining

```python
from prompt_refiner import MessagesPacker, PRIORITY_SYSTEM, PRIORITY_USER

messages = (
    MessagesPacker(max_tokens=500)
    .add("System prompt", role="system", priority=PRIORITY_SYSTEM)
    .add("User query", role="user", priority=PRIORITY_USER)
    .pack()
)
```

### Inspection

```python
packer = MessagesPacker(max_tokens=1000)
packer.add("Item 1", role="system", priority=PRIORITY_SYSTEM)
packer.add("Item 2", role="user", priority=PRIORITY_USER)

# Inspect items before packing
items = packer.get_items()
for item in items:
    print(f"Priority: {item['priority']}, Tokens: {item['tokens']}")
```

### Reset

```python
packer = MessagesPacker(max_tokens=1000)
packer.add("First batch", role="user", priority=PRIORITY_HIGH)
messages1 = packer.pack()

# Clear and reuse
packer.reset()
packer.add("Second batch", role="user", priority=PRIORITY_HIGH)
messages2 = packer.pack()
```

## Algorithm Details

1. **Add Phase**: Items are added with priorities, optional roles, and optional JIT refinement
2. **Token Counting**:
   - MessagesPacker: content tokens + 4 tokens overhead (ChatML format)
   - TextPacker RAW: content tokens + separator overhead
   - TextPacker MARKDOWN: content tokens + marginal overhead (3-4 tokens per item after fixed header reservation)
   - TextPacker XML: content tokens + tag overhead
3. **Sort Phase**: Items are sorted by priority (lower number = higher priority)
4. **Greedy Packing**: Items are selected sequentially if they fit within the token budget
5. **Order Restoration**: Selected items are restored to insertion order for natural reading flow
6. **Format Phase**:
   - MessagesPacker: Returns `List[Dict[str, str]]`
   - TextPacker: Returns formatted `str` based on `text_format`

## Tips

!!! tip "Choose the Right Packer"
    - Use **MessagesPacker** for chat APIs (OpenAI, Anthropic)
    - Use **TextPacker** for completion APIs (Llama Base, GPT-3)

!!! tip "Choose the Right Priority"
    - `PRIORITY_SYSTEM`: System prompts, critical instructions
    - `PRIORITY_USER`: User input, current queries
    - `PRIORITY_HIGH`: Core context, most relevant documents
    - `PRIORITY_MEDIUM`: Supporting context, moderately relevant
    - `PRIORITY_LOW`: Optional content, old history

!!! tip "Clean Before Packing"
    Use `refine_with` to clean items before token counting:

    ```python
    packer.add(
        dirty_html,
        priority=PRIORITY_HIGH,
        refine_with=StripHTML()
    )
    ```

!!! tip "Monitor Token Usage"
    Check effective token budget and utilization:

    ```python
    packer = MessagesPacker(max_tokens=1000)
    print(f"Effective budget: {packer.effective_max_tokens}")  # 900 in estimation mode
    ```

!!! tip "Grouped MARKDOWN Saves Tokens"
    TextPacker with MARKDOWN format groups items by section, saving tokens:

    ```python
    # Old (per-item headers): ### CONTEXT:\nDoc 1\n\n### CONTEXT:\nDoc 2
    # New (grouped): ### CONTEXT:\n- Doc 1\n- Doc 2
    ```
