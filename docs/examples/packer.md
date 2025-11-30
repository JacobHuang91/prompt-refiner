# Packer Examples

Advanced examples for managing context budgets with MessagesPacker and TextPacker.

!!! tip "When to Use Packer"
    Packer is ideal for:

    - **RAG Applications**: Pack multiple retrieved documents within token budget
    - **Chatbots**: Manage conversation history with priorities
    - **Context Window Management**: Fit critical information within model limits
    - **Multi-source Data**: Combine system prompts, user input, and documents

## Example 1: Basic RAG with MessagesPacker

Pack RAG documents for chat APIs with priority-based selection:

```python
from prompt_refiner import (
    MessagesPacker,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
)

# Create packer with token budget
packer = MessagesPacker(max_tokens=500)

# System prompt (must include)
packer.add(
    "Answer based on the provided context only.",
    role="system",
    priority=PRIORITY_SYSTEM
)

# RAG documents with different priorities
packer.add(
    "Product X costs $99 and includes 1-year warranty.",
    role="system",
    priority=PRIORITY_HIGH  # Most relevant document
)

packer.add(
    "We offer free shipping on orders over $50.",
    role="system",
    priority=PRIORITY_MEDIUM  # Less relevant document
)

packer.add(
    "Customer reviews rate Product X 4.5/5 stars.",
    role="system",
    priority=PRIORITY_MEDIUM
)

# User query (must include)
packer.add(
    "What is the price of Product X?",
    role="user",
    priority=PRIORITY_USER
)

# Pack into messages format
messages = packer.pack()

# Use directly with OpenAI
# response = client.chat.completions.create(
#     model="gpt-4",
#     messages=messages
# )

print(f"Packed {len(messages)} messages")
for msg in messages:
    print(f"{msg['role']}: {msg['content'][:50]}...")
```

## Example 2: RAG with Dirty HTML (JIT Refinement)

Clean web-scraped RAG documents on-the-fly:

```python
from prompt_refiner import (
    MessagesPacker,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    PRIORITY_HIGH,
    StripHTML,
    NormalizeWhitespace
)

packer = MessagesPacker(max_tokens=800)

# System prompt
packer.add(
    "You are a helpful product assistant.",
    role="system",
    priority=PRIORITY_SYSTEM
)

# RAG documents from web scraping (with HTML)
docs = [
    "<div class='product'><h2>Product Features</h2><p>  Waterproof   design  </p></div>",
    "<html><body>   <p>Available in  <b>5 colors</b>:  red, blue...</p>  </body></html>",
    "<article>   Battery life:  <strong>  48 hours  </strong>  continuous use  </article>"
]

# Clean each document before adding (JIT refinement)
for doc in docs:
    packer.add(
        doc,
        role="system",
        priority=PRIORITY_HIGH,
        refine_with=[StripHTML(), NormalizeWhitespace()]  # Clean on-the-fly!
    )

# User query
packer.add(
    "What are the key features?",
    role="user",
    priority=PRIORITY_USER
)

messages = packer.pack()

# All HTML is automatically cleaned before packing
print("Cleaned messages:")
for msg in messages:
    if msg['role'] == 'system' and 'Waterproof' in msg['content']:
        print(f"Before: {docs[0][:50]}...")
        print(f"After:  {msg['content'][:50]}...")
```

## Example 3: Chatbot with Conversation History

Manage conversation history with priorities - old messages can be dropped:

```python
from prompt_refiner import (
    MessagesPacker,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    PRIORITY_HIGH,
    PRIORITY_LOW,
)

packer = MessagesPacker(max_tokens=1000)

# System prompt (highest priority)
packer.add(
    "You are a helpful customer support agent.",
    role="system",
    priority=PRIORITY_SYSTEM
)

# RAG: Current relevant documentation
packer.add(
    "Return policy: 30-day money-back guarantee for all products.",
    role="system",
    priority=PRIORITY_HIGH
)

# Old conversation history (can be dropped if budget is tight)
old_conversation = [
    {"role": "user", "content": "What are your business hours?"},
    {"role": "assistant", "content": "We're open 9 AM - 5 PM EST, Monday-Friday."},
    {"role": "user", "content": "Do you ship internationally?"},
    {"role": "assistant", "content": "Yes, we ship to over 50 countries worldwide."}
]

packer.add_messages(old_conversation, priority=PRIORITY_LOW)

# Current user query (highest priority)
packer.add(
    "What is your return policy?",
    role="user",
    priority=PRIORITY_USER
)

messages = packer.pack()

# If budget is tight, old history is dropped, but system prompt + current query are kept
print(f"Packed {len(messages)} messages (old history may be dropped)")
```

## Example 4: TextPacker for Base Models

Use TextPacker with Llama or GPT-3 base models:

```python
from prompt_refiner import (
    TextPacker,
    TextFormat,
    PRIORITY_SYSTEM,
    PRIORITY_HIGH,
    PRIORITY_USER,
)

# Use MARKDOWN format for better structure
packer = TextPacker(
    max_tokens=600,
    text_format=TextFormat.MARKDOWN
)

# System instructions
packer.add(
    "You are a QA assistant. Answer based on the context provided.",
    role="system",
    priority=PRIORITY_SYSTEM
)

# RAG documents (no role = treated as context)
packer.add(
    "Prompt-refiner is a Python library for optimizing LLM inputs.",
    priority=PRIORITY_HIGH
)

packer.add(
    "It reduces token usage by 4-15% through cleaning and compression.",
    priority=PRIORITY_HIGH
)

packer.add(
    "The library has zero dependencies by default.",
    priority=PRIORITY_HIGH
)

# User query
packer.add(
    "What is prompt-refiner?",
    role="user",
    priority=PRIORITY_USER
)

# Pack into formatted text
prompt = packer.pack()

print(prompt)
# Output:
# ### INSTRUCTIONS:
# You are a QA assistant. Answer based on the context provided.
#
# ### CONTEXT:
# - Prompt-refiner is a Python library for optimizing LLM inputs.
# - It reduces token usage by 4-15% through cleaning and compression.
# - The library has zero dependencies by default.
#
# ### INPUT:
# What is prompt-refiner?

# Use with completion API
# response = client.completions.create(
#     model="llama-2-70b",
#     prompt=prompt
# )
```

## Example 5: TextPacker with XML Format

Use XML format (Anthropic best practice for Claude base models):

```python
from prompt_refiner import (
    TextPacker,
    TextFormat,
    PRIORITY_SYSTEM,
    PRIORITY_HIGH,
    PRIORITY_USER,
)

packer = TextPacker(
    max_tokens=500,
    text_format=TextFormat.XML
)

packer.add(
    "You are a code review assistant.",
    role="system",
    priority=PRIORITY_SYSTEM
)

packer.add(
    "Code snippet: def hello(): return 'world'",
    priority=PRIORITY_HIGH
)

packer.add(
    "Please review this code for best practices.",
    role="user",
    priority=PRIORITY_USER
)

prompt = packer.pack()

print(prompt)
# Output:
# <system>
# You are a code review assistant.
# </system>
#
# <context>
# Code snippet: def hello(): return 'world'
# </context>
#
# <user>
# Please review this code for best practices.
# </user>
```

## Example 6: Precise Mode for Maximum Token Utilization

Use precise mode with tiktoken for 100% token budget utilization:

```python
from prompt_refiner import MessagesPacker, PRIORITY_SYSTEM, PRIORITY_USER

# Install tiktoken: pip install llm-prompt-refiner[token]

# Estimation mode (default): 10% safety buffer
packer_estimate = MessagesPacker(max_tokens=1000)
print(f"Estimation mode: {packer_estimate.effective_max_tokens} effective tokens")
# Output: Estimation mode: 900 effective tokens

# Precise mode: 100% budget utilization (no safety buffer)
packer_precise = MessagesPacker(max_tokens=1000, model="gpt-4")
print(f"Precise mode: {packer_precise.effective_max_tokens} effective tokens")
# Output: Precise mode: 997 effective tokens (1000 - 3 request overhead)

# Use precise mode for production to maximize token capacity
packer_precise.add("System prompt", role="system", priority=PRIORITY_SYSTEM)
packer_precise.add("User query", role="user", priority=PRIORITY_USER)
messages = packer_precise.pack()
```

## Example 7: Inspection and Debugging

Inspect items before packing to understand token distribution:

```python
from prompt_refiner import MessagesPacker, PRIORITY_SYSTEM, PRIORITY_HIGH, PRIORITY_USER

packer = MessagesPacker(max_tokens=500)

packer.add("System prompt here", role="system", priority=PRIORITY_SYSTEM)
packer.add("Document 1" * 50, role="system", priority=PRIORITY_HIGH)
packer.add("Document 2" * 50, role="system", priority=PRIORITY_HIGH)
packer.add("User query", role="user", priority=PRIORITY_USER)

# Inspect items before packing
items = packer.get_items()

print("Items before packing:")
for i, item in enumerate(items):
    print(f"{i+1}. Priority: {item['priority']}, Tokens: {item['tokens']}, Role: {item['role']}")

# Pack and see which items fit
messages = packer.pack()
print(f"\nPacked {len(messages)}/{len(items)} items")
```

## Key Takeaways

1. **Choose the Right Packer**:
   - `MessagesPacker` for chat APIs (OpenAI, Anthropic)
   - `TextPacker` for completion APIs (Llama Base, GPT-3)

2. **Set Priorities Correctly**:
   - `PRIORITY_SYSTEM` (0): System prompts, absolute must-have
   - `PRIORITY_USER` (10): User queries, critical
   - `PRIORITY_HIGH` (20): Core RAG documents
   - `PRIORITY_MEDIUM` (30): Supporting context
   - `PRIORITY_LOW` (40): Old conversation history

3. **Use JIT Refinement**:
   - Clean dirty documents with `refine_with` parameter
   - Chain multiple operations: `refine_with=[StripHTML(), NormalizeWhitespace()]`

4. **Optimize for Production**:
   - Use precise mode with `model` parameter for 100% token utilization
   - Choose appropriate text format for base models (MARKDOWN recommended)

## Related Documentation

- [Packer Module Guide](../modules/packer.md)
- [Packer API Reference](../api-reference/packer.md)
- [Getting Started](../getting-started.md)
