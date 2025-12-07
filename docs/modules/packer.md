# Packer Module

Intelligently manage context budgets with smart priority-based packing for RAG applications and chatbots.

## Overview (v0.1.3+)

The Packer module provides two specialized packers following the Single Responsibility Principle:

- **`MessagesPacker`**: For chat completion APIs (OpenAI, Anthropic). Returns `List[Dict]`
- **`TextPacker`**: For text completion APIs (Llama Base, GPT-3). Returns `str`

**Key Features:**
- Smart priority-based selection (auto-prioritizes: system > query > context > history)
- Semantic roles for clear intent (ROLE_SYSTEM, ROLE_QUERY, ROLE_CONTEXT, ROLE_USER, ROLE_ASSISTANT)
- JIT refinement with `refine_with` parameter
- Automatic format overhead calculation

## MessagesPacker

Pack items into chat message format for chat completion APIs.

### Basic Usage

```python
from prompt_refiner import MessagesPacker

# Create packer with token budget
packer = MessagesPacker(max_tokens=1000)

# Add items with semantic roles (auto-prioritized)
packer.add(
    "You are a helpful assistant.",
    role="system"  # Auto: highest priority
)

packer.add(
    "Product documentation: Feature A, B, C...",
    role="context"  # Auto: high priority
)

packer.add(
    "What are the key features?",
    role="query"  # Auto: critical priority
)

# Pack into messages format
messages = packer.pack()  # Returns List[Dict[str, str]]

# Use directly with chat APIs
# response = client.chat.completions.create(messages=messages)
```

### RAG + Conversation History Example

```python
from prompt_refiner import MessagesPacker, StripHTML

packer = MessagesPacker(max_tokens=500)

# System prompt (auto: highest priority)
packer.add(
    "Answer based on the provided context.",
    role="system"
)

# RAG documents with JIT cleaning (auto: high priority)
packer.add(
    "<p>Prompt-refiner is a library...</p>",
    role="context",
    refine_with=StripHTML()
)

# Old conversation history (auto: low priority, can be dropped)
old_messages = [
    {"role": "user", "content": "What is this library?"},
    {"role": "assistant", "content": "It's a tool for optimizing prompts."}
]
packer.add_messages(old_messages)

# Current query (auto: critical priority)
packer.add(
    "How does it reduce costs?",
    role="query"
)

# Pack into messages
messages = packer.pack()  # List[Dict[str, str]]
```

## TextPacker

Pack items into formatted text for text completion APIs (base models).

### Basic Usage

```python
from prompt_refiner import TextPacker, TextFormat

# Create packer with MARKDOWN format
packer = TextPacker(
    max_tokens=1000,
    text_format=TextFormat.MARKDOWN
)

# Add items with semantic roles (auto-prioritized)
packer.add(
    "You are a helpful assistant.",
    role="system"  # Auto: highest priority
)

packer.add(
    "Product documentation...",
    role="context"  # Auto: high priority
)

packer.add(
    "What are the key features?",
    role="query"  # Auto: critical priority
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
from prompt_refiner import TextPacker, TextFormat, StripHTML

packer = TextPacker(max_tokens=500, text_format=TextFormat.MARKDOWN)

# System prompt (auto: highest priority)
packer.add(
    "Answer based on context.",
    role="system"
)

# RAG documents (auto: high priority)
packer.add(
    "<p>Document 1...</p>",
    role="context",
    refine_with=StripHTML()
)

packer.add(
    "Document 2...",
    role="context"
)

# User query (auto: critical priority)
packer.add(
    "What is the answer?",
    role="query"
)

prompt = packer.pack()  # str
```

## Semantic Roles & Priorities

**Semantic Roles (Recommended):**
```python
from prompt_refiner import (
    ROLE_SYSTEM,      # "system" - System instructions (auto: PRIORITY_SYSTEM = 0)
    ROLE_QUERY,       # "query" - Current user question (auto: PRIORITY_QUERY = 10)
    ROLE_CONTEXT,     # "context" - RAG documents (auto: PRIORITY_HIGH = 20)
    ROLE_USER,        # "user" - User messages in history (auto: PRIORITY_LOW = 40)
    ROLE_ASSISTANT,   # "assistant" - Assistant messages in history (auto: PRIORITY_LOW = 40)
)
```

**Priority Constants (Optional):**
```python
from prompt_refiner import (
    PRIORITY_SYSTEM,   # 0 - Absolute must-have (system prompts)
    PRIORITY_QUERY,    # 10 - Current user query (critical for response)
    PRIORITY_HIGH,     # 20 - Important context (core RAG docs)
    PRIORITY_MEDIUM,   # 30 - Normal priority (general RAG docs)
    PRIORITY_LOW,      # 40 - Optional content (old history)
)
```

!!! tip "Use Semantic Roles"
    Semantic roles auto-infer priorities, making code clearer. You usually don't need to specify priority manually!

## Common Features

### JIT Refinement

Apply operations before adding items:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace

packer.add(
    "<div>  Messy   HTML  </div>",
    role="context",
    refine_with=[StripHTML(), NormalizeWhitespace()]
)
```

### Method Chaining

```python
from prompt_refiner import MessagesPacker

messages = (
    MessagesPacker(max_tokens=500)
    .add("System prompt", role="system")
    .add("User query", role="query")
    .pack()
)
```

### Inspection

```python
from prompt_refiner import MessagesPacker

packer = MessagesPacker(max_tokens=1000)
packer.add("Item 1", role="system")
packer.add("Item 2", role="query")

items = packer.get_items()
for item in items:
    print(f"Priority: {item['priority']}, Tokens: {item['tokens']}")
```

### Reset

```python
from prompt_refiner import MessagesPacker

packer = MessagesPacker(max_tokens=1000)
packer.add("First batch", role="context")
messages1 = packer.pack()

# Clear and reuse
packer.reset()
packer.add("Second batch", role="context")
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
