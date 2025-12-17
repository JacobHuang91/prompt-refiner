"""
Packer Benchmark - Validates MessagesPacker and TextPacker functionality.

Tests:
1. Token tracking accuracy (compare tracked savings vs actual tiktoken counts)
2. Priority ordering correctness
3. Default refining strategies (automatic for system/query/context/history)
4. Real-world RAG scenarios
5. Edge cases

Usage:
    python benchmark.py
"""

import argparse
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import tiktoken

from prompt_refiner import MessagesPacker, MinimalStrategy, StandardStrategy, TextFormat, TextPacker


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens using tiktoken."""
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))


def count_message_tokens(messages: List[Dict[str, str]], model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in a list of messages, accounting for ChatML overhead.

    Based on OpenAI's token counting for chat completions:
    - Every message follows <|im_start|>{role}\n{content}<|im_end|>\n
    - Roughly 4 tokens per message overhead
    """
    encoder = tiktoken.encoding_for_model(model)
    total_tokens = 0

    for message in messages:
        # 4 tokens per message overhead (<|im_start|>, role, newline, <|im_end|>)
        total_tokens += 4
        total_tokens += len(encoder.encode(message.get("role", "")))
        total_tokens += len(encoder.encode(message.get("content", "")))

    # Add 2 tokens for priming (<|im_start|>assistant)
    total_tokens += 2

    return total_tokens


class PackerBenchmark:
    """Benchmark suite for MessagesPacker and TextPacker."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.results = []
        # Create tiktoken-based token counter for packer
        encoder = tiktoken.encoding_for_model(model)
        self.token_counter = lambda text: len(encoder.encode(text))

    def test_token_tracking_accuracy(self) -> Dict[str, Any]:
        """
        Test that token tracking is reasonably accurate.

        Note: Packer tracks content tokens only, not ChatML overhead (4 tokens/message).
        For MessagesPacker, expect ~20-30% difference due to this overhead.
        """
        print("\n" + "=" * 60)
        print("TEST 1: Token Tracking Accuracy")
        print("=" * 60)
        print("Note: Packer tracks content tokens only (excludes ChatML overhead)")

        # Scenario with HTML and whitespace that should be cleaned
        system_prompt = "You are a helpful assistant."
        context_docs = [
            "<div>The  quick   brown fox</div>",
            "<p>jumps over    the lazy dog</p>",
            "Some additional   context with    spaces"
        ]
        query = "What does the fox do?"

        # Create packer with tracking enabled
        packer = MessagesPacker(
            system=system_prompt,
            context=context_docs,
            query=query,
            track_tokens=True,
            token_counter=self.token_counter
        )

        # Get packed messages and savings
        messages = packer.pack()
        savings = packer.token_stats

        # Manually count tokens with refinement
        refined_system = MinimalStrategy().run(system_prompt)
        refined_context = [StandardStrategy().run(doc) for doc in context_docs]
        refined_query = MinimalStrategy().run(query)

        # Count raw tokens
        raw_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{' '.join(context_docs)}\n\nQuestion: {query}"}
        ]
        raw_tokens_actual = count_message_tokens(raw_messages, self.model)

        # Count refined tokens
        refined_messages = [
            {"role": "system", "content": refined_system},
            {"role": "user", "content": f"Context:\n{' '.join(refined_context)}\n\nQuestion: {refined_query}"}
        ]
        refined_tokens_actual = count_message_tokens(refined_messages, self.model)

        # Compare tracked vs actual
        tracked_raw = savings["raw_tokens"]
        tracked_refined = savings["refined_tokens"]
        tracked_saved = savings["saved_tokens"]

        actual_saved = raw_tokens_actual - refined_tokens_actual

        # Calculate accuracy
        raw_accuracy = abs(tracked_raw - raw_tokens_actual) / raw_tokens_actual * 100
        refined_accuracy = abs(tracked_refined - refined_tokens_actual) / refined_tokens_actual * 100
        saved_accuracy = abs(tracked_saved - actual_saved) / max(actual_saved, 1) * 100

        print("\n📊 Token Counts:")
        print(f"  Raw tokens:      tracked={tracked_raw:4d} | actual={raw_tokens_actual:4d} | diff={abs(tracked_raw - raw_tokens_actual):3d} ({raw_accuracy:.1f}%)")
        print(f"  Refined tokens:  tracked={tracked_refined:4d} | actual={refined_tokens_actual:4d} | diff={abs(tracked_refined - refined_tokens_actual):3d} ({refined_accuracy:.1f}%)")
        print(f"  Saved tokens:    tracked={tracked_saved:4d} | actual={actual_saved:4d} | diff={abs(tracked_saved - actual_saved):3d} ({saved_accuracy:.1f}%)")
        print(f"  Savings percent: {savings['saving_percent']}")

        # Accuracy threshold: within 40% is acceptable (due to ChatML overhead)
        # MessagesPacker tracks content tokens only, not message formatting overhead
        passed = raw_accuracy < 40.0 and refined_accuracy < 40.0 and saved_accuracy < 40.0
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status} - Token tracking accuracy within acceptable range")

        return {
            "test": "token_tracking_accuracy",
            "tracked_raw": tracked_raw,
            "actual_raw": raw_tokens_actual,
            "raw_accuracy_pct": round(raw_accuracy, 2),
            "tracked_refined": tracked_refined,
            "actual_refined": refined_tokens_actual,
            "refined_accuracy_pct": round(refined_accuracy, 2),
            "tracked_saved": tracked_saved,
            "actual_saved": actual_saved,
            "saved_accuracy_pct": round(saved_accuracy, 2),
            "passed": passed
        }

    def test_priority_ordering(self) -> Dict[str, Any]:
        """Test that items are ordered correctly by priority."""
        print("\n" + "=" * 60)
        print("TEST 2: Priority Ordering")
        print("=" * 60)

        # Create items with explicit priorities (should override role defaults)

        packer = MessagesPacker(
            system="System prompt",  # Should be first (PRIORITY_SYSTEM = 1000)
            query="User query",      # Should be second (PRIORITY_QUERY = 900)
            context=["Context 1", "Context 2"],  # Should be third (PRIORITY_HIGH = 500)
            history=[
                {"role": "user", "content": "Previous question"},
                {"role": "assistant", "content": "Previous answer"}
            ]  # Should be last (PRIORITY_LOW = 100)
        )

        messages = packer.pack()

        # Check key ordering principles:
        # 1. System message should be first
        # 2. Query should be in last user message
        # 3. History should be before query
        print(f"\n📊 Message Order ({len(messages)} messages):")

        system_first = messages[0]["role"] == "system" and "System prompt" in messages[0]["content"]
        query_in_last = "User query" in messages[-1]["content"]
        has_history = any("Previous question" in m.get("content", "") for m in messages)

        for i, msg in enumerate(messages):
            content_preview = msg["content"][:40] if len(msg["content"]) > 40 else msg["content"]
            print(f"  {i+1}. {msg['role']:10s} | {content_preview}...")

        print("\n  Key checks:")
        print(f"    System first: {system_first} {'✓' if system_first else '✗'}")
        print(f"    Query in last message: {query_in_last} {'✓' if query_in_last else '✗'}")
        print(f"    Has history: {has_history} {'✓' if has_history else '✗'}")

        order_correct = system_first and query_in_last and has_history

        status = "✓ PASS" if order_correct else "✗ FAIL"
        print(f"\n{status} - Priority ordering correct")

        return {
            "test": "priority_ordering",
            "passed": order_correct,
            "num_messages": len(messages)
        }

    def test_default_refining_strategies(self) -> Dict[str, Any]:
        """Test that default refining strategies are applied correctly."""
        print("\n" + "=" * 60)
        print("TEST 3: Default Refining Strategies")
        print("=" * 60)

        # Create inputs with HTML and whitespace that should be cleaned
        system_dirty = "<div>System   prompt with    HTML</div>"
        query_dirty = "<p>Query   with    whitespace</p>"
        context_dirty = [
            "<div>Context 1   with HTML</div>",
            "<div>Context 1   with HTML</div>",  # Duplicate
            "<p>Context 2</p>"
        ]

        # Pack without explicit refiners (should use defaults)
        packer = MessagesPacker(
            system=system_dirty,
            query=query_dirty,
            context=context_dirty,
            track_tokens=True,
            token_counter=self.token_counter
        )

        messages = packer.pack()

        # Check that cleaning was applied
        system_msg = next((m for m in messages if m["role"] == "system"), None)
        user_msgs = [m for m in messages if m["role"] == "user"]

        # System should have HTML removed and whitespace normalized (MinimalStrategy)
        system_has_html = "<div>" in system_msg["content"] or "<p>" in system_msg["content"]
        system_has_extra_spaces = "   " in system_msg["content"] or "    " in system_msg["content"]

        # Context should have HTML removed, whitespace normalized, and deduplication (StandardStrategy)
        context_msg = next((m for m in user_msgs if "Context" in m["content"]), None)
        context_has_html = "<div>" in context_msg["content"] or "<p>" in context_msg["content"]
        context_has_extra_spaces = "   " in context_msg["content"]

        # Count occurrences of "Context 1" (should be deduplicated to 1)
        context_1_count = context_msg["content"].count("Context 1 with HTML")

        print("\n📊 Default Refining Results:")
        print("  System prompt:")
        print(f"    HTML removed: {not system_has_html} {'✓' if not system_has_html else '✗'}")
        print(f"    Whitespace normalized: {not system_has_extra_spaces} {'✓' if not system_has_extra_spaces else '✗'}")
        print("\n  Context:")
        print(f"    HTML removed: {not context_has_html} {'✓' if not context_has_html else '✗'}")
        print(f"    Whitespace normalized: {not context_has_extra_spaces} {'✓' if not context_has_extra_spaces else '✗'}")
        print(f"    Deduplicated: {context_1_count == 1} {'✓' if context_1_count == 1 else '✗'} (count: {context_1_count})")

        all_checks_passed = (
            not system_has_html and
            not system_has_extra_spaces and
            not context_has_html and
            not context_has_extra_spaces and
            context_1_count == 1
        )

        status = "✓ PASS" if all_checks_passed else "✗ FAIL"
        print(f"\n{status} - Default refining strategies applied correctly")

        return {
            "test": "default_refining_strategies",
            "system_html_removed": not system_has_html,
            "system_whitespace_normalized": not system_has_extra_spaces,
            "context_html_removed": not context_has_html,
            "context_whitespace_normalized": not context_has_extra_spaces,
            "context_deduplicated": context_1_count == 1,
            "passed": all_checks_passed
        }

    def test_text_packer_markdown_format(self) -> Dict[str, Any]:
        """Test TextPacker with MARKDOWN format for base models."""
        print("\n" + "=" * 60)
        print("TEST 4: TextPacker MARKDOWN Format")
        print("=" * 60)

        # Create TextPacker with MARKDOWN format
        packer = TextPacker(
            system="You are a helpful assistant.",
            context=["Document 1 about Python.", "Document 2 about JavaScript."],
            query="What languages are discussed?",
            text_format=TextFormat.MARKDOWN,
            track_tokens=True,
            token_counter=self.token_counter
        )

        text = packer.pack()

        # Check that MARKDOWN sections are present
        has_instructions = "## INSTRUCTIONS" in text
        has_context = "## CONTEXT" in text
        has_input = "## INPUT" in text

        # Check that content is in the right sections
        instructions_before_context = text.index("## INSTRUCTIONS") < text.index("## CONTEXT")
        context_before_input = text.index("## CONTEXT") < text.index("## INPUT")

        print("\n📊 MARKDOWN Format Results:")
        print(f"  Has INSTRUCTIONS section: {has_instructions} {'✓' if has_instructions else '✗'}")
        print(f"  Has CONTEXT section: {has_context} {'✓' if has_context else '✗'}")
        print(f"  Has INPUT section: {has_input} {'✓' if has_input else '✗'}")
        print(f"  Sections in correct order: {instructions_before_context and context_before_input} {'✓' if (instructions_before_context and context_before_input) else '✗'}")

        # Check token savings
        savings = packer.token_stats
        print(f"\n  Token savings: {savings['saving_percent']}")

        all_checks_passed = (
            has_instructions and
            has_context and
            has_input and
            instructions_before_context and
            context_before_input
        )

        status = "✓ PASS" if all_checks_passed else "✗ FAIL"
        print(f"\n{status} - TextPacker MARKDOWN format correct")

        return {
            "test": "text_packer_markdown",
            "has_instructions": has_instructions,
            "has_context": has_context,
            "has_input": has_input,
            "correct_order": instructions_before_context and context_before_input,
            "token_savings_pct": savings['saving_percent'],
            "passed": all_checks_passed
        }

    def test_real_world_rag_scenario(self) -> Dict[str, Any]:
        """Test realistic RAG scenario with messy HTML context."""
        print("\n" + "=" * 60)
        print("TEST 5: Real-World RAG Scenario")
        print("=" * 60)

        # Realistic RAG scenario with messy HTML from web scraping
        system_prompt = "You are a helpful customer support assistant. Answer questions based on the provided documentation."

        context_docs = [
            """<div class="content">
                <h1>Product   Documentation</h1>
                <p>Our product   supports multiple    authentication methods:</p>
                <ul>
                    <li>OAuth 2.0</li>
                    <li>API    Keys</li>
                    <li>JWT   Tokens</li>
                </ul>
            </div>""",
            """<div class="content">
                <h1>Product   Documentation</h1>
                <p>Our product   supports multiple    authentication methods:</p>
                <ul>
                    <li>OAuth 2.0</li>
                    <li>API    Keys</li>
                    <li>JWT   Tokens</li>
                </ul>
            </div>""",  # Duplicate content
            """<div class="footer">
                <p>© 2024 Company Name. All rights   reserved.</p>
                <a href="/privacy">Privacy Policy</a>
            </div>"""
        ]

        conversation_history = [
            {"role": "user", "content": "How do I authenticate?"},
            {"role": "assistant", "content": "You can use OAuth 2.0, API Keys, or JWT Tokens."}
        ]

        query = "Can you explain OAuth 2.0?"

        # Pack with tracking
        packer = MessagesPacker(
            system=system_prompt,
            context=context_docs,
            history=conversation_history,
            query=query,
            track_tokens=True,
            token_counter=self.token_counter
        )

        messages = packer.pack()
        savings = packer.token_stats

        # Verify structure
        has_system = any(m["role"] == "system" for m in messages)
        has_context = any("Product Documentation" in m["content"] for m in messages)
        has_history = any("How do I authenticate?" in m["content"] for m in messages)
        has_query = any("explain OAuth 2.0" in m["content"] for m in messages)

        # Check that HTML and duplicates were cleaned
        context_msg = next((m for m in messages if "Product Documentation" in m["content"]), {})
        context_clean = not ("<div>" in context_msg.get("content", "") or "<h1>" in context_msg.get("content", ""))
        duplicate_count = context_msg.get("content", "").count("Product Documentation")
        duplicates_removed = duplicate_count == 1

        print("\n📊 RAG Scenario Results:")
        print(f"  Has system prompt: {has_system} {'✓' if has_system else '✗'}")
        print(f"  Has context: {has_context} {'✓' if has_context else '✗'}")
        print(f"  Has conversation history: {has_history} {'✓' if has_history else '✗'}")
        print(f"  Has user query: {has_query} {'✓' if has_query else '✗'}")
        print(f"  HTML cleaned: {context_clean} {'✓' if context_clean else '✗'}")
        print(f"  Duplicates removed: {duplicates_removed} {'✓' if duplicates_removed else '✗'}")
        print("\n  Token savings:")
        print(f"    Raw: {savings['raw_tokens']} tokens")
        print(f"    Refined: {savings['refined_tokens']} tokens")
        print(f"    Saved: {savings['saved_tokens']} tokens ({savings['saving_percent']})")

        all_checks_passed = (
            has_system and
            has_context and
            has_history and
            has_query and
            context_clean and
            duplicates_removed
        )

        status = "✓ PASS" if all_checks_passed else "✗ FAIL"
        print(f"\n{status} - Real-world RAG scenario handled correctly")

        return {
            "test": "real_world_rag",
            "has_all_components": has_system and has_context and has_history and has_query,
            "html_cleaned": context_clean,
            "duplicates_removed": duplicates_removed,
            "raw_tokens": savings['raw_tokens'],
            "refined_tokens": savings['refined_tokens'],
            "saved_tokens": savings['saved_tokens'],
            "savings_pct": savings['saving_percent'],
            "passed": all_checks_passed
        }

    def run_all_tests(self):
        """Run all benchmark tests."""
        print("\n" + "=" * 60)
        print("PACKER BENCHMARK SUITE")
        print("=" * 60)
        print("Testing MessagesPacker and TextPacker functionality\n")

        # Run tests
        self.results.append(self.test_token_tracking_accuracy())
        self.results.append(self.test_priority_ordering())
        self.results.append(self.test_default_refining_strategies())
        self.results.append(self.test_text_packer_markdown_format())
        self.results.append(self.test_real_world_rag_scenario())

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        passed_count = sum(1 for r in self.results if r.get("passed", False))
        total_count = len(self.results)

        print(f"\nTests passed: {passed_count}/{total_count}")
        print()

        for result in self.results:
            status = "✓ PASS" if result.get("passed", False) else "✗ FAIL"
            test_name = result.get("test", "unknown").replace("_", " ").title()
            print(f"  {status} - {test_name}")

        all_passed = passed_count == total_count

        if all_passed:
            print("\n✓ All tests passed!")
        else:
            print(f"\n✗ {total_count - passed_count} test(s) failed")

        print("\n" + "=" * 60)

        return all_passed

    def save_results(self, output_dir: Path):
        """Save benchmark results to CSV."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame and save
        df = pd.DataFrame(self.results)
        csv_path = output_dir / "packer_benchmark_results.csv"
        df.to_csv(csv_path, index=False)

        print(f"\n✓ Results saved to: {csv_path}")


def main():
    """Run packer benchmark."""
    parser = argparse.ArgumentParser(
        description="Benchmark MessagesPacker and TextPacker"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results",
        help="Output directory for results (default: results)"
    )
    args = parser.parse_args()

    # Run benchmark
    benchmark = PackerBenchmark()
    all_passed = benchmark.run_all_tests()

    # Save results
    output_dir = Path(__file__).parent / args.output
    benchmark.save_results(output_dir)

    # Exit with appropriate code
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
