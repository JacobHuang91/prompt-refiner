# Packer Module

Intelligently manage context budgets with priority-based item packing for RAG applications and context window management.

## Overview (v0.1.3+)

The Packer module provides two specialized packers following the Single Responsibility Principle:

- **`MessagesPacker`**: For chat completion APIs (OpenAI, Anthropic)
- **`TextPacker`**: For text completion APIs (Llama Base, GPT-3)

## MessagesPacker

Pack items into chat message format for chat completion APIs.

### Basic Usage

```python
from prompt_refiner import MessagesPacker, PRIORITY_SYSTEM, PRIORITY_USER, PRIORITY_HIGH

# Create packer with token budget
packer = MessagesPacker(max_tokens=1000)

# Add items with priorities and roles
packer.add(
    "You are a helpful assistant.",
    role="system",
    priority=PRIORITY_SYSTEM
)

packer.add(
    "What are the key features?",
    role="user",
    priority=PRIORITY_USER
)

packer.add(
    "Product documentation: Feature A, B, C...",
    role="system",
    priority=PRIORITY_HIGH
)

# Pack into messages format
messages = packer.pack()  # Returns List[Dict[str, str]]

# Use directly with chat APIs
# response = client.chat.completions.create(messages=messages)
```

### RAG + Conversation History Example

```python
from prompt_refiner import (
    MessagesPacker,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    StripHTML
)

packer = MessagesPacker(max_tokens=500)

# System prompt (must include)
packer.add(
    "Answer based on the provided context.",
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

# Pack into messages
messages = packer.pack()  # List[Dict[str, str]]
```

## TextPacker

Pack items into formatted text for text completion APIs (base models).

### Basic Usage

```python
from prompt_refiner import TextPacker, TextFormat, PRIORITY_SYSTEM, PRIORITY_HIGH, PRIORITY_USER

# Create packer with MARKDOWN format
packer = TextPacker(
    max_tokens=1000,
    text_format=TextFormat.MARKDOWN
)

# Add items
packer.add(
    "You are a helpful assistant.",
    role="system",
    priority=PRIORITY_SYSTEM
)

packer.add(
    "Product documentation...",
    priority=PRIORITY_HIGH
)

packer.add(
    "What are the key features?",
    role="user",
    priority=PRIORITY_USER
)

# Pack into formatted text
prompt = packer.pack()  # Returns str

# Use with completion APIs
# response = client.completions.create(prompt=prompt)
```

### Text Formats

**RAW Format** (default):
```python
packer = TextPacker(max_tokens=1000, text_format=TextFormat.RAW)
# Output: Simple concatenation with separators
```

**MARKDOWN Format** (recommended for base models):
```python
packer = TextPacker(max_tokens=1000, text_format=TextFormat.MARKDOWN)
# Output:
# ### INSTRUCTIONS:
# System prompt
#
# ### CONTEXT:
# - Document 1
# - Document 2
#
# ### CONVERSATION:
# User: Hello
# Assistant: Hi
#
# ### INPUT:
# Final query
```

**XML Format** (Anthropic best practice):
```python
packer = TextPacker(max_tokens=1000, text_format=TextFormat.XML)
# Output: <role>content</role> tags
```

### RAG Example with Grouped Sections

```python
from prompt_refiner import (
    TextPacker,
    TextFormat,
    PRIORITY_SYSTEM,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_USER,
    StripHTML
)

packer = TextPacker(max_tokens=500, text_format=TextFormat.MARKDOWN)

# System prompt
packer.add(
    "Answer based on context.",
    role="system",
    priority=PRIORITY_SYSTEM
)

# RAG documents (no role = context)
packer.add(
    "<p>Document 1...</p>",
    priority=PRIORITY_HIGH,
    refine_with=StripHTML()
)

packer.add(
    "Document 2...",
    priority=PRIORITY_MEDIUM
)

# User query
packer.add(
    "What is the answer?",
    role="user",
    priority=PRIORITY_USER
)

prompt = packer.pack()  # str
```

## Priority Constants

```python
from prompt_refiner import (
    PRIORITY_SYSTEM,   # 0 - Absolute must-have (system prompts)
    PRIORITY_USER,     # 10 - Critical user input
    PRIORITY_HIGH,     # 20 - Important context (core RAG docs)
    PRIORITY_MEDIUM,   # 30 - Normal priority (general RAG docs)
    PRIORITY_LOW,      # 40 - Optional content (old history)
)
```

## Common Features

### JIT Refinement

Apply operations before adding items:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace

packer.add(
    "<div>  Messy   HTML  </div>",
    priority=PRIORITY_HIGH,
    refine_with=[StripHTML(), NormalizeWhitespace()]
)
```

### Method Chaining

```python
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

## How It Works

1. **Add items** with priorities, roles, and optional JIT refinement
2. **Sort by priority** (lower number = higher priority)
3. **Greedy packing** - select items that fit within budget
4. **Restore insertion order** for natural reading flow
5. **Format output**:
   - MessagesPacker: Returns `List[Dict[str, str]]`
   - TextPacker: Returns `str` (formatted based on text_format)

## Token Overhead Optimization

### MessagesPacker
- Pre-calculates ChatML format overhead (~4 tokens per message)
- 100% token budget utilization in precise mode

### TextPacker (MARKDOWN)
- **"Entrance fee" strategy**: Pre-reserves 30 tokens for section headers
- **Marginal costs**: Only counts bullet points and newlines per item
- **Result**: Fits more documents compared to per-item header calculation

## Use Cases

- **RAG Applications**: Pack retrieved documents into context budget
- **Chatbots**: Manage conversation history with priorities
- **Context Window Management**: Fit critical information within model limits
- **Multi-source Data**: Combine system prompts, user input, and documents

## New in v0.1.3

The Packer module now provides two specialized packers:

```python
from prompt_refiner import MessagesPacker, TextPacker

# For chat APIs (OpenAI, Anthropic)
messages_packer = MessagesPacker(max_tokens=1000)
messages = messages_packer.pack()  # List[Dict[str, str]]

# For completion APIs (Llama Base, GPT-3)
text_packer = TextPacker(max_tokens=1000, text_format=TextFormat.MARKDOWN)
text = text_packer.pack()  # str
```

[Full API Reference →](../api-reference/packer.md){ .md-button }
[View Examples](https://github.com/JacobHuang91/prompt-refiner/tree/main/examples/packer){ .md-button }
