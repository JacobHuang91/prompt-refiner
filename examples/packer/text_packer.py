"""
TextPacker Demo - Text Completion APIs (v0.1.3+)

Demonstrates TextPacker for text completion APIs like:
- Base models (Llama-2-base, GPT-3, Mistral-base)
- Completion endpoints (not chat)

Key Features:
- Returns str ready for completion APIs
- Multiple text formats: RAW, MARKDOWN, XML
- Priority-based greedy selection
- JIT refinement with operations
- Conversation history management
- Automatic delimiter overhead accounting
"""

import logging

from prompt_refiner import (
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    StripHTML,
    TextFormat,
    TextPacker,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    """Complete RAG + conversation history example with TextPacker."""
    logger.info("\n" + "=" * 80)
    logger.info("TextPacker - RAG + Conversation History Example")
    logger.info("=" * 80)

    # Initialize packer for base model with MARKDOWN format
    # max_tokens is optional - omit it to include all items without limit
    packer = TextPacker(
        max_tokens=300,  # Or omit for unlimited: TextPacker(text_format=TextFormat.MARKDOWN)
        text_format=TextFormat.MARKDOWN,  # Use RAW, MARKDOWN, or XML
        separator="\n\n",  # Smart default for clarity
    )

    # 1. System prompt (auto priority=0 for role="system")
    packer.add(
        "You are a QA assistant. Answer questions based on the provided context.",
        role="system",  # Auto: PRIORITY_SYSTEM (0)
    )

    # 2. RAG documents with JIT HTML cleaning (auto priority=20 for no role)
    doc_html = """
    <div class="doc">
        <h2>TextPacker</h2>
        <p>TextPacker is optimized for text completion APIs. It supports multiple
        formatting strategies to prevent instruction drifting in base models.</p>
    </div>
    """
    packer.add(
        doc_html,
        # No role = RAG document, auto: PRIORITY_HIGH (20)
        refine_with=StripHTML(),  # Clean HTML before packing
    )

    packer.add(
        "The library includes 5 modules: Cleaner, Compressor, Scrubber, Analyzer, and Packer.",
        # No role = RAG document, auto: PRIORITY_HIGH (20)
    )

    # 3. Conversation history (auto priority=40 for history)
    conversation_history = [
        {"role": "user", "content": "What is prompt-refiner?"},
        {"role": "assistant", "content": "It's a Python library for optimizing LLM inputs."},
        {"role": "user", "content": "Does it reduce costs?"},
        {"role": "assistant", "content": "Yes, by removing unnecessary tokens it can save 10-20% on API costs."},
    ]
    packer.add_messages(conversation_history)  # Auto: PRIORITY_LOW (40) for history

    # 4. Recent context (user role = auto priority=10)
    packer.add(
        "I'm working with Llama-2-base and need efficient context management.",
        role="user",  # Auto: PRIORITY_USER (10)
    )

    # 5. Current query (user role = auto priority=10)
    packer.add(
        "What is TextPacker and how does it work?",
        role="user",  # Auto: PRIORITY_USER (10)
    )

    # Pack into text format
    prompt = packer.pack()

    # Display results
    logger.info(f"\nToken Budget: {packer.raw_max_tokens} tokens")
    logger.info(f"Effective Budget: {packer.effective_max_tokens} tokens")

    logger.info("\n" + "-" * 80)
    logger.info("PACKED OUTPUT (Ready for Completion API):")
    logger.info("-" * 80)
    logger.info(prompt)

    logger.info("\n" + "=" * 80)
    logger.info("KEY FEATURES DEMONSTRATED:")
    logger.info("  ✓ MARKDOWN format with clear section boundaries")
    logger.info("  ✓ Priority-based selection (SYSTEM > USER > HIGH > MEDIUM > LOW)")
    logger.info("  ✓ RAG document integration with JIT HTML cleaning")
    logger.info("  ✓ Conversation history management")
    logger.info("  ✓ Direct str output - ready for completion APIs")
    logger.info("  ✓ Automatic delimiter overhead accounting")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
