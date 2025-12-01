"""Tests for Compressor module operations."""

from prompt_refiner import Deduplicate, TruncateTokens


def test_truncate_tokens_head():
    """Test truncation keeping the start."""
    op = TruncateTokens(max_tokens=3, strategy="head", respect_sentence_boundary=False)
    result = op.process("one two three four five")
    assert result == "one two three"


def test_truncate_tokens_tail():
    """Test truncation keeping the end."""
    op = TruncateTokens(max_tokens=3, strategy="tail", respect_sentence_boundary=False)
    result = op.process("one two three four five")
    assert result == "three four five"


def test_truncate_tokens_middle_out():
    """Test truncation keeping start and end."""
    op = TruncateTokens(max_tokens=4, strategy="middle_out", respect_sentence_boundary=False)
    result = op.process("one two three four five six")
    assert "one two" in result
    assert "five six" in result
    assert "..." in result


def test_truncate_tokens_no_truncation():
    """Test that short text is not truncated."""
    op = TruncateTokens(max_tokens=10, strategy="head")
    result = op.process("short text")
    assert result == "short text"


def test_truncate_tokens_sentence_boundary():
    """Test truncation respecting sentence boundaries."""
    op = TruncateTokens(max_tokens=10, strategy="head", respect_sentence_boundary=True)
    text = "First sentence here. Second sentence is longer. Third sentence."
    result = op.process(text)
    # Should keep complete sentences only
    assert "First sentence here." in result


def test_truncate_tokens_head_strategy():
    """Test head truncation strategy."""
    op = TruncateTokens(max_tokens=5, strategy="head", respect_sentence_boundary=False)
    result = op.process("one two three four five six seven")
    assert result == "one two three four five"


def test_truncate_tokens_tail_strategy():
    """Test tail truncation strategy."""
    op = TruncateTokens(max_tokens=5, strategy="tail", respect_sentence_boundary=False)
    result = op.process("one two three four five six seven")
    assert result == "three four five six seven"


def test_truncate_tokens_middle_out_strategy():
    """Test middle_out truncation strategy."""
    op = TruncateTokens(max_tokens=6, strategy="middle_out", respect_sentence_boundary=False)
    result = op.process("one two three four five six seven eight")
    assert "one" in result
    assert "eight" in result
    assert "..." in result


def test_truncate_tokens_head_with_sentences():
    """Test head truncation with sentence boundaries."""
    op = TruncateTokens(max_tokens=8, strategy="head", respect_sentence_boundary=True)
    text = "First sentence. Second sentence is longer. Third sentence."
    result = op.process(text)
    assert "First sentence." in result
    # Should not include partial sentences
    assert result.endswith(".")


def test_truncate_tokens_tail_with_sentences():
    """Test tail truncation with sentence boundaries."""
    op = TruncateTokens(max_tokens=8, strategy="tail", respect_sentence_boundary=True)
    text = "First sentence. Second sentence is longer. Third sentence."
    result = op.process(text)
    assert "Third sentence." in result
    # Should not include partial sentences
    assert result.endswith(".")


def test_truncate_tokens_middle_out_with_sentences():
    """Test middle_out truncation with sentence boundaries."""
    op = TruncateTokens(max_tokens=10, strategy="middle_out", respect_sentence_boundary=True)
    text = (
        "First sentence. Second sentence is here. Third sentence. "
        "Fourth sentence. Fifth sentence here. Sixth sentence. Seventh sentence."
    )
    result = op.process(text)
    # Should have start and end sentences
    assert "First sentence." in result
    assert "Seventh sentence." in result
    assert "..." in result


def test_truncate_tokens_empty_string():
    """Test truncation with empty string."""
    op = TruncateTokens(max_tokens=10, strategy="head")
    result = op.process("")
    assert result == ""


def test_deduplicate_jaccard():
    """Test deduplication using Jaccard similarity."""
    op = Deduplicate(similarity_threshold=0.8, method="jaccard", granularity="sentence")
    text = "Hello world. Hello world. Goodbye world."
    result = op.process(text)
    # Should remove one of the duplicate "Hello world" sentences
    assert result.count("Hello world.") < text.count("Hello world.")


def test_deduplicate_paragraph():
    """Test deduplication at paragraph level."""
    op = Deduplicate(similarity_threshold=0.9, method="jaccard", granularity="paragraph")
    text = "First paragraph.\n\nFirst paragraph.\n\nSecond paragraph."
    result = op.process(text)
    # Should remove duplicate paragraph
    assert result.count("First paragraph.") == 1


def test_deduplicate_levenshtein():
    """Test deduplication using Levenshtein distance."""
    op = Deduplicate(similarity_threshold=0.8, method="levenshtein", granularity="sentence")
    text = "Hello world. Hello word. Goodbye world."
    result = op.process(text)
    # Should detect similar sentences and remove duplicates
    lines = [line.strip() for line in result.split(".") if line.strip()]
    assert len(lines) <= 2


def test_deduplicate_levenshtein_identical():
    """Test Levenshtein with identical texts."""
    op = Deduplicate(similarity_threshold=0.95, method="levenshtein", granularity="sentence")
    text = "Exact same. Exact same. Different text."
    result = op.process(text)
    # Should remove exact duplicate
    assert result.count("Exact same.") == 1


def test_deduplicate_levenshtein_empty():
    """Test Levenshtein with empty text."""
    op = Deduplicate(similarity_threshold=0.8, method="levenshtein", granularity="sentence")
    result = op.process("")
    assert result == ""


def test_deduplicate_no_duplicates():
    """Test deduplication when there are no duplicates."""
    op = Deduplicate(similarity_threshold=0.9, method="jaccard", granularity="sentence")
    text = "First sentence. Second sentence. Third sentence."
    result = op.process(text)
    # Should keep all sentences
    assert "First sentence." in result
    assert "Second sentence." in result
    assert "Third sentence." in result


def test_deduplicate_high_threshold():
    """Test deduplication with very high threshold."""
    op = Deduplicate(similarity_threshold=0.99, method="jaccard", granularity="sentence")
    text = "Hello world. Hello world! Goodbye world."
    result = op.process(text)
    # With high threshold, slight variations are kept
    assert "Hello world." in result


def test_deduplicate_single_sentence():
    """Test deduplication with only one sentence."""
    op = Deduplicate(similarity_threshold=0.8, method="jaccard", granularity="sentence")
    text = "Only one sentence here."
    result = op.process(text)
    assert result == text
