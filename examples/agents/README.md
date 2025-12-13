# Agent Frameworks Comparison - Learning Guide

This directory contains examples comparing **three popular approaches** for building AI agents:

1. **OpenAI Client** - Raw client with full control
2. **OpenAI Agents** - Official framework with automation
3. **LangChain** - Popular ecosystem with rich integrations

## What These Examples Cover

✅ **RAG Context** - Passing retrieved documents to the LLM
✅ **Message History** - Managing conversation state
✅ **Tool Calling** - Executing functions during generation
✅ **Context-Aware Responses** - Combining all three

**All examples use identical shared data** (`shared_data.py`) for fair comparison of token usage and approach.

## Quick Start

```bash
# Install dependencies
pip install openai openai-agents langchain langchain-openai python-dotenv

# Set your OpenAI API key
export OPENAI_API_KEY=your-key-here

# Run examples
python examples/agents/openai_client_baseline.py  # Baseline (no optimization)
python examples/agents/openai_client.py           # OpenAI client + Prompt Refiner
python examples/agents/openai_agents.py           # OpenAI agents framework
python examples/agents/langchain_agent.py         # LangChain agent
```

## Examples Overview

### Shared Data (`shared_data.py`)

All examples use identical data for fair comparison:
- **SYSTEM_PROMPT**: "You are a helpful assistant that recommends books."
- **CONTEXT_DOCUMENTS**: 3 HTML documents with extra whitespace (demonstrates cleaning)
- **MESSAGE_HISTORY**: 4-message conversation history
- **QUERY**: "Can you recommend some Python books for beginners?"
- **search_books()**: Mock function returning book data with debug fields

### 1a. `openai_client_baseline.py` - Baseline (No Optimization)

**Approach:** Build messages manually WITHOUT prompt-refiner optimization

```python
from shared_data import CONTEXT_DOCUMENTS, MESSAGE_HISTORY, QUERY, SYSTEM_PROMPT, get_tool_schema, search_books

# Build messages manually (no MessagesPacker, no HTML stripping)
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": CONTEXT_DOCUMENTS[0]},  # HTML not stripped
    {"role": "user", "content": CONTEXT_DOCUMENTS[1]},
    {"role": "user", "content": CONTEXT_DOCUMENTS[2]},
    MESSAGE_HISTORY[0],
    MESSAGE_HISTORY[1],
    MESSAGE_HISTORY[2],
    MESSAGE_HISTORY[3],
    {"role": "user", "content": QUERY},
]

# Call with uncompressed tool schema
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=[get_tool_schema()],  # No SchemaCompressor
)

# Tool response without compression
messages.append({"role": "tool", "content": json.dumps(tool_response)})  # No ResponseCompressor
```

**Token Usage:** Baseline measurements for comparison

### 1b. `openai_client.py` - Optimized with Prompt Refiner

**Approach:** Same workflow WITH prompt-refiner optimization

```python
from shared_data import CONTEXT_DOCUMENTS, MESSAGE_HISTORY, QUERY, SYSTEM_PROMPT, get_tool_schema, search_books
from prompt_refiner import MessagesPacker, SchemaCompressor, ResponseCompressor, StripHTML

# 1. Optimize messages with tuple API
messages = MessagesPacker.quick_pack(
    model="gpt-4o-mini",
    system=SYSTEM_PROMPT,
    context=(CONTEXT_DOCUMENTS, [StripHTML()]),  # Strips HTML tags
    history=MESSAGE_HISTORY,
    query=QUERY
)

# 2. Compress tool schema
compressed_schema = SchemaCompressor().process(get_tool_schema())

# 3. Call LLM with optimized inputs
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=[compressed_schema],
)

# 4. Compress tool responses
tool_response = search_books(query)
compressed_response = ResponseCompressor().process(tool_response)
messages.append({"role": "tool", "content": json.dumps(compressed_response)})
```

**Token Savings:** Compare actual OpenAI API usage metrics against baseline
- ✅ **Messages**: Strip HTML, normalize whitespace
- ✅ **Tool schemas**: Remove verbose descriptions, keep protocol intact
- ✅ **Tool responses**: Remove debug fields, truncate long strings

**Benefits:**
- Same functionality, just optimized token usage
- Real token counts from OpenAI API for direct comparison

### 2. `openai_agents.py` - OpenAI Agents Framework + TextPacker + ResponseCompressor

**Approach:** Use TextPacker for input and ResponseCompressor for tool responses

```python
from shared_data import CONTEXT_DOCUMENTS, MESSAGE_HISTORY, QUERY, SYSTEM_PROMPT, search_books
from prompt_refiner import ResponseCompressor, StripHTML, TextFormat, TextPacker
from agents import Agent, Runner, function_tool

# Tool with response compression
@function_tool
def search_books_tool(query: str) -> dict:
    """Search for books by query."""
    tool_response = search_books(query)

    # Compress response to reduce tokens
    compressor = ResponseCompressor()
    compressed_response = compressor.process(tool_response)

    return compressed_response

# Build structured, optimized input message
input_message = TextPacker.quick_pack(
    text_format=TextFormat.MARKDOWN,
    system="Context (use this when answering):",
    context=(
        CONTEXT_DOCUMENTS,  # Shared context documents with HTML
        [StripHTML()]  # Clean HTML from context docs
    ),
    history=MESSAGE_HISTORY,  # Shared message history
    query=QUERY  # Shared query
)

# Create agent (using shared system prompt)
agent = Agent(
    name="Book Recommender",
    instructions=SYSTEM_PROMPT,
    tools=[search_books_tool],
)

result = await Runner.run(agent, input=input_message)
```

**What prompt-refiner provides:**
- **TextPacker**: Structured MARKDOWN format (INSTRUCTIONS, CONTEXT, CONVERSATION, INPUT sections)
- **StripHTML**: HTML stripping and whitespace normalization
- **ResponseCompressor**: Removes debug fields, truncates long strings in tool responses
- Token-efficient grouping for OpenAI Agents

**What the framework handles:**
- Tool schema generation from `@function_tool`
- Automatic tool call loop
- Conversation state management
- Tool execution and response formatting

**Pros:**
- Much less boilerplate (~80 lines)
- Automatic schema generation
- Built-in error handling
- Cleaner code

**Cons:**
- Framework dependency
- Less low-level control
- Async/await required

### 3. `langchain_agent.py` - LangChain Framework

**Approach:** Use LangChain's agent system with prompt templates and built-in memory

```python
from shared_data import CONTEXT_DOCUMENTS, MESSAGE_HISTORY, QUERY, SYSTEM_PROMPT, search_books
from prompt_refiner import StripHTML
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# Strip HTML from context documents
strip_html = StripHTML()
cleaned_docs = [strip_html.refine(doc) for doc in CONTEXT_DOCUMENTS]
context_text = "\n".join(f"- {doc}" for doc in cleaned_docs)

# Convert dict format to LangChain message objects
message_history = [
    HumanMessage(content=MESSAGE_HISTORY[0]["content"]),
    AIMessage(content=MESSAGE_HISTORY[1]["content"]),
    HumanMessage(content=MESSAGE_HISTORY[2]["content"]),
    AIMessage(content=MESSAGE_HISTORY[3]["content"]),
]

# Create prompt template with placeholders
prompt = ChatPromptTemplate.from_messages([
    ("system", f"{SYSTEM_PROMPT}\n\nContext:\n{{context}}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create agent
llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_tool_calling_agent(llm, tools=[search_books_tool], prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Run with context and history
result = agent_executor.invoke({
    "context": context_text,
    "chat_history": message_history,
    "input": QUERY,
})
```

**What LangChain provides:**
- Unified interface across different LLMs (OpenAI, Anthropic, etc.)
- Rich ecosystem (vector stores, retrievers, memory)
- Prompt templating with variables
- Built-in conversation management
- Pre-built chains and agents

**Pros:**
- LLM-agnostic (easy to switch providers)
- Rich ecosystem of integrations
- Strong community and documentation
- Prompt templating makes context management easier
- Built-in memory and conversation handling

**Cons:**
- Steep learning curve (lots of abstractions)
- Can be "magical" - harder to debug
- Framework-specific patterns
- Performance overhead from abstraction layers
- Frequent API changes (evolving rapidly)

## Side-by-Side Comparison

| Feature | Baseline | OpenAI Client + Refiner | OpenAI Agents | LangChain |
|---------|----------|-------------------------|---------------|-----------|
| Shared data | ✅ | ✅ | ✅ | ✅ |
| Token optimization | ❌ | ✅ (MessagesPacker, SchemaCompressor, ResponseCompressor) | ✅ (TextPacker, ResponseCompressor) | ✅ (StripHTML) |
| Tool schema | Manual JSON | Manual JSON + SchemaCompressor | `@function_tool` | `@tool` decorator |
| Tool call loop | Manual | Manual | Automatic | Automatic |
| State management | Manual | Manual | Automatic | Automatic (with memory) |
| Code complexity | ~100 lines | ~110 lines | ~80 lines | ~100 lines |
| Control level | Full | Full | High-level | High-level |
| Async support | Optional | Optional | Required | Optional |
| LLM flexibility | OpenAI only | OpenAI only | OpenAI only | Any LLM |
| Prompt management | Manual strings | MessagesPacker/tuple API | TextPacker | Template system |
| Ecosystem | OpenAI SDK | OpenAI SDK + prompt-refiner | OpenAI agents | Huge (vectors, chains, etc) |
| Learning curve | Low | Low | Medium | High |
| Debugging | Easy | Easy | Medium | Hard |
| Token savings | 0% (baseline) | 10-50% vs baseline | 10-20% | 10-20% |

## When to Use Each

### Use Baseline (openai_client_baseline.py) When:
- 📊 Measuring token usage before optimization
- 🔬 A/B testing optimization impact
- 📈 Establishing performance benchmarks
- 🎓 Understanding raw OpenAI API behavior

### Use OpenAI Client + Refiner (openai_client.py) When:
- 💰 Need to reduce API costs (10-50% token savings)
- 🎓 Learning how LLMs work under the hood
- 🎯 Need fine-grained control over every API call
- 🔧 Building production workflows with RAG/context
- 📦 Want minimal dependencies (just prompt-refiner)
- 🔄 Working with synchronous code
- 🐛 Need easy debugging and transparency
- 🧹 Have dirty inputs (HTML, extra whitespace, debug fields)

### Use OpenAI Agents + TextPacker When:
- 🚀 Building production applications with OpenAI
- 🤖 Multi-step agent workflows
- 👥 Need multi-agent coordination
- 🧹 Want cleaner, maintainable code
- ⚡ Comfortable with async/await
- 🏢 Committed to OpenAI ecosystem
- 📝 Need structured MARKDOWN format for context
- 💰 Want token optimization with minimal code

### Use LangChain When:
- 🔀 Need flexibility to switch LLM providers (OpenAI, Anthropic, etc.)
- 🧩 Want rich ecosystem (vector stores, retrievers, memory)
- 📚 Building complex RAG applications
- 🔗 Need pre-built chains and workflows
- 🌐 Using multiple data sources and integrations
- 👥 Large team with LangChain experience
- 🎨 Want powerful prompt templating system

## Other Common Use Cases

Beyond tools, RAG, and history, here are other important patterns:

### 1. **Streaming Responses**
Get responses token-by-token for better UX.

**OpenAI Client:**
```python
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**OpenAI Agents:**
```python
async for chunk in Runner.run_stream(agent, input="Hello"):
    print(chunk.delta, end="")
```

### 2. **Structured Outputs**
Force responses to follow a specific JSON schema.

**OpenAI Client:**
```python
from pydantic import BaseModel

class BookRecommendation(BaseModel):
    title: str
    author: str
    reason: str

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=messages,
    response_format=BookRecommendation
)

book = response.choices[0].message.parsed
```

**OpenAI Agents:**
```python
from pydantic import BaseModel

class BookRecommendation(BaseModel):
    title: str
    author: str
    reason: str

agent = Agent(
    name="Recommender",
    instructions="Recommend a book.",
    output_type=BookRecommendation
)

result = await Runner.run(agent, input="Recommend a Python book")
# result.final_output is BookRecommendation instance
```

### 3. **Multi-Agent Orchestration**
Have multiple specialized agents work together.

**Only in OpenAI Agents:**
```python
# Specialized agents
research_agent = Agent(name="Researcher", ...)
writer_agent = Agent(name="Writer", ...)

# Orchestrator uses agents as tools
orchestrator = Agent(
    name="Orchestrator",
    tools=[
        research_agent.as_tool(),
        writer_agent.as_tool()
    ]
)

result = await Runner.run(orchestrator, input="Write a report on Python")
```

### 4. **Error Handling & Retries**

**OpenAI Client:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def call_with_retry():
    return client.chat.completions.create(...)
```

**OpenAI Agents:**
```python
@function_tool
def flaky_api(query: str) -> str:
    """Tool with built-in error handling."""
    try:
        return call_external_api(query)
    except Exception as e:
        return f"Error: {str(e)}"
```

### 5. **Token Usage & Cost Tracking**

**OpenAI Client:**
```python
response = client.chat.completions.create(...)

print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Completion tokens: {response.usage.completion_tokens}")
print(f"Total tokens: {response.usage.total_tokens}")

# Calculate cost (example for gpt-4o-mini)
cost = (response.usage.prompt_tokens * 0.00015 / 1000 +
        response.usage.completion_tokens * 0.0006 / 1000)
print(f"Cost: ${cost:.6f}")
```

**OpenAI Agents:**
```python
result = await Runner.run(agent, input="...")

# Access from result object (if available)
# or track via callbacks
```

### 6. **Context Window Management**
Handle conversations that exceed token limits.

**Strategy 1: Sliding window**
```python
def keep_recent_messages(messages, max_messages=10):
    # Keep system message + last N messages
    system = [m for m in messages if m["role"] == "system"]
    recent = messages[-max_messages:]
    return system + recent
```

**Strategy 2: Summarization**
```python
# Summarize old messages before adding new ones
summary = client.chat.completions.create(
    messages=[{"role": "user", "content": f"Summarize: {old_messages}"}]
)

new_messages = [
    {"role": "system", "content": f"Context: {summary}"},
    *recent_messages
]
```

### 7. **Response Validation**
Ensure responses meet criteria.

```python
def validate_response(text: str) -> bool:
    """Check if response meets requirements."""
    return (
        len(text) > 50 and
        "..." not in text and
        text.endswith(".")
    )

# Retry if invalid
max_attempts = 3
for attempt in range(max_attempts):
    response = client.chat.completions.create(...)
    if validate_response(response.choices[0].message.content):
        break
```

## Best Practices

### OpenAI Client
1. Always validate tool call arguments
2. Handle errors in tool execution
3. Keep conversation history manageable (token limits!)
4. Use structured logging for debugging
5. Consider rate limits and implement retries

### OpenAI Agents
1. Use descriptive docstrings (they become tool descriptions)
2. Add type hints (they define parameter schemas)
3. Keep tools focused and single-purpose
4. Handle errors within tool functions
5. Use async functions for I/O operations

## Next Steps

1. **Run the examples** - See the difference between client and agents
2. **Modify the examples** - Add your own context/tools
3. **Try streaming** - Implement token-by-token responses
4. **Add structured outputs** - Force JSON responses
5. **Build something!** - Apply to your use case

## Quick Recommendation

**Measuring baseline?** → Run `openai_client_baseline.py` first (establish token usage)
**Just learning?** → Start with OpenAI Client + Refiner (understand optimization basics)
**Building production app with OpenAI?** → Use OpenAI Agents + TextPacker (cleaner code + optimization)
**Need LLM flexibility or complex RAG?** → Use LangChain (rich ecosystem)
**Want to see token savings?** → Compare baseline vs optimized versions side-by-side

## Resources

### OpenAI
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

### OpenAI Agents
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [OpenAI Agents Documentation](https://openai.github.io/openai-agents-python/)

### LangChain
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangChain Agents Guide](https://python.langchain.com/docs/modules/agents/)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [LangChain Memory](https://python.langchain.com/docs/modules/memory/)
