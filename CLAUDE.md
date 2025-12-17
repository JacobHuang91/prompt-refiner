# Prompt Refiner - Project Context

This document provides context for Claude Code and developers working on this project.

## Project Purpose

Prompt Refiner is a Python library for building production LLM applications. It solves two core problems:

1. **Token Optimization** - Clean dirty inputs (HTML, whitespace, PII) to reduce API costs by 10-20%
2. **Context Management** - Pack system prompts, RAG docs, and chat history with automatic refinement and priority-based ordering

Perfect for RAG applications, chatbots, and any production system that needs to optimize LLM inputs efficiently.

## Architecture

The library is organized into 6 core transformation modules plus measurement utilities:

**Core Modules (Transform prompts):**
- **Cleaner**: Operations for cleaning dirty data (HTML, whitespace, Unicode, JSON)
- **Compressor**: Operations for reducing prompt size (truncation, deduplication)
- **Scrubber**: Operations for security and privacy (PII redaction)
- **Tools**: Operations for optimizing LLM tool schemas and responses (SchemaCompressor, ResponseCompressor) (v0.1.6+)
- **Packer**: Context composition with specialized packers and automatic refinement (v0.1.3+)
- **Strategy**: Benchmark-tested preset strategies (MinimalStrategy, StandardStrategy, AggressiveStrategy) (v0.1.5+)
  - **MessagesPacker**: For chat completion APIs (OpenAI, Anthropic)
  - **TextPacker**: For text completion APIs (Llama Base, GPT-3)
  - **Semantic roles for RAG**: ROLE_SYSTEM, ROLE_QUERY, ROLE_CONTEXT, ROLE_USER, ROLE_ASSISTANT
  - **Smart priority defaults**: Role automatically infers priority (PRIORITY_SYSTEM, PRIORITY_QUERY, PRIORITY_HIGH, PRIORITY_LOW)
  - **Default refining strategies**: Automatic cleaning (MinimalStrategy for system/query, StandardStrategy for context/history) (v0.2.1+)
  - Priority-based ordering with insertion order preservation
  - Grouped MARKDOWN sections for base models
  - Token savings tracking for optimization impact measurement

**Measurement Utilities (Analyze, don't transform):**
- **Analyzer**: Operations for measuring optimization impact (token counting, cost savings)

Each core module contains specialized operations that can be composed into pipelines using the `Refiner` class. The `Packer` module provides higher-level functionality for managing complex context budgets with support for both plain text and structured message formats. The Analyzer module provides measurement tools to track token savings and demonstrate ROI, but does not transform prompts.

## Development Philosophy

- Keep it lightweight - minimal dependencies (zero by default, optional for advanced features)
- Focus on performance - cleaning should be fast
- Make it configurable - users should control cleaning behavior
- Start simple - add features incrementally
- Graceful degradation - advanced features degrade gracefully when optional dependencies unavailable

## Version History

### v0.2.2 (Current) - Code Cleanup & Documentation Polish

**Non-Breaking Changes:**
- **Removed unused `model` parameter**: Cleaned up packer constructors
  - Removed from `BasePacker.__init__()`, `MessagesPacker.__init__()`, `MessagesPacker.quick_pack()`, `TextPacker.__init__()`, `TextPacker.quick_pack()`
  - Model parameter was never used internally, only stored
  - Follows YAGNI principle (You Aren't Gonna Need It)
  - Note: `model` parameter still exists in `CountTokens` operation for precise token counting

- **Removed unused TYPE_CHECKING blocks**: Cleaned up empty type checking imports in packer files

- **Documentation updates**:
  - Updated all examples to remove `model` parameter
  - Fixed README.md quickstart example
  - Updated API reference documentation
  - Clarified that `model` parameter is only for `CountTokens` operation

**Benefits:**
- Simpler, cleaner API
- No functional changes - purely cleanup
- Better code maintainability
- Reduced confusion about unused parameters

### v0.2.1 - Packer Simplification & Default Strategies
**BREAKING CHANGES:**

**Packer Simplification**
- **Removed `max_tokens` parameter**: Packers now include all items without token budget constraints
  - LLM APIs handle final token limits
  - Simpler API - no more budget management complexity
  - All items are included and ordered by priority, then insertion order
- **Removed overhead calculations**: No more `_calculate_overhead()`, `PER_MESSAGE_OVERHEAD`, `PER_REQUEST_OVERHEAD`
- **Renamed internal method**: `_greedy_select()` → `_select_items()` (simpler logic)
- **File renames**: `messages_packer.py` → `messages.py`, `text_packer.py` → `text.py`

**Default Refining Strategies (NEW)**
- Automatic refining applied when no explicit refiner provided:
  - `system`/`query`: MinimalStrategy (StripHTML + NormalizeWhitespace)
  - `context`/`history`: StandardStrategy (StripHTML + NormalizeWhitespace + Deduplicate)
- Override with tuple syntax: `context=(docs, StripHTML() | NormalizeWhitespace())`
- Improved UX: Clean inputs automatically without explicit configuration

**Migration Guide:**
```python
# OLD (v0.2.0)
packer = MessagesPacker(
    max_tokens=1000,
    system="You are helpful.",
    context=(["<div>Doc</div>"], [StripHTML()])
)

# NEW (v0.2.1)
packer = MessagesPacker(
    system="You are helpful.",  # Auto-refined with MinimalStrategy
    context=(["<div>Doc</div>"], StripHTML() | NormalizeWhitespace())  # Pipeline with |
)
```

**Benefits:**
- Simpler API (no token budget management)
- Automatic optimization with sensible defaults
- Easy to override when needed
- Cleaner pipeline syntax with `|` operator

### v0.2.0 - Strategy Refactoring
**BREAKING CHANGES:**

**Strategy Module Refactoring**
- **Strategies now inherit from Pipeline**: MinimalStrategy, StandardStrategy, and AggressiveStrategy now directly inherit from Pipeline class
- **Removed `.create_refiner()` method**: Strategies ARE pipelines now - use them directly with `.run()` or `.process()`
- **Fine-grained parameter control**: Each operator's parameters exposed with clear prefixing
  - `strip_html_to_markdown` - Configure StripHTML operator
  - `deduplicate_method`, `deduplicate_similarity_threshold`, `deduplicate_granularity` - Configure Deduplicate operator
  - `truncate_max_tokens`, `truncate_strategy` - Configure TruncateTokens operator
- **Simplified API**: Direct usage without intermediate conversion step
- **Consistent extension**: Use `.pipe()` method (inherited from Pipeline) to add operations
- **Type-safe**: Full IDE autocomplete for all operator parameters with Literal types
- **Removed BaseStrategy**: No longer needed with direct Pipeline inheritance

**Migration Guide:**
```python
# OLD (v0.1.x)
strategy = StandardStrategy()
refiner = strategy.create_refiner()
result = refiner.run(text)

# NEW (v0.2.0)
strategy = StandardStrategy()
result = strategy.run(text)  # Direct usage!

# Configure individual operators
strategy = StandardStrategy(
    deduplicate_method="levenshtein",
    deduplicate_similarity_threshold=0.9,
    strip_html_to_markdown=True
)

# Extend with .pipe()
extended = StandardStrategy().pipe(RedactPII())
```

**Benefits:**
- Simpler API (one less step)
- Better type safety (full parameter autocomplete)
- Cleaner code (strategies work exactly like Pipeline)
- More flexible (fine-grained control over preset operators)

### v0.1.6 - Tools Module
**New Operations:**

**SchemaCompressor**
- Compresses tool schemas (OpenAI/Anthropic function calling) to save tokens
- Never modifies protocol fields (name, type, required, enum)
- Only optimizes documentation fields (description, title, examples, markdown)
- Achieves 10-50% token savings depending on schema verbosity (simple: 10-15%, verbose: 30-50%)
- Simple API: all compression features enabled by default
- 21 comprehensive tests + real-world OpenAI integration example

**ResponseCompressor (NEW)**
- Compresses verbose tool/API responses before sending to LLM
- Hardcoded sensible limits: 512 chars per string, 16 items per list
- Removes debug/trace/logs fields automatically
- Optionally drops null values and empty containers
- Depth protection prevents infinite recursion
- Achieves 30-70% token savings on verbose API responses
- 24 comprehensive tests + OpenAI integration example showing 36% savings

**Use Cases:**
- Compress tool schemas for OpenAI/Anthropic function calling
- Compress verbose API/tool responses in agent systems
- Reduce token cost from verbose tool definitions and responses
- Fit more tools and tool outputs within token budget

### v0.1.5 - Preset Strategies & Token Savings Tracking
**Three Major Features:**

1. **Strategy Module (NEW)** *(Refactored in v0.2.0)*
   - 3 benchmark-tested preset strategies: MinimalStrategy, StandardStrategy, AggressiveStrategy
   - Direct instantiation API (v0.1.5: `MinimalStrategy().create_refiner()`, v0.2.0: `MinimalStrategy()`)
   - Type-safe with Literal types
   - Fully extensible with `.pipe()` for additional operations
   - 25 comprehensive tests + 3 focused example files

2. **Token Savings Tracking (NEW)**
   - Automatic token savings tracking in MessagesPacker and TextPacker
   - Opt-in via `track_savings=True` parameter
   - New `get_token_savings()` method returns aggregated statistics
   - Measures impact of `refine_with` operations during packing
   - 256 new tests for savings tracking functionality

3. **Packer Examples Enhancement**
   - Real OpenAI API integration in examples
   - `.env` support with `python-dotenv` for API keys
   - `examples/packer/README.md` with setup instructions
   - Demonstrates production usage patterns with token savings

**Documentation Updates:**
- README updated with strategy quick start and token savings tracking
- Updated examples from ContextPacker to MessagesPacker
- Enhanced measurement documentation

### v0.1.4 - Semantic Roles & Documentation Polish
**Enhancements:**
- **Semantic Roles**: Renamed `PRIORITY_USER` to `PRIORITY_QUERY` for clarity
- **Smart Defaults**: All examples now use semantic roles (ROLE_SYSTEM, ROLE_QUERY, ROLE_CONTEXT) with auto-inferred priorities
- **Documentation**: Polished README, removed duplicate sections, emphasized both token optimization AND context management use cases
- **Bug Fix**: Unlimited mode now correctly sorts by priority (system > query > context > history)

### v0.1.3 - Separated Packer Architecture
**New Architecture:**
- **`MessagesPacker`**: For chat completion APIs (OpenAI, Anthropic)
  - Returns `List[Dict[str, str]]` directly
  - Accurate ChatML overhead (4 tokens per message)
  - 100% token budget utilization with precise mode

- **`TextPacker`**: For text completion APIs (Llama Base, GPT-3)
  - Returns `str` directly
  - Multiple text formats: RAW, MARKDOWN, XML
  - Grouped MARKDOWN sections (INSTRUCTIONS, CONTEXT, CONVERSATION, INPUT)
  - "Entrance fee" overhead strategy for maximum token utilization

**Key Benefits:**
- Single Responsibility Principle: Each packer handles only its format
- Better type safety: Direct return types (no wrapper)
- More accurate: Each packer calculates only its overhead
- Better capacity: Grouped format + entrance fee strategy fits more content

### v0.1.2 - Optional Tiktoken Support
- Added optional tiktoken dependency for precise token counting
- Graceful degradation to character-based estimation
- 10% safety buffer in estimation mode

### v0.1.1 - ContextPacker Module
- Initial release of ContextPacker for priority-based token budget management

## Key Considerations

1. **Unicode handling**: Be careful with non-ASCII characters
2. **Whitespace**: Different types (spaces, tabs, newlines) need different handling
3. **Performance**: Process large prompts efficiently (target: < 0.5ms per 1k tokens)
4. **API stability**: v0.1.3 enhanced ContextPacker API. Keep API stable in patch versions.

## Technology Stack

- Python 3.9+
- uv for package management
- pytest for testing
- ruff for linting and formatting

### Optional Dependencies

- **tiktoken** (optional): For precise token counting
  - Install with: `pip install llm-prompt-refiner[token]`
  - Opt-in by passing `model` parameter to CountTokens operation
  - Falls back to character-based estimation if unavailable

## Code Style

- Follow PEP 8
- Use type hints
- Keep functions small and focused
- Write clear docstrings

## Project Structure

```
src/prompt_refiner/
├── __init__.py          # Main exports
├── refiner.py           # Pipeline builder
├── operation.py         # Base operation class
├── cleaner/             # Cleaner module
│   ├── html.py
│   ├── whitespace.py
│   ├── unicode.py
│   └── json.py
├── compressor/          # Compressor module
│   ├── truncate.py
│   └── deduplicate.py
├── scrubber/            # Scrubber module
│   └── pii.py
├── tools/               # Tools module (v0.1.6+)
│   ├── schema_compressor.py
│   └── response_compressor.py
├── analyzer/            # Analyzer module
│   └── counter.py
├── packer/              # Packer module (v0.1.3+)
│   ├── base.py          # Abstract base class
│   ├── messages.py      # Chat completion APIs
│   └── text.py          # Text completion APIs
└── strategy/            # Strategy module (v0.1.5+)
    ├── __init__.py
    ├── minimal.py       # MinimalStrategy
    ├── standard.py      # StandardStrategy
    └── aggressive.py    # AggressiveStrategy

tests/
├── test_refiner.py      # Pipeline tests
├── test_cleaner.py      # Cleaner module tests
├── test_compressor.py   # Compressor module tests
├── test_scrubber.py     # Scrubber module tests
├── test_schema_compressor.py  # SchemaCompressor tests
├── test_response_compressor.py  # ResponseCompressor tests
├── test_analyzer.py     # Analyzer module tests
├── test_messages_packer.py  # MessagesPacker tests
├── test_text_packer.py  # TextPacker tests
└── test_strategy.py     # Strategy tests

examples/
├── cleaner/             # Cleaner examples
├── compressor/          # Compressor examples
├── scrubber/            # Scrubber examples
├── tools/               # Tools examples
├── analyzer/            # Analyzer examples
├── packer/              # Packer examples
└── strategy/            # Strategy examples
    ├── minimal.py       # MinimalStrategy example
    ├── standard.py      # StandardStrategy example
    └── aggressive.py    # AggressiveStrategy example

benchmark/
├── README.md            # Index of all benchmarks
├── function_calling/    # Function calling optimization (⭐ primary benchmark)
│   ├── benchmark_schemas.py              # SchemaCompressor benchmark
│   ├── benchmark_responses.py            # ResponseCompressor benchmark
│   ├── test_functional_equivalence.py    # Validates compressed schemas work with OpenAI (20 schemas)
│   ├── visualize_results.py              # Generate charts
│   ├── data/
│   │   ├── schemas/                      # 20 tool schemas (JSON)
│   │   └── responses/                    # 20 API responses (JSON)
│   └── results/                          # Generated results (CSV, MD, PNG)
├── packer/              # MessagesPacker & TextPacker validation
│   ├── benchmark.py     # Comprehensive packer benchmark (5 tests)
│   └── results/         # Generated results (CSV)
├── rag_quality/         # Quality/cost A/B testing benchmark
│   ├── benchmark.py     # Main orchestrator
│   ├── datasets.py      # Test data loader
│   ├── evaluators.py    # Quality metrics (cosine + LLM judge)
│   ├── visualizer.py    # Matplotlib plots
│   ├── data/            # 30 curated test cases
│   │   ├── squad_samples.json
│   │   └── rag_scenarios.json
│   └── results/         # Generated results (CSV, MD, PNG)
└── latency/             # Latency/performance benchmark
    ├── benchmark.py     # Performance measurement script
    └── README.md        # Latency benchmark documentation
```

## Testing & Benchmarking

### Unit Tests
- Unit tests for all operations organized by module
- Edge case testing (empty strings, Unicode, very long inputs)
- Tests are separated by module for better organization

### Benchmarks
- **Function Calling Benchmark**: SchemaCompressor/ResponseCompressor on 20 real-world APIs (56.9% avg reduction, 100% callable validated)
- **Packer Benchmark**: MessagesPacker/TextPacker functionality validation (5 comprehensive tests, all passing)
- **RAG Quality Benchmark**: Measures token reduction (4-15%) and response quality (96-99%)
- **Latency Benchmark**: Measures processing overhead (< 0.5ms per 1k tokens)

## Future Vision

This will eventually become a product offering prompt optimization as a service. The library is the foundation for that product.
