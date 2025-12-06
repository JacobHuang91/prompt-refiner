"""Example: Schema compression with real OpenAI API calls.

This example demonstrates that compressed tool schemas work perfectly with OpenAI's
function calling while saving 40-50% tokens.

Setup:
    pip install openai python-dotenv
    cp .env.example .env  # Add your OpenAI API key
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from prompt_refiner import SchemaCompressor

# Load API key from .env
load_dotenv(Path(__file__).parent / ".env")
client = OpenAI()

# Define verbose tool schemas (typical real-world scenario)
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "title": "Flight Search Tool",
            "description": (
                "Search for available flights between two airports. "
                "Use this whenever the user asks about flights, schedules, "
                "ticket prices, or airline options. You MUST always call this "
                "tool before answering any flight-related question.\n\n"
                "Examples:\n"
                "- Find me a flight from LAX to JFK tomorrow\n"
                "- Show me business class options next Monday\n"
                "- What's the cheapest flight to London?"
            ),
            "parameters": {
                "type": "object",
                "title": "FlightSearchParameters",
                "properties": {
                    "origin": {
                        "type": "string",
                        "title": "Origin Airport",
                        "description": (
                            "Origin airport IATA code, for example `LAX` or `SFO`.\n"
                            "You should infer this from the user location when missing.\n"
                            "Do not ask again if already provided. "
                            "Must be a valid 3-letter IATA code."
                        ),
                        "examples": ["LAX", "SFO", "JFK"]
                    },
                    "destination": {
                        "type": "string",
                        "title": "Destination Airport",
                        "description": "Destination airport IATA code. Same rules as origin apply.",
                        "examples": ["JFK", "ORD", "ATL"]
                    },
                    "date": {
                        "type": "string",
                        "title": "Travel Date",
                        "description": (
                            "Travel date in YYYY-MM-DD format. ```python\n"
                            "from datetime import datetime\n"
                            "date = datetime.now().strftime('%Y-%m-%d')\n"
                            "```"
                        ),
                        "examples": ["2024-12-25", "2025-01-01"]
                    }
                },
                "required": ["origin", "destination", "date"]
            }
        }
    }
]

user_query = "Find me a flight from San Francisco to New York on December 25th"

# Test with ORIGINAL schemas
response1 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": user_query}],
    tools=tools,
    tool_choice="auto"
)
original_tokens = response1.usage.prompt_tokens
args1 = json.loads(response1.choices[0].message.tool_calls[0].function.arguments)

# Test with COMPRESSED schemas
compressor = SchemaCompressor(
    drop_examples=True,
    drop_titles=True,
    drop_markdown_formatting=True
)
compressed_tools = [compressor.process(tool) for tool in tools]

response2 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": user_query}],
    tools=compressed_tools,
    tool_choice="auto"
)
compressed_tokens = response2.usage.prompt_tokens
args2 = json.loads(response2.choices[0].message.tool_calls[0].function.arguments)

# Results
print("\n" + "=" * 60)
print("SCHEMA COMPRESSION RESULTS")
print("=" * 60)

savings_pct = (original_tokens - compressed_tokens) / original_tokens * 100

print(f"\nOriginal tokens:    {original_tokens}")
print(f"Compressed tokens:  {compressed_tokens}")
print(f"Savings:            {savings_pct:.1f}%")

print("\n" + "-" * 60)
print("FUNCTION ARGUMENTS")
print("-" * 60)

print("\nOriginal:")
print(json.dumps(args1, indent=2))

print("\nCompressed:")
print(json.dumps(args2, indent=2))

# Match status
print("\n" + "-" * 60)
if args1 == args2:
    print("✅ Results match perfectly!")
else:
    print("❌ Results differ!")
print("=" * 60)
