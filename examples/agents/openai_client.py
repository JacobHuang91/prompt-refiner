"""
OpenAI Client + Prompt Refiner Integration

This example shows how to easily integrate prompt-refiner with the raw OpenAI client
to optimize:
1. Messages (MessagesPacker) - Clean and optimize context
2. Tool schemas (SchemaCompressor) - Reduce schema tokens
3. Tool responses (ResponseCompressor) - Compress API responses

Compare against baseline: python examples/agents/openai_client_baseline.py
Run optimized version: python examples/agents/openai_client.py
"""

import json

from dotenv import load_dotenv
from openai import OpenAI

from prompt_refiner import MessagesPacker, ResponseCompressor, SchemaCompressor, StripHTML
from shared_data import (
    CONTEXT_DOCUMENTS,
    MESSAGE_HISTORY,
    QUERY,
    SYSTEM_PROMPT,
    get_tool_schema,
    search_books,
)

load_dotenv()


def main():
    """Run the OpenAI client example with prompt-refiner integration."""
    print("OpenAI Client + Prompt Refiner (Optimized)")
    print("=" * 80)
    print()

    client = OpenAI()

    # 1. Compress tool schema
    compressed_schema = SchemaCompressor().process(get_tool_schema())

    # 2. Build optimized messages with tuple API
    messages = MessagesPacker.quick_pack(
        model="gpt-4o-mini",
        system=SYSTEM_PROMPT,
        context=(CONTEXT_DOCUMENTS, [StripHTML()]),  # Strips HTML tags
        history=MESSAGE_HISTORY,
        query=QUERY
    )

    # 3. Call LLM with optimized inputs
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[compressed_schema],
    )

    print(f"✓ Optimized prompt tokens: {response.usage.prompt_tokens}")
    print()

    # 4. Handle tool calls with response compression
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Execute and compress tool response
            tool_response = search_books(**function_args)
            compressed_response = ResponseCompressor().process(tool_response)

            print(f"✓ Optimized tool response size: {len(json.dumps(compressed_response))} chars")
            print()

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(compressed_response),
            })

        # Get final response
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        print(f"✓ Optimized final prompt tokens: {final_response.usage.prompt_tokens}")
        print()

        final_message = final_response.choices[0].message.content
    else:
        final_message = response_message.content

    print("Final Response:")
    print("-" * 80)
    print(final_message)
    print()
    print("=" * 80)
    print()
    print("To see token savings, compare with baseline:")
    print("  python examples/agents/openai_client_baseline.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
