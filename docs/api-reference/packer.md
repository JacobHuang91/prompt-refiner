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

### Semantic Role Constants (Recommended)

```python
from prompt_refiner import (
    ROLE_SYSTEM,      # "system" - System instructions (auto: PRIORITY_SYSTEM = 0)
    ROLE_QUERY,       # "query" - Current user question (auto: PRIORITY_QUERY = 10)
    ROLE_CONTEXT,     # "context" - RAG documents (auto: PRIORITY_HIGH = 20)
    ROLE_USER,        # "user" - User messages in history (auto: PRIORITY_LOW = 40)
    ROLE_ASSISTANT,   # "assistant" - Assistant messages in history (auto: PRIORITY_LOW = 40)
)
```

### Priority Constants (Optional)

```python
from prompt_refiner import (
    PRIORITY_SYSTEM,   # 0 - Absolute must-have (system prompts)
    PRIORITY_QUERY,    # 10 - Current user query (critical for response)
    PRIORITY_HIGH,     # 20 - Important context (core RAG documents)
    PRIORITY_MEDIUM,   # 30 - Normal priority (general RAG documents)
    PRIORITY_LOW,      # 40 - Optional content (old conversation history)
)
```

!!! tip "Smart Priority Defaults"
    **You usually don't need to specify priority!** Just use semantic roles and priority is auto-inferred:

    ```python
    # Recommended: Use semantic roles (priority auto-inferred)
    packer.add("System prompt", role=ROLE_SYSTEM)  # Auto: PRIORITY_SYSTEM (0)
    packer.add("User query", role=ROLE_QUERY)      # Auto: PRIORITY_QUERY (10)
    packer.add("RAG doc", role=ROLE_CONTEXT)       # Auto: PRIORITY_HIGH (20)

    # Advanced: Override priority if needed
    packer.add("Urgent RAG doc", role=ROLE_CONTEXT, priority=PRIORITY_QUERY)
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

## Token Savings Tracking

**Version 0.1.5+** introduces automatic token savings tracking to measure the optimization impact of `refine_with` operations.

### Enable Tracking

```python
# Opt-in to tracking with track_savings parameter
packer = MessagesPacker(track_savings=True)

# Add items with refinement
packer.add(
    "<div>  Messy   HTML  </div>",
    role=ROLE_CONTEXT,
    refine_with=[StripHTML(), NormalizeWhitespace()]
)

# Get savings statistics
savings = packer.get_token_savings()
# Returns: {
#   'original_tokens': 25,      # Tokens before refinement
#   'refined_tokens': 12,       # Tokens after refinement
#   'saved_tokens': 13,         # Tokens saved
#   'saving_percent': 52.0,     # Percentage saved
#   'items_refined': 1          # Count of refined items
# }
```

### Key Features

- **Opt-in**: Disabled by default (no overhead when not needed)
- **Automatic aggregation**: Tracks all items that use `refine_with`
- **Per-item and total**: Aggregates savings across all refined items
- **Works with both packers**: Available for `MessagesPacker` and `TextPacker`

### Example with Real API

```python
from prompt_refiner import MessagesPacker, StripHTML
from openai import OpenAI

client = OpenAI()
packer = MessagesPacker(model="gpt-4o", track_savings=True)

# Add multiple RAG documents with automatic cleaning
for doc in scraped_html_docs:
    packer.add(doc, role="context", refine_with=StripHTML())

# Pack messages and check savings
messages = packer.pack()
savings = packer.get_token_savings()

print(f"Saved {savings['saved_tokens']} tokens ({savings['saving_percent']:.1f}%)")
# Example output: "Saved 1,234 tokens (23.5%)"

# Use cleaned messages with API
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)
```

### When to Use

✅ **Use token savings tracking when:**
- You want to measure ROI of optimization efforts
- Demonstrating token savings to stakeholders
- A/B testing different refinement strategies
- Monitoring optimization impact in production

❌ **Skip tracking when:**
- Not using `refine_with` parameter (returns empty dict)
- Performance is absolutely critical (negligible overhead, but why enable?)
- You don't need savings metrics

!!! tip "Combine with CountTokens"
    For pipeline optimization (not packer), use `CountTokens` instead:
    ```python
    from prompt_refiner import CountTokens, StripHTML, NormalizeWhitespace

    counter = CountTokens(original_text=dirty_html)
    pipeline = StripHTML() | NormalizeWhitespace()
    clean = pipeline.run(dirty_html)
    counter.process(clean)
    print(counter.format_stats())
    ```

## MessagesPacker Examples

### Basic Usage

```python
from prompt_refiner import MessagesPacker

packer = MessagesPacker(max_tokens=500)

packer.add(
    "You are a helpful assistant.",
    role="system"  # Auto: PRIORITY_SYSTEM (0)
)

packer.add(
    "What is prompt-refiner?",
    role="query"  # Auto: PRIORITY_QUERY (10)
)

messages = packer.pack()  # List[Dict[str, str]]
# Use directly: openai.chat.completions.create(messages=messages)
```

### RAG with Conversation History

```python
from prompt_refiner import MessagesPacker, StripHTML

packer = MessagesPacker(max_tokens=1000)

# System prompt (must include)
packer.add(
    "Answer based on provided context.",
    role="system"  # Auto: PRIORITY_SYSTEM (0)
)

# RAG documents with JIT cleaning
packer.add(
    "<p>Prompt-refiner is a library...</p>",
    role="context",  # Auto: PRIORITY_HIGH (20)
    refine_with=StripHTML()
)

# Old conversation history (can be dropped if needed)
old_messages = [
    {"role": "user", "content": "What is this library?"},
    {"role": "assistant", "content": "It's a tool for optimizing prompts."}
]
packer.add_messages(old_messages)  # Auto: PRIORITY_LOW (40) for history

# Current query (must include)
packer.add(
    "How does it reduce costs?",
    role="query"  # Auto: PRIORITY_QUERY (10)
)

messages = packer.pack()
```

## TextPacker Examples

### Basic Usage

```python
from prompt_refiner import TextPacker, TextFormat

packer = TextPacker(
    max_tokens=500,
    text_format=TextFormat.MARKDOWN
)

packer.add(
    "You are a QA assistant.",
    role="system"  # Auto: PRIORITY_SYSTEM (0)
)

packer.add(
    "Context: Prompt-refiner is a library...",
    role="context"  # Auto: PRIORITY_HIGH (20)
)

packer.add(
    "What is prompt-refiner?",
    role="query"  # Auto: PRIORITY_QUERY (10)
)

prompt = packer.pack()  # str
# Use with: completion.create(prompt=prompt)
```

### Text Format Comparison

```python
from prompt_refiner import TextPacker, TextFormat

# RAW format (simple concatenation)
packer = TextPacker(max_tokens=200, text_format=TextFormat.RAW)
packer.add("System prompt", role="system")
packer.add("User query", role="query")
prompt = packer.pack()
# Output:
# System prompt
#
# User query

# MARKDOWN format (grouped sections in v0.1.3+)
packer = TextPacker(max_tokens=200, text_format=TextFormat.MARKDOWN)
packer.add("System prompt", role="system")
packer.add("Doc 1", role="context")
packer.add("Doc 2", role="context")
packer.add("User query", role="query")
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
packer.add("System prompt", role="system")
packer.add("User query", role="query")
prompt = packer.pack()
# Output:
# <system>
# System prompt
# </system>
#
# <query>
# User query
# </query>
```

## Common Features

### JIT Refinement

Both packers support Just-In-Time refinement:

```python
from prompt_refiner import StripHTML, NormalizeWhitespace

# Single operation
packer.add(
    "<div>HTML content</div>",
    role="context",
    refine_with=StripHTML()
)

# Multiple operations
packer.add(
    "<p>  Messy   HTML  </p>",
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

# Inspect items before packing
items = packer.get_items()
for item in items:
    print(f"Priority: {item['priority']}, Tokens: {item['tokens']}, Role: {item['role']}")
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

!!! tip "Use Semantic Roles (Recommended)"
    Semantic roles auto-infer priorities, making code clearer:

    - `ROLE_SYSTEM`: System instructions → PRIORITY_SYSTEM (0)
    - `ROLE_QUERY`: Current user question → PRIORITY_QUERY (10)
    - `ROLE_CONTEXT`: RAG documents → PRIORITY_HIGH (20)
    - `ROLE_USER` / `ROLE_ASSISTANT`: Conversation history → PRIORITY_LOW (40)

    ```python
    # Recommended: Clear intent with semantic roles
    packer.add("System prompt", role=ROLE_SYSTEM)
    packer.add("Current query", role=ROLE_QUERY)
    packer.add("RAG doc", role=ROLE_CONTEXT)
    ```

!!! tip "Override Priority When Needed"
    Most of the time semantic roles are enough, but you can override:

    ```python
    # Make a RAG document urgent (higher priority than normal)
    packer.add("Critical doc", role=ROLE_CONTEXT, priority=PRIORITY_QUERY)
    ```

!!! tip "Clean Before Packing"
    Use `refine_with` to clean items before token counting:

    ```python
    packer.add(
        dirty_html,
        role=ROLE_CONTEXT,
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
