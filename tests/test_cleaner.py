"""Tests for Cleaner module operations."""

from prompt_refiner import FixUnicode, NormalizeWhitespace, StripHTML


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
