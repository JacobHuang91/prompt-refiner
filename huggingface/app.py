import time
import json
import streamlit as st
import tiktoken
from prompt_refiner import MinimalStrategy, StandardStrategy, AggressiveStrategy, SchemaCompressor

# --- Page Configuration ---
st.set_page_config(
    page_title="Prompt Refiner - Interactive Demo",
    page_icon="🧹",
    layout="wide",
)

# --- Helper Functions ---
def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using tiktoken (GPT-4 tokenizer)."""
    if not text:
        return 0
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        return len(text.split())


def calculate_savings(original_tokens: int, final_tokens: int) -> dict:
    """Calculate token savings and cost impact."""
    saved_tokens = original_tokens - final_tokens
    saved_percentage = (saved_tokens / original_tokens * 100) if original_tokens > 0 else 0

    # GPT-4 input pricing: $0.03 per 1K tokens
    PRICE_PER_1K_TOKENS = 0.03

    cost_per_1k_calls = (saved_tokens / 1000) * PRICE_PER_1K_TOKENS * 1000
    cost_per_month_1m = (saved_tokens / 1000) * PRICE_PER_1K_TOKENS * 1_000_000

    return {
        "saved_tokens": saved_tokens,
        "saved_percentage": saved_percentage,
        "cost_per_1k": cost_per_1k_calls,
        "cost_per_month": cost_per_month_1m,
    }


# --- Main App ---
st.title("🧹 Prompt Refiner - Interactive Demo")
st.markdown(
    """
**Optimize LLM inputs with benchmark-tested strategies.** Save tokens, reduce costs, improve context usage.

[![GitHub](https://img.shields.io/github/stars/JacobHuang91/prompt-refiner?style=social)](https://github.com/JacobHuang91/prompt-refiner)
[![PyPI](https://img.shields.io/pypi/v/llm-prompt-refiner)](https://pypi.org/project/llm-prompt-refiner/)
"""
)

st.divider()

# --- Tabs ---
tab1, tab2 = st.tabs(["📝 Text Optimization", "🔧 Function Calling"])

# ============================================================================
# TAB 1: TEXT OPTIMIZATION
# ============================================================================

with tab1:
    # --- Preset Examples for Text ---
    TEXT_EXAMPLES = {
        "E-commerce RAG Context": {
            "text": """<div class="products">
    <div class="product">
        <h2>Laptop Pro 15</h2>
        <p>High-performance laptop with 16GB RAM and 512GB SSD</p>
        <p>Price: $999</p>
        <p>Rating: 4.5/5 stars</p>
    </div>
    <div class="product">
        <h2>Laptop Pro 15</h2>
        <p>High-performance laptop with 16GB RAM and 512GB SSD</p>
        <p>Price: $999</p>
        <p>Rating: 4.5/5 stars</p>
    </div>
    <div class="product">
        <h2>Tablet X</h2>
        <p>Lightweight tablet with stylus support and 10-inch display</p>
        <p>Price: $599</p>
        <p>Rating: 4.2/5 stars</p>
    </div>
</div>""",
            "description": "Product listings scraped from web - contains HTML tags and duplicates",
            "recommended": "Standard",
            "why": "HTML needs cleaning, duplicates should be removed, but preserve all product info",
        },
        "Customer Support Ticket": {
            "text": """Customer Name: John Doe
Email:    john.doe@example.com
Phone:    555-123-4567

Issue:   Billing    problem    with   excessive   spaces

Description:    I    was    charged    twice    for    my    subscription.
Please    contact    me    at    john.doe@example.com    or    call    555-123-4567.

The    transaction    IDs    are:    TXN-12345    and    TXN-67890.
My    account    number    is    ACC-999888777.
""",
            "description": "Support ticket with PII (emails, phones) and excessive whitespace",
            "recommended": "Aggressive",
            "why": "Remove PII for privacy, clean excessive whitespace, keep key information",
        },
        "Technical Documentation": {
            "text": """<div class="documentation">
    <h1>   Installation   Guide   </h1>
    <p>  To install the package, run the following command:  </p>
    <pre><code>  pip install llm-prompt-refiner  </code></pre>

    <h2>   Quick    Start   </h2>
    <p>   Import the library:   </p>
    <pre><code>from prompt_refiner import MinimalStrategy</code></pre>
</div>""",
            "description": "HTML documentation with preserved code structure",
            "recommended": "Minimal",
            "why": "Light cleaning to remove HTML and normalize whitespace",
        },
    }

    # Strategy descriptions
    STRATEGY_INFO = {
        "Minimal": {
            "emoji": "⚡",
            "description": "Light cleaning for well-formatted text",
            "operations": ["StripHTML", "NormalizeWhitespace"],
            "use_cases": "Documentation, clean datasets, structured content",
            "avg_reduction": "4.3%",
            "quality": "98.7%",
        },
        "Standard": {
            "emoji": "🎯",
            "description": "Balanced optimization for most use cases",
            "operations": ["StripHTML", "NormalizeWhitespace", "Deduplicate"],
            "use_cases": "RAG contexts, web scraping, general text processing",
            "avg_reduction": "4.8%",
            "quality": "98.4%",
        },
        "Aggressive": {
            "emoji": "🚀",
            "description": "Maximum compression for noisy data",
            "operations": ["StripHTML", "NormalizeWhitespace", "Deduplicate", "RedactPII", "TruncateTokens"],
            "use_cases": "Messy web data, PII-sensitive content, token-constrained contexts",
            "avg_reduction": "15.0%",
            "quality": "96.4%",
        },
    }

    # --- Sidebar for Tab 1 ---
    with st.sidebar:
        st.header("⚙️ Choose Strategy")

        strategy_choice = st.radio(
            "Select optimization strategy:",
            ["Minimal", "Standard", "Aggressive"],
            help="Each strategy is benchmark-tested and production-ready",
        )

        info = STRATEGY_INFO[strategy_choice]
        st.info(f"""
**{info['emoji']} {strategy_choice} Strategy**

{info['description']}

**Operations:**
{', '.join(info['operations'])}

**Best for:**
{info['use_cases']}

**Benchmark Results:**
- Avg Token Reduction: {info['avg_reduction']}
- Quality Preservation: {info['quality']}
""")

    # --- Content for Tab 1 ---
    st.subheader("📝 Select Example")
    selected_example = st.selectbox(
        "Choose a preset example or enter custom text:",
        ["Custom"] + list(TEXT_EXAMPLES.keys()),
        help="Each example demonstrates a different use case",
        key="text_example_select"
    )

    if selected_example != "Custom":
        example_data = TEXT_EXAMPLES[selected_example]
        default_text = example_data["text"]

        with st.expander(f"ℹ️ About this example", expanded=True):
            st.write(f"**Description:** {example_data['description']}")
            st.write(f"**Recommended Strategy:** {example_data['recommended']}")
            st.write(f"**Why:** {example_data['why']}")
    else:
        default_text = """<div>
    <p>Enter your text here...</p>
    <p>Try adding HTML tags, duplicates, or PII like test@example.com</p>
</div>"""

    st.divider()

    # Input/Output columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 Original Input")
        raw_text = st.text_area(
            "Input Text:",
            value=default_text,
            height=400,
            help="Paste your text here",
            label_visibility="collapsed",
            key="text_input"
        )
        raw_tokens = count_tokens(raw_text)
        st.caption(f"📊 **{raw_tokens:,} tokens**")

    # Process the text
    result = None
    cleaned_tokens = 0
    processing_time = 0

    if raw_text.strip():
        start_time = time.time()
        try:
            if strategy_choice == "Minimal":
                strategy = MinimalStrategy()
            elif strategy_choice == "Standard":
                strategy = StandardStrategy()
            else:
                strategy = AggressiveStrategy()

            result = strategy.run(raw_text)
            processing_time = (time.time() - start_time) * 1000
            cleaned_tokens = count_tokens(result)

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

    with col2:
        st.subheader("✨ Optimized Output")
        if result is not None:
            st.text_area(
                "Result:", value=result, height=400, label_visibility="collapsed", key="text_output"
            )
            st.caption(f"📊 **{cleaned_tokens:,} tokens**")
        else:
            st.info("👈 Enter text to see optimization results")

    # Metrics
    if result is not None and raw_text.strip():
        st.divider()
        st.subheader("📊 Performance Metrics")

        savings = calculate_savings(raw_tokens, cleaned_tokens)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Original", f"{raw_tokens:,} tokens")
        with m2:
            st.metric(
                "Optimized",
                f"{cleaned_tokens:,} tokens",
                delta=f"-{savings['saved_tokens']:,}",
                delta_color="normal",
            )
        with m3:
            st.metric("Reduction", f"{savings['saved_percentage']:.1f}%")
        with m4:
            st.metric("Processing", f"{processing_time:.1f}ms")

        if savings["saved_percentage"] > 0:
            st.success(
                f"""
**💰 Cost Savings (GPT-4 pricing):**
- Per 1,000 calls: **${savings['cost_per_1k']:.2f}**
- Per 1M calls/month: **${savings['cost_per_month']:.2f}/month**
"""
            )

# ============================================================================
# TAB 2: FUNCTION CALLING
# ============================================================================

with tab2:
    st.subheader("🔧 Function Calling Optimization")
    st.markdown("""
Compress OpenAI/Anthropic tool schemas by **57% on average** while preserving 100% functionality.
Tested on 20 real-world APIs with **100% callable validation**.
""")

    # --- Example Tool Schemas ---
    TOOL_EXAMPLES = {
        "Weather API (Simple)": {
            "schema": {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather information for a specific location. This function retrieves real-time weather data including temperature, humidity, wind speed, and general conditions for any city worldwide.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, for example: San Francisco, CA or Paris, France. Please provide the full city name and country/state for accurate results."
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "description": "The temperature unit to use for the weather data. Options are celsius or fahrenheit. Default is fahrenheit if not specified."
                            }
                        },
                        "required": ["location"]
                    }
                }
            },
            "category": "Simple",
            "expected_reduction": "~20%"
        },
        "Stripe Payment (Complex)": {
            "schema": {
                "type": "function",
                "function": {
                    "name": "create_payment_intent",
                    "description": "Creates a new PaymentIntent object to process a payment. A PaymentIntent guides you through the process of collecting a payment from your customer. The PaymentIntent transitions through multiple statuses throughout its lifetime as it interfaces with Stripe.js to perform authentication flows and ultimately creates at most one successful charge.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "integer",
                                "description": "Amount intended to be collected by this PaymentIntent. A positive integer representing how much to charge in the smallest currency unit (e.g., 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency). The minimum amount is $0.50 US or equivalent in charge currency."
                            },
                            "currency": {
                                "type": "string",
                                "description": "Three-letter ISO currency code, in lowercase. Must be a supported currency. See the full list of supported currencies in the Stripe documentation."
                            },
                            "customer": {
                                "type": "string",
                                "description": "ID of the Customer this PaymentIntent belongs to, if one exists. Payment methods attached to other Customers cannot be used with this PaymentIntent. If present in combination with setup_future_usage, this PaymentIntent's payment method will be attached to the Customer after the PaymentIntent has been confirmed and any required actions from the user are complete."
                            }
                        },
                        "required": ["amount", "currency"]
                    }
                }
            },
            "category": "Complex",
            "expected_reduction": "~60%"
        },
        "HubSpot Contact (Very Verbose)": {
            "schema": {
                "type": "function",
                "function": {
                    "name": "create_hubspot_contact",
                    "description": "Create a new contact in HubSpot CRM. This endpoint allows you to create a new contact record in your HubSpot account. Contacts are the people you do business with and are stored in the contacts database. Each contact record contains information about a single person, including their name, email address, phone number, company affiliation, and any other custom properties you've created. This is the primary method for adding new leads, prospects, or customers to your CRM system. You can use this to programmatically add contacts from forms, integrations, or any other source. The contact will be immediately available in your HubSpot portal and can be used in workflows, lists, and reports.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "The contact's primary email address. This is a unique identifier for the contact in HubSpot. If a contact with this email already exists, the request will update that contact instead of creating a new one. Email addresses must be valid and properly formatted according to RFC 5322 standards. This field is commonly used for email marketing, sales outreach, and automated communication workflows."
                            },
                            "firstname": {
                                "type": "string",
                                "description": "The contact's first name or given name. This is used for personalization in emails, forms, and reports. It's a best practice to always collect the first name when possible as it improves engagement rates in email campaigns and makes your communications feel more personal and human."
                            },
                            "lastname": {
                                "type": "string",
                                "description": "The contact's last name or family name or surname. This field, combined with the first name, provides the contact's full name for formal communications, reports, and contact management. Having both first and last names enables better sorting, searching, and professional communication with your contacts."
                            }
                        },
                        "required": ["email"]
                    }
                }
            },
            "category": "Very Verbose",
            "expected_reduction": "~70%"
        }
    }

    # --- Content for Tab 2 ---
    st.subheader("🔍 Select Tool Schema")
    selected_tool = st.selectbox(
        "Choose an example tool or paste your own schema:",
        ["Custom"] + list(TOOL_EXAMPLES.keys()),
        help="Each example shows different compression rates",
        key="tool_example_select"
    )

    if selected_tool != "Custom":
        tool_data = TOOL_EXAMPLES[selected_tool]
        default_schema = json.dumps(tool_data["schema"], indent=2)

        with st.expander(f"ℹ️ About this schema", expanded=True):
            st.write(f"**Category:** {tool_data['category']}")
            st.write(f"**Expected Reduction:** {tool_data['expected_reduction']}")
            st.write("**Note:** Protocol fields (name, type, required, enum) are never modified - only descriptions are optimized")
    else:
        default_schema = json.dumps({
            "type": "function",
            "function": {
                "name": "your_function_name",
                "description": "Your verbose function description here...",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }, indent=2)

    st.divider()

    # Input/Output columns for tools
    tool_col1, tool_col2 = st.columns(2)

    with tool_col1:
        st.subheader("📥 Original Schema")
        schema_input = st.text_area(
            "Tool Schema (JSON):",
            value=default_schema,
            height=400,
            help="Paste your OpenAI/Anthropic tool schema",
            label_visibility="collapsed",
            key="schema_input"
        )

        try:
            original_schema = json.loads(schema_input)
            original_tokens = count_tokens(schema_input)
            st.caption(f"📊 **{original_tokens:,} tokens**")
            schema_valid = True
        except json.JSONDecodeError:
            st.error("⚠️ Invalid JSON format")
            schema_valid = False

    # Process schema
    compressed_result = None
    compressed_tokens = 0
    schema_processing_time = 0

    if schema_valid and schema_input.strip():
        start_time = time.time()
        try:
            compressor = SchemaCompressor()
            compressed_schema = compressor.process(original_schema)
            compressed_result = json.dumps(compressed_schema, indent=2)
            compressed_tokens = count_tokens(compressed_result)
            schema_processing_time = (time.time() - start_time) * 1000

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

    with tool_col2:
        st.subheader("✨ Compressed Schema")
        if compressed_result:
            st.text_area(
                "Compressed:", value=compressed_result, height=400, label_visibility="collapsed", key="schema_output"
            )
            st.caption(f"📊 **{compressed_tokens:,} tokens**")
        else:
            st.info("👈 Enter valid JSON schema to see compression")

    # Metrics for tools
    if compressed_result and schema_valid:
        st.divider()
        st.subheader("📊 Compression Results")

        schema_savings = calculate_savings(original_tokens, compressed_tokens)

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("Original", f"{original_tokens:,} tokens")
        with s2:
            st.metric(
                "Compressed",
                f"{compressed_tokens:,} tokens",
                delta=f"-{schema_savings['saved_tokens']:,}",
                delta_color="normal",
            )
        with s3:
            st.metric("Reduction", f"{schema_savings['saved_percentage']:.1f}%")
        with s4:
            st.metric("Processing", f"{schema_processing_time:.1f}ms")

        if schema_savings["saved_percentage"] > 0:
            st.success(
                f"""
**💰 Cost Savings for AI Agents:**

**Small Agent** (5 tools, 100 calls/day):
- Daily: ${(schema_savings['saved_tokens'] * 5 * 100 / 1000 * 0.03):.2f}
- Monthly: **${(schema_savings['saved_tokens'] * 5 * 100 * 30 / 1000 * 0.03):.2f}**

**Medium Agent** (10 tools, 500 calls/day):
- Monthly: **${(schema_savings['saved_tokens'] * 10 * 500 * 30 / 1000 * 0.03):.2f}**

**Large Agent** (20 tools, 1000 calls/day):
- Monthly: **${(schema_savings['saved_tokens'] * 20 * 1000 * 30 / 1000 * 0.03):.2f}**

*Based on GPT-4 pricing ($0.03/1k tokens)*
"""
            )

        st.info("""
**✅ Guaranteed Safe:**
- 100% lossless compression (protocol fields preserved)
- 100% callable (validated with OpenAI)
- Works with OpenAI & Anthropic function calling
""")

# ============================================================================
# BOTTOM SECTION (Shared)
# ============================================================================

st.divider()

with st.sidebar:
    st.divider()
    st.caption("📖 [Documentation](https://jacobhuang91.github.io/prompt-refiner/)")
    st.caption("💻 [GitHub](https://github.com/JacobHuang91/prompt-refiner)")
    st.caption("📦 [PyPI](https://pypi.org/project/llm-prompt-refiner/)")

st.markdown(
    """
## 🚀 Quick Start

### Installation
```bash
pip install llm-prompt-refiner
```

### Text Optimization
```python
from prompt_refiner import StandardStrategy

strategy = StandardStrategy()
cleaned = strategy.run(dirty_text)
```

### Function Calling Compression
```python
from prompt_refiner import SchemaCompressor

compressor = SchemaCompressor()
compressed_schema = compressor.process(tool_schema)
```

### 📖 Learn More

- [Full Documentation](https://jacobhuang91.github.io/prompt-refiner/)
- [Benchmark Results](https://github.com/JacobHuang91/prompt-refiner/tree/main/benchmark)
- [GitHub Repository](https://github.com/JacobHuang91/prompt-refiner)

---

Made with ❤️ by [Xinghao Huang](https://github.com/JacobHuang91) | `pip install llm-prompt-refiner`
"""
)
