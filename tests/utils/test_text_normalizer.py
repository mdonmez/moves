"""Tests for utils.text_normalizer module."""
import pytest
from unittest.mock import patch

from utils import text_normalizer


def test_normalize_text_converts_to_lowercase():
    """Test normalize_text converts text to lowercase."""
    text = "HELLO World"
    result = text_normalizer.normalize_text(text)
    assert result.islower()
    assert "hello" in result
    assert "world" in result


def test_normalize_text_removes_accents():
    """Test normalize_text removes accent marks from characters."""
    text = "café naïve résumé"
    result = text_normalizer.normalize_text(text)
    assert result == "cafe naive resume"


def test_normalize_text_removes_emojis():
    """Test normalize_text removes emoji characters."""
    text = "Hello 😀 world 🎉 test 💯"
    result = text_normalizer.normalize_text(text)
    assert result == "hello world test"


def test_normalize_text_normalizes_quotes():
    """Test normalize_text normalizes various quote characters."""
    text = "He said 'hello' and \"goodbye\""
    result = text_normalizer.normalize_text(text)
    assert "he said 'hello' and \"goodbye\"" in result


def test_normalize_text_handles_special_quotes():
    """Test normalize_text handles various special quote characters."""
    test_cases = [
        ("'test'", "'test'"),  # Already normalized
        ("'test'", "'test'"),
        ("‚test‛", "'test'"),  
        ('"test"', '"test"'),
        ('"test"', '"test"'),
        ("„test‟", '"test"'),
    ]
    
    for input_text, expected_quotes in test_cases:
        result = text_normalizer.normalize_text(input_text)
        # Extract just the quote characters
        for char in expected_quotes:
            if char in ["'", '"']:
                assert char in result


@patch('utils.text_normalizer.num2words')
def test_normalize_text_converts_numbers_to_words(mock_num2words):
    """Test normalize_text converts numbers to words."""
    mock_num2words.side_effect = lambda x: "one hundred twenty three"
    
    text = "There are 123 items"
    result = text_normalizer.normalize_text(text)
    
    mock_num2words.assert_called_with("123")
    assert "one hundred twenty three" in result
    assert "123" not in result


@patch('utils.text_normalizer.num2words')
def test_normalize_text_handles_multiple_numbers(mock_num2words):
    """Test normalize_text handles multiple numbers in text."""
    def mock_converter(num_str):
        conversions = {"1": "one", "23": "twenty three", "456": "four hundred fifty six"}
        return conversions.get(num_str, num_str)
    
    mock_num2words.side_effect = mock_converter
    
    text = "I have 1 cat, 23 dogs, and 456 fish"
    result = text_normalizer.normalize_text(text)
    
    assert "one" in result
    assert "twenty three" in result
    assert "four hundred fifty six" in result
    assert "1" not in result
    assert "23" not in result
    assert "456" not in result


def test_normalize_text_removes_punctuation():
    """Test normalize_text removes most punctuation except quotes and apostrophes."""
    text = "Hello, world! How are you? I'm fine & well."
    result = text_normalizer.normalize_text(text)
    
    # Should remove: , ! ? &
    assert "," not in result
    assert "!" not in result
    assert "?" not in result
    assert "&" not in result
    
    # Should keep: apostrophes in contractions
    assert "i'm" in result.lower()


def test_normalize_text_consolidates_whitespace():
    """Test normalize_text consolidates multiple whitespace into single spaces."""
    text = "Hello    world\t\ttest\n\nmore   spaces"
    result = text_normalizer.normalize_text(text)
    
    # Should not have multiple consecutive spaces
    assert "    " not in result
    assert "\t" not in result
    assert "\n" not in result
    assert result == "hello world test more spaces"


def test_normalize_text_strips_leading_trailing_whitespace():
    """Test normalize_text strips leading and trailing whitespace."""
    text = "   hello world   "
    result = text_normalizer.normalize_text(text)
    
    assert result == "hello world"
    assert not result.startswith(" ")
    assert not result.endswith(" ")


@patch('utils.text_normalizer.num2words')
def test_normalize_text_comprehensive_example(mock_num2words):
    """Test normalize_text with a comprehensive example."""
    mock_num2words.return_value = "twenty one"
    
    text = "  HELLO, Café! 🎉 I'm 21 years old... \"Great!\"   "
    result = text_normalizer.normalize_text(text)
    
    expected_parts = ["hello", "cafe", "i'm", "twenty one", "years", "old", "great"]
    for part in expected_parts:
        assert part in result.lower()
    
    # Should not contain original problematic parts
    assert "HELLO" not in result
    assert "🎉" not in result
    assert "21" not in result
    assert "..." not in result


def test_normalize_text_handles_empty_string():
    """Test normalize_text handles empty strings."""
    result = text_normalizer.normalize_text("")
    assert result == ""


def test_normalize_text_handles_only_whitespace():
    """Test normalize_text handles strings with only whitespace."""
    result = text_normalizer.normalize_text("   \t\n   ")
    assert result == ""


def test_normalize_text_handles_only_punctuation():
    """Test normalize_text handles strings with only punctuation."""
    text = "!@#$%^&*()"
    result = text_normalizer.normalize_text(text)
    assert result == ""


@patch('utils.text_normalizer.num2words')
def test_normalize_text_handles_only_numbers(mock_num2words):
    """Test normalize_text handles strings with only numbers."""
    mock_num2words.side_effect = lambda x: {"123": "one hundred twenty three", "456": "four hundred fifty six"}[x]
    
    text = "123 456"
    result = text_normalizer.normalize_text(text)
    
    assert "one hundred twenty three four hundred fifty six" == result


@pytest.mark.parametrize("input_text,expected_parts", [
    ("simple text", ["simple", "text"]),
    ("UPPERCASE", ["uppercase"]),
    ("MixedCase", ["mixedcase"]),
    ("with-dashes", ["with", "dashes"]),  # Dashes become spaces
    ("under_scores", ["under", "scores"]), # Underscores become spaces
])
def test_normalize_text_parametrized(input_text, expected_parts):
    """Test normalize_text with various input patterns."""
    with patch('utils.text_normalizer.num2words') as mock_num2words:
        # Mock to return the number as-is if no conversion needed
        mock_num2words.side_effect = lambda x: x
        
        result = text_normalizer.normalize_text(input_text)
        
        for part in expected_parts:
            assert part in result


def test_normalize_text_preserves_apostrophes_in_contractions():
    """Test normalize_text preserves apostrophes in contractions."""
    contractions = ["don't", "can't", "won't", "I'm", "you're", "it's"]
    
    for contraction in contractions:
        result = text_normalizer.normalize_text(contraction)
        # Should still contain the apostrophe
        assert "'" in result
        assert result.count("'") == 1


@patch('utils.text_normalizer.num2words')
def test_normalize_text_handles_numbers_with_hyphens(mock_num2words):
    """Test normalize_text properly handles hyphenated number words."""
    # num2words sometimes returns hyphenated words like "twenty-one"
    mock_num2words.return_value = "twenty-one"
    
    text = "I am 21 today"
    result = text_normalizer.normalize_text(text)
    
    # The function should replace hyphens with spaces in number words
    assert "twenty one" in result
    assert "twenty-one" not in result