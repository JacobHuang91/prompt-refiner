"""
OpenAI Client - Baseline (No Optimization)

This example shows the SAME workflow WITHOUT prompt-refiner optimization.
Use this to compare token usage against openai_client.py to see savings.

Run: python examples/agents/openai_client_baseline.py
"""

import json

from dotenv import load_dotenv
from openai import OpenAI

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
    """Run the baseline example without prompt-refiner."""
    print("OpenAI Client - Baseline (No Optimization)")
    print("=" * 80)
    print()

    client = OpenAI()

    # Build messages manually (no MessagesPacker, no HTML stripping)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": CONTEXT_DOCUMENTS[0]},
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

    print(f"✓ Baseline prompt tokens: {response.usage.prompt_tokens}")
    print()

    # Handle tool calls (no ResponseCompressor)
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Execute tool (no compression)
            tool_response = search_books(**function_args)

            print(f"✓ Baseline tool response size: {len(json.dumps(tool_response))} chars")
            print()

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_response),  # No ResponseCompressor
            })

        # Get final response
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        print(f"✓ Baseline final prompt tokens: {final_response.usage.prompt_tokens}")
        print()

        final_message = final_response.choices[0].message.content
    else:
        final_message = response_message.content

    print("Final Response:")
    print("-" * 80)
    print(final_message)
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
