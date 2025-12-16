#!/usr/bin/env python3
"""
End-to-end tests for Tools module operations.

Tests SchemaCompressor and ResponseCompressor as a user would use them after pip install.
"""

import sys


def test_schema_compressor():
    """Test SchemaCompressor operation."""
    print("\nTesting SchemaCompressor...")
    from prompt_refiner import SchemaCompressor

    # OpenAI-style function schema
    schema = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Get the current weather for a specific location. "
                "This function retrieves real-time weather data including "
                "temperature, humidity, and conditions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": (
                            "The city and state, for example: San Francisco, CA. "
                            "You can also provide country for international locations."
                        ),
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": (
                            "The temperature unit to use. "
                            "Options are celsius or fahrenheit. Default is fahrenheit."
                        ),
                    },
                },
                "required": ["location"],
            },
        },
    }

    operation = SchemaCompressor()
    result = operation.process(schema)

    # Verify structure preserved
    assert result["type"] == "function", "Type should be preserved"
    assert result["function"]["name"] == "get_weather", "Name should be preserved"
    assert "location" in result["function"]["parameters"]["properties"], (
        "Properties should be preserved"
    )
    assert result["function"]["parameters"]["required"] == ["location"], (
        "Required should be preserved"
    )

    # Verify descriptions compressed
    original_desc = schema["function"]["description"]
    result_desc = result["function"]["description"]
    assert len(result_desc) <= len(original_desc), "Description should be compressed or unchanged"

    print("✓ SchemaCompressor works correctly")


def test_response_compressor():
    """Test ResponseCompressor operation."""
    print("\nTesting ResponseCompressor...")
    from prompt_refiner import ResponseCompressor

    # Simple test case
    response = {
        "data": {
            "name": "Alice",
            "bio": "x" * 1000,  # Very long string
        },
        "items": list(range(100)),  # Very long list
        "logs": ["log1", "log2"],  # Should be removed
        "debug": "debug info",  # Should be removed
    }

    operation = ResponseCompressor()
    result = operation.process(response)

    # Verify structure preserved
    assert "data" in result, "Main data should be preserved"
    assert result["data"]["name"] == "Alice", "Names should be preserved"

    # Verify compression applied
    assert "debug" not in result, "Debug field should be removed"
    assert "logs" not in result, "Logs field should be removed"

    # Verify string truncation
    if "bio" in result.get("data", {}):
        bio_length = len(result["data"]["bio"])
        assert bio_length <= 512 + 20, (
            "Long strings should be truncated (with some margin for markers)"
        )

    # Verify list truncation
    if "items" in result:
        assert len(result["items"]) <= 16 + 1, (
            "Long lists should be truncated (with some margin for markers)"
        )

    print("✓ ResponseCompressor works correctly")


def test_response_compressor_options():
    """Test ResponseCompressor with different options."""
    print("\nTesting ResponseCompressor options...")
    from prompt_refiner import ResponseCompressor

    response = {
        "name": "Test",
        "value": None,
        "empty_list": [],
        "empty_dict": {},
        "data": "content",
    }

    # Test with drop_null_fields=True
    operation = ResponseCompressor(drop_null_fields=True)
    result = operation.process(response)
    assert "value" not in result, "Null values should be dropped"
    assert "name" in result, "Non-null values should be kept"

    # Test with drop_empty_fields=True
    operation = ResponseCompressor(drop_empty_fields=True)
    result = operation.process(response)
    assert "empty_list" not in result, "Empty lists should be dropped"
    assert "empty_dict" not in result, "Empty dicts should be dropped"
    assert "data" in result, "Non-empty values should be kept"

    print("✓ ResponseCompressor options work correctly")


def test_tools_pipeline():
    """Test using tools in a pipeline."""
    print("\nTesting Tools in Pipeline...")
    from prompt_refiner import ResponseCompressor, SchemaCompressor

    # This is a conceptual test - tools are typically used separately
    # but we can verify they work in sequence

    # First compress a schema
    schema = {
        "type": "function",
        "function": {
            "name": "test_function",
            "description": "A test function with a long description that should be compressed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "A parameter with a very detailed description.",
                    }
                },
            },
        },
    }

    schema_compressor = SchemaCompressor()
    compressed_schema = schema_compressor.process(schema)

    # Then compress a response
    response = {
        "result": "success",
        "data": {"items": list(range(50))},
        "debug": "should be removed",
    }

    response_compressor = ResponseCompressor()
    compressed_response = response_compressor.process(response)

    # Verify both compressions worked
    assert compressed_schema["function"]["name"] == "test_function", "Schema should be compressed"
    assert "debug" not in compressed_response, "Response should be compressed"

    print("✓ Tools Pipeline works correctly")


def main():
    """Run all tools e2e tests."""
    print("=" * 60)
    print("Running Tools Module E2E Tests")
    print("=" * 60)

    try:
        test_schema_compressor()
        test_response_compressor()
        test_response_compressor_options()
        test_tools_pipeline()

        print("\n" + "=" * 60)
        print("✓ All Tools E2E tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
