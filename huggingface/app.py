import time
import streamlit as st
import tiktoken
from prompt_refiner import (
    StripHTML,
    NormalizeWhitespace,
    FixUnicode,
    Deduplicate,
    TruncateTokens,
    RedactPII,
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Prompt Refiner - Interactive Demo",
    page_icon="🧹",
    layout="wide",
)

# --- Preset Examples ---
PRESET_EXAMPLES = {
    "E-commerce Product Search": {
        "text": """<div class="products">
    <div class="product">
        <h2>Laptop Pro 15</h2>
        <p>High-performance laptop with 16GB RAM</p>
        <p>Price: $999</p>
    </div>
    <div class="product">
        <h2>Laptop Pro 15</h2>
        <p>High-performance laptop with 16GB RAM</p>
        <p>Price: $999</p>
    </div>
    <div class="product">
        <h2>Tablet X</h2>
        <p>Lightweight tablet with stylus support</p>
        <p>Price: $599</p>
    </div>
    <div class="product">
        <h2>Tablet X</h2>
        <p>Lightweight tablet with stylus support</p>
        <p>Price: $599</p>
    </div>
</div>""",
        "description": "Product listings with HTML and duplicates",
        "recommended": "🎯 Standard (with deduplication)",
    },
    "Customer Support Ticket": {
        "text": """Customer Name: John Doe
Email:    john.doe@example.com
Phone:    555-123-4567
IP Address: 192.168.1.1

Issue:   Billing    problem    with   excessive   spaces    and    formatting

Description:    I    was    charged    twice    for    my    subscription.
Please    contact    me    at    john.doe@example.com    or    call    555-123-4567.

Additional    information    with    way    too    many    spaces    between    words.
""",
        "description": "Support ticket with PII and formatting issues",
        "recommended": "🚀 Aggressive (redact PII + clean whitespace)",
    },
    "Documentation Snippet": {
        "text": """<div class="documentation">
    <h1>   Installation   Guide   </h1>
    <p>  To install the package, run the following command:  </p>
    <pre><code>  pip install llm-prompt-refiner  </code></pre>

    <h2>   Quick    Start   </h2>
    <p>   Import the library:   </p>
    <pre><code>from prompt_refiner import Refiner</code></pre>

    <p>   For more information, visit our website at https://example.com/docs   </p>
</div>""",
        "description": "HTML documentation with excessive whitespace",
        "recommended": "⚡ Minimal (basic cleaning)",
    },
    "Code Documentation": {
        "text": """/**
 * Calculate the total price of items in cart
 * Calculate the total price of items in cart
 *
 * @param items - Array of cart items
 * @param items - Array of cart items
 * @return Total price
 * @return Total price
 */
function    calculateTotal(items)    {
    let    total    =    0;

    // Loop through items
    // Loop through items
    for    (let    item    of    items)    {
        total    +=    item.price;
        total    +=    item.price;
    }

    return    total;
}""",
        "description": "Code with duplicate comments and excessive spaces",
        "recommended": "🎯 Standard (deduplicate + clean)",
    },
    "News Article": {
        "text": """Breaking News: Tech Company Announces New Product

In a press conference today, TechCorp CEO Jane Smith announced the launch of their revolutionary new product. The product, which has been in development for three years, promises to change the industry.

"This is a game-changer," said Smith during the announcement. "We've invested millions in research and development to bring this to market." The company expects significant revenue growth from this launch.

Industry analysts predict the product will be well-received. "TechCorp has a strong track record," said market analyst John Johnson. "Their latest innovation continues this trend of excellence."

The product will be available next month at a starting price of $299. Pre-orders begin next week through the company website at https://techcorp.example.com.

For more information, contact press@techcorp.example.com or call 1-800-555-0199.

TechCorp, founded in 1995, is a leading technology company with over 10,000 employees worldwide. The company specializes in consumer electronics and software solutions. Their previous products have won numerous awards and achieved strong market penetration.

This announcement comes amid growing competition in the tech sector. Rivals have announced similar products in recent months. However, industry experts believe TechCorp's brand strength and innovation will help them maintain their market leadership position.

Stock prices rose 5% following the announcement. Investors appear optimistic about the company's future prospects. Quarterly earnings reports are expected next month, which will provide more insight into the financial impact of this launch.
""",
        "description": "Long news article for truncation testing",
        "recommended": "🚀 Aggressive (truncate to key info)",
    },
    "RAG Context (Mixed Issues)": {
        "text": """<div class="search-results">
    <div class="result">
        <h3>User Profile: Alice Johnson</h3>
        <p>Email: alice@example.com</p>
        <p>Phone: 555-0101</p>
        <p>Account Status: Active</p>
        <p>Last Login: 2024-01-15</p>
    </div>

    <div class="result">
        <h3>User Profile: Alice Johnson</h3>
        <p>Email: alice@example.com</p>
        <p>Phone: 555-0101</p>
        <p>Account Status: Active</p>
        <p>Last Login: 2024-01-15</p>
    </div>

    <div class="result">
        <h3>User   Activity   Log</h3>
        <p>IP:   192.168.1.100   </p>
        <p>Action:    Login    successful    </p>
        <p>Timestamp:    2024-01-15   10:30:00   </p>
    </div>

    <div class="result">
        <h3>Purchase History</h3>
        <p>Credit Card: 4532-1234-5678-9012</p>
        <p>Amount: $99.99</p>
        <p>Date: 2024-01-10</p>
    </div>
</div>""",
        "description": "RAG context with HTML, duplicates, PII, and formatting issues",
        "recommended": "🚀 Aggressive (all operations)",
    },
}


# --- Helper Functions ---
def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using tiktoken (GPT-4 tokenizer)."""
    if not text:
        return 0
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback to simple word count if tiktoken fails
        return len(text.split())


def calculate_cost_savings(original_tokens: int, final_tokens: int) -> dict:
    """Calculate estimated cost savings."""
    # GPT-4 input pricing: $0.03 per 1K tokens (as of 2024)
    PRICE_PER_1K_TOKENS = 0.03

    saved_tokens = original_tokens - final_tokens
    saved_percentage = (saved_tokens / original_tokens * 100) if original_tokens > 0 else 0

    # Cost per 1K calls
    cost_per_1k = (saved_tokens / 1000) * PRICE_PER_1K_TOKENS * 1000

    # Monthly savings (1M calls)
    monthly_savings = (saved_tokens / 1000) * PRICE_PER_1K_TOKENS * 1_000_000

    return {
        "saved_tokens": saved_tokens,
        "saved_percentage": saved_percentage,
        "cost_per_1k": cost_per_1k,
        "monthly_savings": monthly_savings,
    }


def apply_preset_strategy(strategy: str) -> dict:
    """Return configuration for preset strategy."""
    if strategy == "⚡ Minimal":
        return {
            "strip_html": True,
            "normalize_whitespace": True,
            "fix_unicode": False,
            "deduplicate": False,
            "truncate": False,
            "redact_pii": False,
        }
    elif strategy == "🎯 Standard":
        return {
            "strip_html": True,
            "normalize_whitespace": True,
            "fix_unicode": True,
            "deduplicate": True,
            "truncate": False,
            "redact_pii": False,
        }
    elif strategy == "🚀 Aggressive":
        return {
            "strip_html": True,
            "normalize_whitespace": True,
            "fix_unicode": True,
            "deduplicate": True,
            "truncate": True,
            "redact_pii": True,
        }
    else:  # Custom
        return {}


# --- Main App ---
st.title("🧹 Prompt Refiner")
st.markdown(
    """
**Stop paying for invisible tokens.** Optimize your LLM inputs to save costs, improve context usage, and enhance security.

[![GitHub](https://img.shields.io/github/stars/JacobHuang91/prompt-refiner?style=social)](https://github.com/JacobHuang91/prompt-refiner)
[![PyPI](https://img.shields.io/pypi/v/llm-prompt-refiner)](https://pypi.org/project/llm-prompt-refiner/)
"""
)

st.divider()

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")

    # Preset Strategy Selection
    st.subheader("Quick Presets")
    strategy = st.radio(
        "Choose a strategy:",
        ["⚡ Minimal", "🎯 Standard", "🚀 Aggressive", "🔧 Custom"],
        help="Select a preset or customize your own configuration",
    )

    # Apply preset if not custom
    if strategy != "🔧 Custom":
        preset_config = apply_preset_strategy(strategy)
    else:
        preset_config = {}

    st.divider()

    # --- Cleaner Module ---
    st.subheader("🧼 Cleaner")
    use_html = st.checkbox(
        "Strip HTML",
        value=preset_config.get("strip_html", True),
        help="Remove HTML tags and convert to plain text",
    )

    use_whitespace = st.checkbox(
        "Normalize Whitespace",
        value=preset_config.get("normalize_whitespace", True),
        help="Collapse multiple spaces, tabs, and newlines",
    )

    use_unicode = st.checkbox(
        "Fix Unicode",
        value=preset_config.get("fix_unicode", False),
        help="Remove zero-width spaces and problematic Unicode characters",
    )

    st.divider()

    # --- Compressor Module ---
    st.subheader("🗜️ Compressor")

    use_deduplicate = st.checkbox(
        "Deduplicate",
        value=preset_config.get("deduplicate", False),
        help="Remove duplicate or highly similar text chunks",
    )

    if use_deduplicate:
        dedup_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.7,
            max_value=0.95,
            value=0.85,
            step=0.05,
            help="Higher = more similar text needed to remove",
        )
        dedup_granularity = st.selectbox("Granularity", ["sentence", "paragraph"])
        dedup_method = st.selectbox("Method", ["jaccard", "levenshtein"])
    else:
        dedup_threshold = 0.85
        dedup_granularity = "paragraph"
        dedup_method = "jaccard"

    use_truncate = st.checkbox(
        "Truncate Tokens",
        value=preset_config.get("truncate", False),
        help="Limit text to a maximum number of tokens",
    )

    if use_truncate:
        max_tokens = st.slider(
            "Max Tokens", min_value=100, max_value=2000, value=500, step=50
        )
        truncate_strategy = st.selectbox(
            "Strategy",
            ["head", "tail", "middle_out"],
            help="head: keep start, tail: keep end, middle_out: keep both ends",
        )
        respect_boundary = st.checkbox(
            "Respect Sentence Boundary", value=True, help="Truncate at sentence breaks"
        )
    else:
        max_tokens = 500
        truncate_strategy = "head"
        respect_boundary = True

    st.divider()

    # --- Scrubber Module ---
    st.subheader("🔒 Scrubber")

    use_pii = st.checkbox(
        "Redact PII",
        value=preset_config.get("redact_pii", False),
        help="Redact personally identifiable information",
    )

    if use_pii:
        pii_types = st.multiselect(
            "PII Types to Redact",
            ["email", "phone", "ip", "credit_card", "ssn", "url"],
            default=["email", "phone"],
        )
    else:
        pii_types = []

    st.divider()

    # Info
    st.caption("📖 [Documentation](https://jacobhuang91.github.io/prompt-refiner/)")
    st.caption("💻 [GitHub](https://github.com/JacobHuang91/prompt-refiner)")
    st.caption("📦 [PyPI](https://pypi.org/project/llm-prompt-refiner/)")

# --- Main Content ---

# Preset example selection (moved to top)
selected_example = st.selectbox(
    "Choose a preset example or enter custom text:",
    ["Custom"] + list(PRESET_EXAMPLES.keys()),
    help="Select a pre-configured example to see prompt-refiner in action",
)

if selected_example != "Custom":
    example_data = PRESET_EXAMPLES[selected_example]
    default_text = example_data["text"]
    with st.expander("ℹ️ About this example", expanded=False):
        st.write(f"**{example_data['description']}**")
        st.write(f"**Recommended:** {example_data['recommended']}")
else:
    default_text = """<div>
    <p>Enter your text here...</p>
    <p>Try adding HTML, excessive    spaces, or PII like test@example.com</p>
</div>"""

# Input/Output columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔴 Dirty Input")
    raw_text = st.text_area(
        "Input Text:",
        value=default_text,
        height=200,
        help="Paste your messy prompt here",
        label_visibility="collapsed",
    )
    raw_tokens = count_tokens(raw_text)
    st.caption(f"📝 Token Count: {raw_tokens:,}")

# Process the text (before displaying in columns)
result = None
cleaned_tokens = 0
processing_time = 0
processing_error = None

if raw_text.strip():
    start_time = time.time()
    try:
        result = raw_text

        # Apply operations in sequence
        if use_html:
            result = StripHTML().process(result)

        if use_whitespace:
            result = NormalizeWhitespace().process(result)

        if use_unicode:
            result = FixUnicode().process(result)

        if use_deduplicate:
            result = Deduplicate(
                similarity_threshold=dedup_threshold,
                method=dedup_method,
                granularity=dedup_granularity,
            ).process(result)

        if use_truncate:
            result = TruncateTokens(
                max_tokens=max_tokens,
                strategy=truncate_strategy,
                respect_sentence_boundary=respect_boundary,
            ).process(result)

        if use_pii:
            result = RedactPII(redact_types=set(pii_types)).process(result)

        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        cleaned_tokens = count_tokens(result)

    except Exception as e:
        processing_error = str(e)
        result = None

# Display output in col2
with col2:
    st.subheader("🟢 Cleaned Output")

    if result is not None:
        st.text_area("Result:", value=result, height=200, label_visibility="collapsed")
        st.caption(f"📝 Token Count: {cleaned_tokens:,}")
    elif processing_error:
        st.error(f"⚠️ Error processing text: {processing_error}")
        st.info(
            "Make sure you have the latest version: `pip install --upgrade prompt-refiner`"
        )
    elif not raw_text.strip():
        st.info("👈 Enter text in the left panel to see the magic happen!")
    else:
        st.info("Processing...")

# Metrics Dashboard (moved outside columns, always visible when processing succeeds)
if result is not None and raw_text.strip():
    st.divider()
    st.subheader("📊 Metrics Dashboard")

    # Calculate savings
    savings = calculate_cost_savings(raw_tokens, cleaned_tokens)

    # Metrics in 3 columns
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Original Tokens", f"{raw_tokens:,}")
    with m2:
        st.metric(
            "Final Tokens",
            f"{cleaned_tokens:,}",
            delta=f"-{savings['saved_tokens']:,}",
            delta_color="normal",
        )
    with m3:
        st.metric(
            "Reduction",
            f"{savings['saved_percentage']:.1f}%",
            help="Percentage of tokens saved",
        )

    # Savings message
    if savings["saved_percentage"] > 0:
        st.success(
            f"🚀 **You saved {savings['saved_percentage']:.1f}% tokens!** "
            f"That's \${savings['cost_per_1k']:.3f} per 1,000 calls or "
            f"\${savings['monthly_savings']:.2f}/month at 1M calls/month (GPT-4 pricing)."
        )
    else:
        st.info(
            "💡 No tokens saved. Try enabling more operations or choose a different example."
        )

    # Processing time and download button in columns
    action_col1, action_col2 = st.columns([1, 3])
    with action_col1:
        st.caption(f"⚡ Processing time: {processing_time:.1f}ms")
    with action_col2:
        st.download_button(
            label="📥 Download Cleaned Text",
            data=result,
            file_name="cleaned_prompt.txt",
            mime="text/plain",
        )

# --- Bottom Section ---
st.divider()

st.markdown(
    """
### 🎯 How to Use

1. **Choose a preset example** or enter your own text in the left panel
2. **Configure operations** in the sidebar - try different strategies!
3. **Click between presets** to see how different settings affect different text types
4. **See real-time savings** and download the cleaned result

### 📦 Installation

```bash
pip install llm-prompt-refiner
```

### 💻 Example Code

```python
from prompt_refiner import (
    StripHTML,
    NormalizeWhitespace,
    TruncateTokens
)

# Use pipe operator to chain operations
pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | TruncateTokens(max_tokens=1000)
)

cleaned = pipeline.run(dirty_text)
```

### 🔗 Links

- 📖 [Documentation](https://jacobhuang91.github.io/prompt-refiner/)
- 💻 [GitHub Repository](https://github.com/JacobHuang91/prompt-refiner)
- 📦 [PyPI Package](https://pypi.org/project/llm-prompt-refiner/)

---

Made with ❤️ by [Xinghao Huang](https://github.com/JacobHuang91) | Easy to install: `pip install llm-prompt-refiner`
"""
)
