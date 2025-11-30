# Packer Module

The Packer module provides high-level operations for managing context budgets with priority-based item selection. **Version 0.1.3+** adds unified support for both plain text (completion APIs) and structured messages (chat APIs).

## ContextPacker

Intelligently pack text items and messages into a token budget using a greedy algorithm that respects priorities and maintains insertion order.

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

### Overhead Constants

```python
from prompt_refiner import (
    PER_MESSAGE_OVERHEAD,  # 4 tokens - ChatML format overhead per message
    PER_REQUEST_OVERHEAD,  # 3 tokens - Base request overhead
)
```

These constants reflect the approximate token overhead for OpenAI's ChatML format (`<|im_start|>role\n...\n<|im_end|>`).

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

## API Enhancements in v0.1.3

!!! info "API Changes"
    Version 0.1.3 enhances the ContextPacker API:

    **Method Changes:**
    - `add_item()` → `add()` (renamed, added `role` parameter)
    - `pack()` now returns `PackedResult` (strongly-typed object) instead of `str`

    **Updated Usage:**
    ```python
    # v0.1.3+ API
    packer.add("content", priority=PRIORITY_HIGH)
    result = packer.pack()  # Returns PackedResult object

    print(result.text)      # Dot notation access (NEW!)
    print(result.messages)  # Perfect IDE autocomplete (NEW!)
    print(result.meta)      # Type-safe access (NEW!)
    ```

    **Benefits:**
    - ✓ Better IDE support with autocomplete
    - ✓ Type safety - no typos in key names
    - ✓ Pythonic dot notation (`result.messages` vs `result["messages"]`)

## Text Formatting Strategies

!!! info "New in v0.1.3: Prevent Instruction Drifting"
    When using completion APIs (base models), simply joining content with newlines can cause **instruction drifting** - the model confuses where instructions end and context begins.

    ContextPacker now supports **text formatting strategies** to add clear semantic delimiters:

    - **`TextFormat.RAW`** (default): No delimiters, backward compatible
    - **`TextFormat.MARKDOWN`**: Use `### ROLE:` headers for section boundaries
    - **`TextFormat.XML`**: Use `<role>content</role>` tags (Anthropic best practice)

### Formatting Parameters

The `pack()` method accepts two parameters for customizing text output:

```python
from prompt_refiner import TextFormat

def pack(
    self,
    text_format: TextFormat = TextFormat.RAW,
    separator: Optional[str] = None,
) -> PackedResult:
```

**Parameters:**

- `text_format`: TextFormat enum specifying formatting strategy
  - `TextFormat.RAW`: Join content with separator (no delimiters)
  - `TextFormat.MARKDOWN`: Add `### ROLE:` headers before each item
  - `TextFormat.XML`: Wrap content in `<role>content</role>` tags
- `separator`: String to join packed items
  - `None` (default): Smart default uses `"\n\n"` for all formats (clarity > length)
  - `""`: Expert override for maximum compression
  - Any custom string: Full control over item separation

**Delimiter Overhead:**

Delimiters consume tokens! ContextPacker automatically accounts for delimiter overhead in the budget:

```python
from prompt_refiner import ContextPacker, PRIORITY_USER, TextFormat

packer = ContextPacker(max_tokens=100)
packer.add("Hello", role="user", priority=PRIORITY_USER)

# Raw: no delimiter overhead
result_raw = packer.pack(text_format=TextFormat.RAW)
# token_usage: ~10 tokens

# Markdown: adds "### USER:\n" = ~3 tokens overhead
result_md = packer.pack(text_format=TextFormat.MARKDOWN)
# token_usage: ~13 tokens

# XML: adds "<user>\n" + "\n</user>" = ~4 tokens overhead
result_xml = packer.pack(text_format=TextFormat.XML)
# token_usage: ~14 tokens
```

**Separator Best Practices:**

```python
# Smart default (recommended): uses "\n\n" for clarity
result = packer.pack()  # Principle: Clarity > Length

# Expert override: maximum compression
result = packer.pack(separator="")  # No whitespace between items

# Custom separator
result = packer.pack(separator=" | ")  # Custom delimiter
```

### Strategy Comparison

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_HIGH, PRIORITY_USER, TextFormat

packer = ContextPacker(max_tokens=200)
packer.add("You are helpful.", role="system", priority=PRIORITY_SYSTEM)
packer.add("London is the capital.", priority=PRIORITY_HIGH)  # RAG doc
packer.add("What is the capital?", role="user", priority=PRIORITY_USER)

# Format 1: Raw (default)
result = packer.pack(text_format=TextFormat.RAW)
print(result.text)
# Output:
# You are helpful.
#
# London is the capital.
#
# What is the capital?

# Format 2: Markdown
result = packer.pack(text_format=TextFormat.MARKDOWN)
print(result.text)
# Output:
# ### SYSTEM:
# You are helpful.
#
# ### CONTEXT:
# London is the capital.
#
# ### USER:
# What is the capital?

# Format 3: XML
result = packer.pack(text_format=TextFormat.XML)
print(result.text)
# Output:
# <system>
# You are helpful.
# </system>
#
# <context>
# London is the capital.
# </context>
#
# <user>
# What is the capital?
# </user>

```

### When to Use Each Format

!!! tip "Choose the Right Format"

    **Use `TextFormat.RAW` (default) when:**

    - Using chat APIs (use `result.messages` instead)
    - Very simple prompts where structure doesn't matter
    - Backward compatibility is required

    **Use `TextFormat.MARKDOWN` when:**

    - Targeting base completion models (GPT-3, Llama-2-base)
    - You need clear section boundaries
    - Widely supported, familiar format

    **Use `TextFormat.XML` when:**

    - Using Anthropic Claude (in completion format)
    - Complex RAG scenarios with nested context
    - You want maximum semantic clarity

!!! warning "Message Format Unaffected"
    Text formatting **only affects** `result.text`.

    The `result.messages` format is **always** the same (standard ChatML):

    ```python
    result = packer.pack(text_format=TextFormat.XML)

    # Text output has XML tags
    print(result.text)  # <system>...</system>

    # Messages output is standard
    print(result.messages)
    # [{"role": "system", "content": "..."}]
    ```

## Examples

### Basic Usage (Text Format)

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER

packer = ContextPacker(max_tokens=500)

packer.add(
    "You are a helpful assistant.",
    priority=PRIORITY_SYSTEM
)

packer.add(
    "What is prompt-refiner?",
    priority=PRIORITY_USER
)

result = packer.pack()
print(result.text)  # Plain text output
```

### Message Format (Chat APIs)

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER

packer = ContextPacker(max_tokens=500)

# Add messages with roles
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

result = packer.pack()

# Use message format for chat APIs
for msg in result.messages:
    print(f"{msg['role']}: {msg['content']}")

# Or send directly to OpenAI/Anthropic
# response = openai.chat.completions.create(
#     model="gpt-4",
#     messages=result.messages
# )
```

### RAG Application

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
packer.add(
    "You are a QA assistant. Answer based on the provided context.",
    role="system",
    priority=PRIORITY_SYSTEM
)

# User query (must include)
packer.add(
    "What are the main features of prompt-refiner?",
    role="user",
    priority=PRIORITY_USER
)

# Retrieved documents with different relevance scores
packer.add(
    "Prompt-refiner is a library for optimizing LLM prompts...",
    role="system",
    priority=PRIORITY_HIGH  # Most relevant document
)

packer.add(
    "The library includes 5 modules: Cleaner, Compressor...",
    role="system",
    priority=PRIORITY_MEDIUM  # Moderately relevant
)

packer.add(
    "Installation instructions and setup details...",
    role="system",
    priority=PRIORITY_LOW  # Less critical, may be dropped
)

# Pack into final context
result = packer.pack()

# Send to chat API
# response = client.chat(messages=result.messages)
```

### Mixed Text and Messages

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_HIGH, PRIORITY_USER

packer = ContextPacker(max_tokens=500)

# System message
packer.add(
    "You are a QA assistant.",
    role="system",
    priority=PRIORITY_SYSTEM
)

# RAG documents as raw text (no role)
packer.add(
    "Context: Prompt-refiner is a Python library...",
    priority=PRIORITY_HIGH
)

# User query as message
packer.add(
    "What is prompt-refiner?",
    role="user",
    priority=PRIORITY_USER
)

result = packer.pack()

# Text format includes all content
print(result.text)

# Messages format only includes items with roles
print(result.messages)  # Only system and user messages
```

### JIT Refinement

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
packer.add(
    dirty_html,
    priority=PRIORITY_HIGH,
    refine_with=StripHTML()
)

# Chain multiple operations
messy_text = "<p>  Multiple   spaces   here  </p>"
packer.add(
    messy_text,
    priority=PRIORITY_HIGH,
    refine_with=[StripHTML(), NormalizeWhitespace()]
)

result = packer.pack()
```

### Batch Add Messages

Convenience method for adding conversation history:

```python
from prompt_refiner import ContextPacker, PRIORITY_HIGH

packer = ContextPacker(max_tokens=500)

conversation = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
]

packer.add_messages(conversation, priority=PRIORITY_HIGH)

result = packer.pack()
print(result.messages)
```

### Method Chaining

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER, PRIORITY_HIGH

result = (
    ContextPacker(max_tokens=500)
    .add("System prompt", role="system", priority=PRIORITY_SYSTEM)
    .add("User query", role="user", priority=PRIORITY_USER)
    .add("Context document", priority=PRIORITY_HIGH)
    .pack()
)

print(result.messages)
```

### Inspection and Reset

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER

packer = ContextPacker(max_tokens=1000)
packer.add("First item", role="system", priority=PRIORITY_SYSTEM)
packer.add("Second item", role="user", priority=PRIORITY_USER)

# Inspect items before packing
items = packer.get_items()
for item in items:
    print(f"Priority: {item['priority']}, Tokens: {item['tokens']}, Role: {item['role']}")

# Pack first batch
result1 = packer.pack()

# Reset and reuse
packer.reset()
packer.add("New batch", role="system", priority=PRIORITY_SYSTEM)
result2 = packer.pack()
```

## How the Algorithm Works

1. **Add Phase**: Items are added with priorities, optional roles, and optional JIT refinement
2. **Token Counting**:
   - Raw text: content tokens only
   - Messages: content tokens + `PER_MESSAGE_OVERHEAD` (4 tokens)
   - Request: base overhead of `PER_REQUEST_OVERHEAD` (3 tokens)
   - Text delimiters: additional overhead based on `text_format` (calculated during packing)
3. **Sort Phase**: Items are sorted by priority (lower number = higher priority)
4. **Greedy Packing**: Items are selected sequentially if they fit within the token budget (including delimiter overhead)
5. **Order Restoration**: Selected items are restored to insertion order for natural reading flow
6. **Format Phase**: Items are formatted as both text string (with delimiters and smart separator) and message list (standard ChatML)

## Output Format

The `pack()` method returns a `PackedResult` object with three attributes:

```python
@dataclass
class PackedResult:
    messages: List[Dict[str, str]]  # Chat API format (only items with roles)
    text: str                       # Completion API format (all items formatted)
    meta: Dict[str, int]            # Metadata: {"token_usage": int, "item_count": int}
```

**Usage:**

```python
result = packer.pack()

# Access with dot notation (Pythonic!)
print(result.text)                # str
print(result.messages)            # List[Dict[str, str]]
print(result.meta["token_usage"]) # int
```

## Common Use Cases

### Chatbot with Conversation History

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER, PRIORITY_LOW

packer = ContextPacker(max_tokens=2000)

# System prompt
packer.add(
    "You are a helpful chatbot...",
    role="system",
    priority=PRIORITY_SYSTEM
)

# Recent conversation (high priority)
packer.add(
    "What's the weather?",
    role="user",
    priority=PRIORITY_USER
)

# Older history (low priority, may be dropped)
for old_message in old_messages:
    packer.add(
        old_message["content"],
        role=old_message["role"],
        priority=PRIORITY_LOW
    )

# Current user input (highest priority)
packer.add(current_input, role="user", priority=PRIORITY_USER)

result = packer.pack()
# Send result.messages to chat API
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
packer.add(system_prompt, role="system", priority=PRIORITY_SYSTEM)

# User query
packer.add(user_query, role="user", priority=PRIORITY_USER)

# Vector database results (cleaned)
for doc in vector_results:
    packer.add(
        doc.content,
        role="system",
        priority=PRIORITY_HIGH,
        refine_with=StripHTML()
    )

# Keyword search results (lower priority)
for doc in keyword_results:
    packer.add(doc.content, role="system", priority=PRIORITY_MEDIUM)

# Send to API
result = packer.pack()
# response = client.chat(messages=result.messages)
```

### Dynamic Context Budgeting

```python
from prompt_refiner import ContextPacker, PRIORITY_SYSTEM, PRIORITY_USER, PRIORITY_HIGH, PRIORITY_MEDIUM

def create_prompt(system, user, documents, max_tokens):
    """Create prompt with dynamic budget allocation."""
    packer = ContextPacker(max_tokens=max_tokens)

    packer.add(system, role="system", priority=PRIORITY_SYSTEM)
    packer.add(user, role="user", priority=PRIORITY_USER)

    # Add documents by relevance score
    for doc in documents:
        priority = PRIORITY_HIGH if doc.score > 0.8 else PRIORITY_MEDIUM
        packer.add(doc.content, role="system", priority=priority)

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

!!! tip "Use Roles for Chat APIs"
    When targeting chat completion APIs, always specify roles:

    ```python
    packer.add("content", role="system", priority=PRIORITY_SYSTEM)
    # Then use result.messages for the API call
    ```

!!! tip "Clean Before Packing"
    Use `refine_with` to clean items before token counting for accuracy:

    ```python
    packer.add(
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
    items_after = result.meta["item_count"]
    dropped = items_before - items_after
    logger.info(f"Dropped {dropped} items due to budget constraints")
    ```

!!! tip "Understand Message Overhead"
    Messages have ~4 tokens overhead for ChatML format. Use raw text (no role) for dense packing:

    ```python
    # With role: content tokens + 4 overhead
    packer.add("Hello", role="user")  # ~6 tokens

    # Without role: just content tokens
    packer.add("Hello")  # ~2 tokens
    ```

!!! tip "Use Metadata"
    The `meta` attribute provides valuable debugging information:

    ```python
    result = packer.pack()
    print(f"Used {result.meta['token_usage']} tokens")
    print(f"Selected {result.meta['item_count']} items")
    ```
