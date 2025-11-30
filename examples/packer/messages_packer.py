"""
MessagesPacker Demo - Chat Completion APIs (v0.1.3+)

Demonstrates MessagesPacker for chat completion APIs like:
- OpenAI Chat Completions (gpt-4, gpt-3.5-turbo)
- Anthropic Messages API (claude-3-opus, claude-3-sonnet)

Key Features:
- Returns List[Dict] ready for chat APIs
- Priority-based greedy selection
- JIT refinement with operations
- Automatic ChatML overhead accounting (4 tokens per message)
- Conversation history management
"""

import json
import logging

from prompt_refiner import (
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    MessagesPacker,
    StripHTML,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    """Complete RAG + conversation history example with MessagesPacker."""
    logger.info("\n" + "=" * 80)
    logger.info("MessagesPacker - RAG + Conversation History Example")
    logger.info("=" * 80)

    # Initialize packer for chat APIs
    # max_tokens is optional - omit it to include all items without limit
    packer = MessagesPacker(max_tokens=400)  # Or MessagesPacker() for unlimited

    # 1. System prompt (auto priority=0 for role="system")
    packer.add(
        "You are a helpful AI assistant. Answer questions based on the provided "
        "documentation and conversation context.",
        role="system",  # Auto: PRIORITY_SYSTEM (0)
    )

    # 2. RAG documents with JIT HTML cleaning (auto priority=20 for no role)
    doc_html = """
    <div class="doc">
        <h2>MessagesPacker</h2>
        <p>MessagesPacker is optimized for chat completion APIs. It automatically
        accounts for ChatML format overhead (~4 tokens per message).</p>
    </div>
    """
    packer.add(
        doc_html,
        # No role = RAG document, auto: PRIORITY_HIGH (20)
        refine_with=StripHTML(),  # Clean HTML before packing
    )

    packer.add(
        "The library includes MessagesPacker for chat APIs and TextPacker for completion APIs.",
        # No role = RAG document, auto: PRIORITY_HIGH (20)
    )

    # 3. Old conversation history (auto priority=40 for history)
    old_conversation = [
        {"role": "user", "content": "What is prompt-refiner?"},
        {"role": "assistant", "content": "Prompt-refiner is a Python library for optimizing LLM inputs."},
        {"role": "user", "content": "Does it support token counting?"},
        {"role": "assistant", "content": "Yes, it has precise token counting with tiktoken."},
    ]
    packer.add_messages(old_conversation)  # Auto: PRIORITY_LOW (40) for history

    # 4. Recent context (user role = auto priority=10)
    packer.add(
        "I'm building a chatbot and need to manage context window efficiently.",
        role="user",  # Auto: PRIORITY_USER (10)
    )

    # 5. Current query (user role = auto priority=10)
    packer.add(
        "How does MessagesPacker handle conversation history?",
        role="user",  # Auto: PRIORITY_USER (10)
    )

    # Pack into messages format
    messages = packer.pack()

    # Display results
    logger.info(f"\nToken Budget: {packer.raw_max_tokens} tokens")
    logger.info(f"Effective Budget: {packer.effective_max_tokens} tokens")
    logger.info(f"Selected: {len(messages)} messages")
    logger.info(f"Dropped: {len(packer.get_items()) - len(messages)} items")

    logger.info("\n" + "-" * 80)
    logger.info("PACKED OUTPUT (Ready for Chat APIs):")
    logger.info("-" * 80)
    logger.info(json.dumps(messages, indent=2))

    logger.info("\n" + "=" * 80)
    logger.info("KEY FEATURES DEMONSTRATED:")
    logger.info("  ✓ Priority-based selection (SYSTEM > USER > HIGH > MEDIUM > LOW)")
    logger.info("  ✓ RAG document integration with JIT HTML cleaning")
    logger.info("  ✓ Conversation history management")
    logger.info("  ✓ Direct List[Dict] output - ready for chat APIs")
    logger.info("  ✓ Automatic ChatML overhead accounting (~4 tokens per message)")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
