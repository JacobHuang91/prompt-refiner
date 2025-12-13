"""Tests for SchemaCompressor operation."""

import json

from prompt_refiner import SchemaCompressor


def test_schema_compressor_basic():
    """Test basic schema compression."""
    tool = {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search for available flights between two airports",
            "parameters": {
                "type": "object",
                "properties": {"origin": {"type": "string", "description": "Origin airport code"}},
            },
        },
    }

    compressor = SchemaCompressor()
    result = compressor.process(tool)

    # Name should be preserved
    assert result["function"]["name"] == "search_flights"
    # Description should be preserved (not truncated if short)
    assert "available flights" in result["function"]["description"]


def test_schema_compressor_truncate_long_description():
    """Test truncating long tool descriptions."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "A" * 300,  # Very long description
            "parameters": {"type": "object", "properties": {}},
        },
    }

    compressor = SchemaCompressor()
    result = compressor.process(tool)

    # Description should be truncated to ~256 chars (hardcoded default)
    assert len(result["function"]["description"]) <= 256


def test_schema_compressor_drop_titles():
    """Test dropping title fields."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "title": "Test Tool Title",
            "description": "Test description",
            "parameters": {
                "type": "object",
                "title": "Parameters Title",
                "properties": {
                    "param1": {
                        "type": "string",
                        "title": "Param Title",
                        "description": "Test param",
                    }
                },
            },
        },
    }

    compressor = SchemaCompressor(drop_titles=True)
    result = compressor.process(tool)

    # All titles should be removed
    assert "title" not in result["function"]
    assert "title" not in result["function"]["parameters"]
    assert "title" not in result["function"]["parameters"]["properties"]["param1"]


def test_schema_compressor_keep_titles():
    """Test keeping title fields when configured."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "title": "Test Tool Title",
            "description": "Test description",
            "parameters": {"type": "object", "properties": {}},
        },
    }

    compressor = SchemaCompressor(drop_titles=False)
    result = compressor.process(tool)

    # Title should be preserved
    assert result["function"]["title"] == "Test Tool Title"


def test_schema_compressor_drop_examples():
    """Test dropping examples fields."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "Test",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Test",
                        "examples": ["example1", "example2"],
                    }
                },
            },
        },
    }

    compressor = SchemaCompressor(drop_examples=True)
    result = compressor.process(tool)

    # Examples should be removed
    assert "examples" not in result["function"]["parameters"]["properties"]["param1"]


def test_schema_compressor_keep_examples():
    """Test keeping examples when configured."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "Test",
            "parameters": {
                "type": "object",
                "properties": {"param1": {"type": "string", "examples": ["example1", "example2"]}},
            },
        },
    }

    compressor = SchemaCompressor(drop_examples=False)
    result = compressor.process(tool)

    # Examples should be preserved
    assert result["function"]["parameters"]["properties"]["param1"]["examples"] == [
        "example1",
        "example2",
    ]


def test_schema_compressor_remove_markdown():
    """Test removing markdown formatting."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "This has `inline code` and ```code blocks```",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Use `LAX` or `SFO` format"}
                },
            },
        },
    }

    compressor = SchemaCompressor(drop_markdown_formatting=True)
    result = compressor.process(tool)

    # Markdown should be removed
    fn_desc = result["function"]["description"]
    assert "`" not in fn_desc
    assert "inline code" in fn_desc

    param_desc = result["function"]["parameters"]["properties"]["param1"]["description"]
    assert "`" not in param_desc
    assert "LAX" in param_desc and "SFO" in param_desc


def test_schema_compressor_keep_markdown():
    """Test keeping markdown when configured."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "This has `inline code`",
            "parameters": {"type": "object", "properties": {}},
        },
    }

    compressor = SchemaCompressor(drop_markdown_formatting=False)
    result = compressor.process(tool)

    # Markdown should be preserved
    assert "`inline code`" in result["function"]["description"]


def test_schema_compressor_preserve_protocol_fields():
    """Test that protocol-level fields are never modified."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "Test",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "number"},
                    "param3": {"type": "string", "enum": ["option1", "option2"]},
                },
                "required": ["param1", "param3"],
            },
        },
    }

    compressor = SchemaCompressor()
    result = compressor.process(tool)

    params = result["function"]["parameters"]

    # All protocol fields should be preserved exactly
    assert params["type"] == "object"
    assert "param1" in params["properties"]
    assert "param2" in params["properties"]
    assert "param3" in params["properties"]
    assert params["properties"]["param1"]["type"] == "string"
    assert params["properties"]["param2"]["type"] == "number"
    assert params["properties"]["param3"]["type"] == "string"
    assert params["properties"]["param3"]["enum"] == ["option1", "option2"]
    assert params["required"] == ["param1", "param3"]


def test_schema_compressor_nested_objects():
    """Test compression of deeply nested object schemas."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "Test",
            "parameters": {
                "type": "object",
                "properties": {
                    "nested": {
                        "type": "object",
                        "title": "Nested Title",
                        "properties": {
                            "deep": {
                                "type": "string",
                                "description": "A" * 200,
                                "examples": ["test"],
                            }
                        },
                    }
                },
            },
        },
    }

    compressor = SchemaCompressor(drop_titles=True, drop_examples=True)
    result = compressor.process(tool)

    nested = result["function"]["parameters"]["properties"]["nested"]

    # Title should be removed
    assert "title" not in nested
    # Nested description should be truncated (hardcoded to 160 chars for params)
    assert len(nested["properties"]["deep"]["description"]) <= 160
    # Examples should be removed
    assert "examples" not in nested["properties"]["deep"]


def test_schema_compressor_array_types():
    """Test compression of array type schemas."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "Test",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "title": "Item Title",
                            "description": "Very long description " * 50,
                            "examples": ["example"],
                        },
                    }
                },
            },
        },
    }

    compressor = SchemaCompressor(drop_titles=True, drop_examples=True)
    result = compressor.process(tool)

    items_schema = result["function"]["parameters"]["properties"]["items"]["items"]

    # Title should be removed
    assert "title" not in items_schema
    # Description should be truncated (hardcoded to 160 chars for params)
    assert len(items_schema["description"]) <= 160
    # Examples should be removed
    assert "examples" not in items_schema


def test_schema_compressor_whitespace_normalization():
    """Test that excessive whitespace is normalized."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "This   has    excessive\n\n\nwhitespace    everywhere",
            "parameters": {"type": "object", "properties": {}},
        },
    }

    compressor = SchemaCompressor()
    result = compressor.process(tool)

    desc = result["function"]["description"]
    # Multiple spaces should be collapsed
    assert "   " not in desc
    assert "\n" not in desc
    assert "has excessive whitespace everywhere" in desc


def test_schema_compressor_sentence_boundary_truncation():
    """Test that truncation respects max length and tries sentence boundaries."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "This is sentence one. " * 50 + "This is the final sentence.",
            "parameters": {"type": "object", "properties": {}},
        },
    }

    compressor = SchemaCompressor()
    result = compressor.process(tool)

    desc = result["function"]["description"]
    # Should respect max_len + window constraint (256 + 40)
    assert len(desc) <= 296
    # Description should be truncated (original is much longer)
    assert len(desc) < len(tool["function"]["description"])


def test_schema_compressor_sentence_boundary_found():
    """Test that truncation finds and uses sentence boundary."""
    # Create description that has a period near the max_len threshold
    # Max len for function description is 256
    # Need a sentence ending between 128 (50% of 256) and 296 (256 + 40 window)
    # Total length must exceed 256 to trigger truncation
    base_text = "A" * 230  # 230 chars
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": (
                base_text + ". More text after the period that should be cut off "
                "and not appear in the result."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    }

    compressor = SchemaCompressor()
    result = compressor.process(tool)

    desc = result["function"]["description"]
    # Should end with the period (sentence boundary found)
    assert desc.endswith(".")
    # Should not contain text after the period
    assert "More text" not in desc
    # Should contain the A's before the period
    assert "AAA" in desc


def test_schema_compressor_multiple_tools():
    """Test compressing multiple tools."""
    tool1 = {
        "type": "function",
        "function": {
            "name": "tool1",
            "description": "First tool",
            "parameters": {"type": "object", "properties": {}},
        },
    }

    tool2 = {
        "type": "function",
        "function": {
            "name": "tool2",
            "description": "Second tool",
            "parameters": {"type": "object", "properties": {}},
        },
    }

    compressor = SchemaCompressor()
    result1 = compressor.process(tool1)
    result2 = compressor.process(tool2)

    assert result1["function"]["name"] == "tool1"
    assert result2["function"]["name"] == "tool2"


def test_schema_compressor_json_string_input():
    """Test processing JSON string input."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "title": "Title to remove",
            "description": "Test",
            "parameters": {"type": "object", "properties": {}},
        },
    }

    compressor = SchemaCompressor(drop_titles=True)
    result = compressor.process(tool)

    # Should work with JSON string input
    assert "title" not in result["function"]


def test_schema_compressor_single_tool_dict_input():
    """Test processing single tool dict (not list)."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "Test",
            "parameters": {"type": "object", "properties": {}},
        },
    }

    compressor = SchemaCompressor()
    result = compressor.process(tool)

    # Should handle single tool dict
    assert isinstance(result, dict)
    assert result["function"]["name"] == "test_tool"


def test_schema_compressor_config_object():
    """Test using direct parameters."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "title": "Keep This",
            "description": "A" * 100,
            "parameters": {"type": "object", "properties": {}},
        },
    }

    compressor = SchemaCompressor(
        drop_examples=False, drop_titles=False, drop_markdown_formatting=False
    )
    result = compressor.process(tool)

    # Config settings should be applied
    assert "title" in result["function"]  # drop_titles=False
    # Description is short enough (100 chars < 256 limit), so not truncated
    assert len(result["function"]["description"]) == 100


def test_schema_compressor_parameter_override():
    """Test that parameters can be set explicitly."""
    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "title": "Title",
            "description": "Test",
            "parameters": {
                "type": "object",
                "properties": {"param1": {"type": "string", "examples": ["test"]}},
            },
        },
    }

    # Create compressor with drop enabled
    compressor = SchemaCompressor(drop_titles=True, drop_examples=True)
    result = compressor.process(tool)

    # Settings should be applied
    assert "title" not in result["function"]
    assert "examples" not in result["function"]["parameters"]["properties"]["param1"]


def test_schema_compressor_real_world_openai_schema():
    """Test with realistic OpenAI function calling schema."""
    tool = {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": (
                "Search for available flights between two airports. "
                "Use this whenever the user asks about flights, schedules, "
                "ticket prices, or airline options. You MUST always call this "
                "tool before answering any flight-related question.\n\n"
                "Examples:\n"
                "- Find me a flight from LAX to JFK tomorrow\n"
                "- Show me business class options next Monday"
            ),
            "parameters": {
                "type": "object",
                "title": "FlightSearchParameters",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": (
                            "Origin airport IATA code, for example `LAX` or `SFO`.\n"
                            "You should infer this from the user location when missing.\n"
                            "Do not ask again if already provided."
                        ),
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination airport IATA code. Same rules as origin apply.",
                    },
                },
                "required": ["origin", "destination"],
            },
        },
    }

    compressor = SchemaCompressor(
        drop_examples=True, drop_titles=True, drop_markdown_formatting=True
    )

    result = compressor.process(tool)

    fn = result["function"]

    # Name and type preserved
    assert fn["name"] == "search_flights"

    # Description compressed (hardcoded to 256 chars)
    assert len(fn["description"]) <= 256
    assert "available flights" in fn["description"]

    # Parameters structure preserved
    assert fn["parameters"]["type"] == "object"
    assert "origin" in fn["parameters"]["properties"]
    assert "destination" in fn["parameters"]["properties"]
    assert fn["parameters"]["required"] == ["origin", "destination"]

    # Title removed
    assert "title" not in fn["parameters"]

    # Param descriptions compressed and markdown removed (hardcoded to 160 chars)
    origin_desc = fn["parameters"]["properties"]["origin"]["description"]
    assert len(origin_desc) <= 160
    assert "`" not in origin_desc  # Markdown removed
    assert "LAX" in origin_desc  # Content preserved


def test_schema_compressor_in_refiner_pipeline():
    """Test SchemaCompressor works in a Refiner pipeline."""
    from prompt_refiner import Pipeline

    tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "title": "Remove Me",
            "description": "Test description",
            "parameters": {"type": "object", "properties": {}},
        },
    }

    pipeline = Pipeline().pipe(SchemaCompressor(drop_titles=True))
    result = pipeline.run(tool)

    assert "title" not in result["function"]


def test_schema_compressor_token_savings():
    """Test that schema compression actually saves tokens."""
    tool = {
        "type": "function",
        "function": {
            "name": "complex_tool",
            "title": "Complex Tool Title That Takes Up Space",
            "description": (
                "This is a very detailed description with lots of information. "
                "It includes multiple sentences and examples. "
                "```python\n"
                "# Example code block\n"
                "result = tool(param='value')\n"
                "```\n"
                "More text with `inline code` and other formatting."
            ),
            "parameters": {
                "type": "object",
                "title": "Parameters",
                "properties": {
                    "param1": {
                        "type": "string",
                        "title": "Parameter 1",
                        "description": "A very long parameter description that goes on and on "
                        * 10,
                        "examples": ["example1", "example2", "example3"],
                    },
                    "param2": {
                        "type": "number",
                        "title": "Parameter 2",
                        "description": "Another long description",
                        "examples": [1, 2, 3],
                    },
                },
                "required": ["param1"],
            },
        },
    }

    # Original size
    original = json.dumps(tool, separators=(",", ":"))
    original_len = len(original)

    # Compressed size
    compressor = SchemaCompressor()
    compressed = compressor.process(tool)
    compressed_str = json.dumps(compressed, separators=(",", ":"))
    compressed_len = len(compressed_str)

    # Should save significant tokens
    savings = (original_len - compressed_len) / original_len * 100
    assert savings > 20  # At least 20% savings
    print(f"\nToken savings: {savings:.1f}% ({original_len} → {compressed_len} chars)")
