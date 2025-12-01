"""Tests for Cleaner module operations."""

import json

from prompt_refiner import FixUnicode, JsonCleaner, NormalizeWhitespace, StripHTML


def test_strip_html_basic():
    """Test basic HTML stripping."""
    op = StripHTML()
    assert op.process("<div>hello</div>") == "hello"
    assert op.process("<b>bold</b> text") == "bold text"


def test_strip_html_nested():
    """Test nested HTML stripping."""
    op = StripHTML()
    assert op.process("<div><span>nested</span></div>") == "nested"


def test_strip_html_to_markdown():
    """Test HTML to Markdown conversion."""
    op = StripHTML(to_markdown=True)
    assert op.process("<strong>bold</strong>") == "**bold**"
    assert op.process("<em>italic</em>") == "*italic*"
    assert op.process("<h1>Header</h1>") == "# Header"


def test_strip_html_preserve_tags():
    """Test preserving specific HTML tags."""
    op = StripHTML(preserve_tags={"p"})
    result = op.process("<div><p>Keep this</p><span>Remove this</span></div>")
    assert "<p>" in result
    assert "<span>" not in result


def test_normalize_whitespace():
    """Test whitespace normalization."""
    op = NormalizeWhitespace()
    assert op.process("hello   world") == "hello world"
    assert op.process("  spaces  ") == "spaces"
    assert op.process("line\n\nbreaks") == "line breaks"


def test_fix_unicode_zero_width():
    """Test removal of zero-width characters."""
    op = FixUnicode()
    text_with_zwsp = "hello\u200bworld"
    result = op.process(text_with_zwsp)
    assert result == "helloworld"


def test_fix_unicode_control_chars():
    """Test removal of control characters."""
    op = FixUnicode(remove_control_chars=True)
    # Keep newlines and tabs
    result = op.process("hello\nworld\ttest")
    assert "\n" in result
    assert "\t" in result


def test_json_cleaner_strip_nulls():
    """Test stripping null values from JSON."""
    op = JsonCleaner(strip_nulls=True, strip_empty=False)
    input_json = '{"name": "Alice", "age": null, "city": "NYC"}'
    result = op.process(input_json)
    parsed = json.loads(result)

    assert "name" in parsed
    assert "age" not in parsed  # null removed
    assert "city" in parsed


def test_json_cleaner_strip_empty_dict():
    """Test stripping empty dictionaries from JSON."""
    op = JsonCleaner(strip_nulls=False, strip_empty=True)
    input_json = '{"data": {"nested": {}}, "value": 42}'
    result = op.process(input_json)
    parsed = json.loads(result)

    assert "data" not in parsed  # empty nested dict removed
    assert "value" in parsed


def test_json_cleaner_strip_empty_list():
    """Test stripping empty lists from JSON."""
    op = JsonCleaner(strip_nulls=False, strip_empty=True)
    input_json = '{"tags": [], "count": 5}'
    result = op.process(input_json)
    parsed = json.loads(result)

    assert "tags" not in parsed  # empty list removed
    assert "count" in parsed


def test_json_cleaner_strip_empty_string():
    """Test stripping empty strings from JSON."""
    op = JsonCleaner(strip_nulls=False, strip_empty=True)
    input_json = '{"name": "", "bio": "Developer"}'
    result = op.process(input_json)
    parsed = json.loads(result)

    assert "name" not in parsed  # empty string removed
    assert "bio" in parsed


def test_json_cleaner_combined():
    """Test both strip_nulls and strip_empty together."""
    op = JsonCleaner(strip_nulls=True, strip_empty=True)
    input_json = """
    {
        "name": "Alice",
        "age": null,
        "address": {},
        "tags": [],
        "bio": "",
        "score": 0
    }
    """
    result = op.process(input_json)
    parsed = json.loads(result)

    # Only name and score should remain (0 is not null or empty)
    assert parsed == {"name": "Alice", "score": 0}


def test_json_cleaner_nested_structure():
    """Test cleaning nested JSON structures."""
    op = JsonCleaner(strip_nulls=True, strip_empty=True)
    input_json = """
    {
        "user": {
            "name": "Bob",
            "email": null,
            "profile": {
                "bio": "",
                "avatar": null,
                "settings": {}
            }
        },
        "posts": []
    }
    """
    result = op.process(input_json)
    parsed = json.loads(result)

    # After cleaning, profile becomes empty dict and gets removed,
    # then user only has name
    assert parsed == {"user": {"name": "Bob"}}


def test_json_cleaner_array_cleaning():
    """Test cleaning arrays with nulls and empties."""
    op = JsonCleaner(strip_nulls=True, strip_empty=True)
    input_json = """
    {
        "items": [
            {"id": 1, "name": "Item1"},
            {"id": 2, "name": null},
            {},
            {"id": 3, "name": ""}
        ]
    }
    """
    result = op.process(input_json)
    parsed = json.loads(result)

    # First item: {"id": 1, "name": "Item1"} - kept as-is
    # Second item: {"id": 2, "name": null} - name removed, becomes {"id": 2}
    # Third item: {} - empty dict removed from array
    # Fourth item: {"id": 3, "name": ""} - name removed, becomes {"id": 3}
    assert len(parsed["items"]) == 3
    assert parsed["items"][0] == {"id": 1, "name": "Item1"}
    assert parsed["items"][1] == {"id": 2}
    assert parsed["items"][2] == {"id": 3}


def test_json_cleaner_minification():
    """Test that output is minified (no whitespace)."""
    op = JsonCleaner(strip_nulls=False, strip_empty=False)
    input_json = """
    {
        "name": "Alice",
        "age": 30
    }
    """
    result = op.process(input_json)

    # Should be minified (no spaces after colons/commas)
    assert result == '{"name":"Alice","age":30}'


def test_json_cleaner_dict_input():
    """Test that dict input works directly."""
    op = JsonCleaner(strip_nulls=True, strip_empty=True)
    input_dict = {"name": "Alice", "age": None, "tags": []}

    result = op.process(input_dict)
    parsed = json.loads(result)

    assert parsed == {"name": "Alice"}


def test_json_cleaner_list_input():
    """Test that list input works directly."""
    op = JsonCleaner(strip_nulls=True, strip_empty=True)
    input_list = [{"id": 1}, {"id": 2, "data": None}, {}]

    result = op.process(input_list)
    parsed = json.loads(result)

    # Third item (empty dict) removed, second item loses data field
    assert len(parsed) == 2
    assert parsed[0] == {"id": 1}
    assert parsed[1] == {"id": 2}


def test_json_cleaner_invalid_json():
    """Test that invalid JSON is returned unchanged."""
    op = JsonCleaner(strip_nulls=True, strip_empty=True)
    invalid_json = "not valid json {{"

    result = op.process(invalid_json)

    # Should return input unchanged
    assert result == invalid_json


def test_json_cleaner_preserve_false_and_zero():
    """Test that False and 0 are not treated as empty."""
    op = JsonCleaner(strip_nulls=True, strip_empty=True)
    input_json = """
    {
        "active": false,
        "count": 0,
        "rating": 0.0,
        "name": ""
    }
    """
    result = op.process(input_json)
    parsed = json.loads(result)

    # False and 0 should be kept, empty string removed
    assert parsed == {"active": False, "count": 0, "rating": 0.0}


def test_json_cleaner_unicode():
    """Test that Unicode characters are preserved."""
    op = JsonCleaner(strip_nulls=True, strip_empty=False)
    input_json = '{"name": "测试", "emoji": "🎉", "data": null}'
    result = op.process(input_json)
    parsed = json.loads(result)

    assert parsed == {"name": "测试", "emoji": "🎉"}


def test_json_cleaner_no_stripping():
    """Test with both options disabled (only minifies)."""
    op = JsonCleaner(strip_nulls=False, strip_empty=False)
    input_json = """
    {
        "name": "Alice",
        "age": null,
        "tags": []
    }
    """
    result = op.process(input_json)
    parsed = json.loads(result)

    # All fields preserved
    assert parsed == {"name": "Alice", "age": None, "tags": []}


def test_json_cleaner_deeply_nested():
    """Test cleaning deeply nested structures."""
    op = JsonCleaner(strip_nulls=True, strip_empty=True)
    input_json = """
    {
        "level1": {
            "level2": {
                "level3": {
                    "level4": {
                        "value": null,
                        "data": {}
                    }
                }
            }
        }
    }
    """
    result = op.process(input_json)
    parsed = json.loads(result)

    # Everything gets cleaned up recursively
    assert parsed == {}


def test_json_cleaner_array_with_nulls_not_stripped():
    """Test that nulls are kept when strip_nulls=False."""
    op = JsonCleaner(strip_nulls=False, strip_empty=True)
    input_json = '{"items": [1, null, 2, null, 3]}'
    result = op.process(input_json)
    parsed = json.loads(result)

    # Nulls should be preserved
    assert parsed == {"items": [1, None, 2, None, 3]}


def test_json_cleaner_primitive_values_in_array():
    """Test arrays with primitive values (non-null, non-empty)."""
    op = JsonCleaner(strip_nulls=True, strip_empty=True)
    input_json = '{"numbers": [1, 2, 3], "booleans": [true, false], "strings": ["a", "b"]}'
    result = op.process(input_json)
    parsed = json.loads(result)

    # All primitive values should be preserved
    assert parsed == {"numbers": [1, 2, 3], "booleans": [True, False], "strings": ["a", "b"]}


def test_json_cleaner_array_with_direct_nulls():
    """Test array containing direct null values (not nested in objects)."""
    op = JsonCleaner(strip_nulls=True, strip_empty=False)
    input_json = '{"items": [1, null, 2, null, 3]}'
    result = op.process(input_json)
    parsed = json.loads(result)

    # Direct nulls in array should be removed
    assert parsed == {"items": [1, 2, 3]}
