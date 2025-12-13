"""Tests for ResponseCompressor operation."""

import json

from prompt_refiner import ResponseCompressor


def test_response_compressor_basic():
    """Test basic response compression."""
    response = {"status": "success", "data": "test"}

    compressor = ResponseCompressor()
    result = compressor.process(response)

    assert result["status"] == "success"
    assert result["data"] == "test"


def test_response_compressor_string_truncation():
    """Test string truncation."""
    response = {"long_text": "x" * 1000}

    compressor = ResponseCompressor()
    result = compressor.process(response)

    assert len(result["long_text"]) <= 530  # 512 + suffix
    assert "truncated" in result["long_text"]


def test_response_compressor_list_truncation():
    """Test list truncation."""
    response = {"items": list(range(100))}

    compressor = ResponseCompressor()
    result = compressor.process(response)

    # 16 items + 1 truncation marker
    assert len(result["items"]) == 17
    assert "truncated from 100 to 16" in str(result["items"][-1])


def test_response_compressor_drop_debug_keys():
    """Test dropping debug/trace keys."""
    response = {
        "data": "important",
        "debug": "verbose debug info",
        "trace": "stack trace",
        "logs": ["log1", "log2"],
    }

    compressor = ResponseCompressor()
    result = compressor.process(response)

    assert "data" in result
    assert "debug" not in result
    assert "trace" not in result
    assert "logs" not in result


def test_response_compressor_custom_drop_keys():
    """Test custom drop keys."""
    response = {"data": "keep", "internal": "drop", "metadata": "drop"}

    compressor = ResponseCompressor(drop_keys={"internal", "metadata"})
    result = compressor.process(response)

    assert "data" in result
    assert "internal" not in result
    assert "metadata" not in result


def test_response_compressor_drop_null_fields():
    """Test dropping null fields."""
    response = {"value": "test", "empty": None, "zero": 0}

    compressor = ResponseCompressor(drop_null_fields=True)
    result = compressor.process(response)

    assert "value" in result
    assert "empty" not in result
    assert "zero" in result  # 0 is not null


def test_response_compressor_keep_null_fields():
    """Test keeping null fields when configured."""
    response = {"value": "test", "empty": None}

    compressor = ResponseCompressor(drop_null_fields=False)
    result = compressor.process(response)

    assert "value" in result
    assert "empty" in result
    assert result["empty"] is None


def test_response_compressor_drop_empty_fields():
    """Test dropping empty fields."""
    response = {
        "text": "keep",
        "empty_string": "",
        "empty_list": [],
        "empty_dict": {},
        "zero": 0,
    }

    compressor = ResponseCompressor(drop_empty_fields=True)
    result = compressor.process(response)

    assert "text" in result
    assert "empty_string" not in result
    assert "empty_list" not in result
    assert "empty_dict" not in result
    assert "zero" in result  # 0 is not empty


def test_response_compressor_keep_empty_fields():
    """Test keeping empty fields when configured."""
    response = {"text": "keep", "empty_string": "", "empty_list": []}

    compressor = ResponseCompressor(drop_empty_fields=False)
    result = compressor.process(response)

    assert "text" in result
    assert "empty_string" in result
    assert "empty_list" in result


def test_response_compressor_nested_objects():
    """Test compression of nested objects."""
    response = {
        "level1": {
            "level2": {
                "level3": {"data": "x" * 1000, "debug": "verbose"},
                "items": list(range(50)),
            }
        }
    }

    compressor = ResponseCompressor()
    result = compressor.process(response)

    # Check nested string truncation
    assert len(result["level1"]["level2"]["level3"]["data"]) <= 530
    # Check debug key removed
    assert "debug" not in result["level1"]["level2"]["level3"]
    # Check list truncation (16 items + 1 marker)
    assert len(result["level1"]["level2"]["items"]) == 17


def test_response_compressor_max_depth():
    """Test max depth protection."""
    # Create deeply nested structure (9 levels deep)
    response = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": "deep"}}}}}}}}}

    compressor = ResponseCompressor(max_depth=5)
    result = compressor.process(response)

    # Navigate to depth 5 (a->b->c->d->e)
    current = result
    for _ in range(5):
        current = list(current.values())[0]

    # At depth 6 (f level), should be truncated
    current = list(current.values())[0]
    assert isinstance(current, str)
    assert "truncated at depth" in current


def test_response_compressor_dict_input():
    """Test processing dict input."""
    response = {"data": "x" * 1000, "debug": "verbose"}

    compressor = ResponseCompressor()
    result = compressor.process(response)

    # Result should be dict
    assert isinstance(result, dict)
    assert len(result["data"]) <= 530
    assert "debug" not in result


def test_response_compressor_list_input():
    """Test processing list input."""
    data = list(range(100))

    compressor = ResponseCompressor()
    result = compressor.process(data)

    assert isinstance(result, list)
    # 16 items + 1 marker
    assert len(result) == 17
    assert "truncated from 100 to 16" in str(result[-1])


def test_response_compressor_no_truncation_marker():
    """Test disabling truncation markers."""
    response = {"items": list(range(100)), "text": "x" * 1000}

    compressor = ResponseCompressor(add_truncation_marker=False)
    result = compressor.process(response)

    # List should have exactly 16 items (no marker)
    assert len(result["items"]) == 16
    # String should not have suffix
    assert "truncated" not in result["text"]


def test_response_compressor_custom_suffix():
    """Test custom truncation suffix."""
    response = {"text": "x" * 1000}

    compressor = ResponseCompressor(truncation_suffix="[...]")
    result = compressor.process(response)

    assert "[...]" in result["text"]
    assert "truncated" not in result["text"]


def test_response_compressor_numbers_and_booleans():
    """Test that numbers and booleans pass through unchanged."""
    response = {
        "int_value": 42,
        "float_value": 3.14,
        "bool_true": True,
        "bool_false": False,
        "zero": 0,
    }

    compressor = ResponseCompressor()
    result = compressor.process(response)

    assert result["int_value"] == 42
    assert result["float_value"] == 3.14
    assert result["bool_true"] is True
    assert result["bool_false"] is False
    assert result["zero"] == 0


def test_response_compressor_mixed_types():
    """Test compression with mixed data types."""
    response = {
        "string": "test",
        "number": 123,
        "bool": True,
        "null": None,
        "list": [1, 2, 3],
        "dict": {"nested": "value"},
    }

    compressor = ResponseCompressor(drop_null_fields=True)
    result = compressor.process(response)

    assert result["string"] == "test"
    assert result["number"] == 123
    assert result["bool"] is True
    assert "null" not in result
    assert result["list"] == [1, 2, 3]
    assert result["dict"]["nested"] == "value"


def test_response_compressor_real_world_api_response():
    """Test with realistic API response."""
    response = {
        "status": "success",
        "data": {
            "results": [
                {
                    "id": i,
                    "title": f"Item {i}",
                    "description": "Lorem ipsum " * 100,
                    "metadata": {"created": "2024-01-01", "updated": "2024-01-02"},
                }
                for i in range(50)
            ],
            "pagination": {"page": 1, "total": 50, "has_more": False},
            "debug": {"query_time_ms": 123, "cache_hit": True},
        },
        "trace": {"request_id": "abc123", "timestamp": "2024-01-01T00:00:00Z"},
    }

    compressor = ResponseCompressor()
    result = compressor.process(response)

    # Status preserved
    assert result["status"] == "success"
    # Results truncated (16 items + 1 marker)
    assert len(result["data"]["results"]) == 17
    # Descriptions truncated
    assert len(result["data"]["results"][0]["description"]) <= 530
    # Pagination preserved
    assert result["data"]["pagination"]["total"] == 50
    # Debug removed
    assert "debug" not in result["data"]
    # Trace removed
    assert "trace" not in result


def test_response_compressor_case_insensitive_drop_keys():
    """Test that drop_keys matching is case-insensitive."""
    response = {"data": "keep", "DEBUG": "drop", "Trace": "drop", "LOGS": "drop"}

    compressor = ResponseCompressor()
    result = compressor.process(response)

    assert "data" in result
    assert "DEBUG" not in result
    assert "Trace" not in result
    assert "LOGS" not in result


def test_response_compressor_tuple_handling():
    """Test that tuples are converted to lists."""
    response = {"items": tuple(range(100))}

    compressor = ResponseCompressor()
    result = compressor.process(response)

    assert isinstance(result["items"], list)
    # 16 items + 1 marker
    assert len(result["items"]) == 17


def test_response_compressor_in_refiner_pipeline():
    """Test ResponseCompressor works in a Pipeline."""
    from prompt_refiner import Pipeline

    response = {"data": "x" * 1000, "debug": "verbose"}

    pipeline = Pipeline().pipe(ResponseCompressor())
    result = pipeline.run(response)

    assert len(result["data"]) <= 530
    assert "debug" not in result


def test_response_compressor_empty_response():
    """Test handling empty response."""
    compressor = ResponseCompressor()

    assert compressor.process({}) == {}
    assert compressor.process([]) == []
    assert compressor.process("") == ""


def test_response_compressor_preserves_structure():
    """Test that compression preserves overall structure."""
    response = {
        "metadata": {"version": "1.0", "timestamp": "2024-01-01"},
        "results": [{"id": 1, "name": "test"}],
        "pagination": {"page": 1, "size": 10},
    }

    compressor = ResponseCompressor()
    result = compressor.process(response)

    # Structure preserved
    assert "metadata" in result
    assert "results" in result
    assert "pagination" in result
    # Values accessible
    assert result["metadata"]["version"] == "1.0"
    assert result["results"][0]["id"] == 1


def test_response_compressor_token_savings():
    """Test that compression achieves significant token savings."""
    # Simulate verbose API response
    response = {
        "results": [
            {
                "id": i,
                "description": "Very long description " * 50,
                "debug_info": {"trace": "...", "logs": ["log1", "log2"]},
            }
            for i in range(100)
        ]
    }

    # Original size
    original = json.dumps(response, separators=(",", ":"))
    original_len = len(original)

    # Compressed size
    compressor = ResponseCompressor()
    compressed = compressor.process(response)
    compressed_str = json.dumps(compressed, separators=(",", ":"))
    compressed_len = len(compressed_str)

    # Should achieve significant savings (at least 50%)
    savings = (original_len - compressed_len) / original_len * 100
    assert savings > 50
    print(f"\nToken savings: {savings:.1f}% ({original_len} → {compressed_len} chars)")
