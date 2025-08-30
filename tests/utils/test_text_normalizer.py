import pytest
from utils.text_normalizer import normalize_text


class TestNormalizeText:
    def test_normalize_text_basic(self):
        text = "Hello World"
        result = normalize_text(text)
        assert result == "hello world"

    def test_normalize_text_with_numbers(self):
        text = "I have 123 apples"
        result = normalize_text(text)
        assert "one hundred and twenty three" in result

    def test_normalize_text_with_quotes(self):
        text = "'Hello' and \"world\""
        result = normalize_text(text)
        assert "'hello' and \"world\"" == result

    def test_normalize_text_with_unicode_quotes(self):
        text = "„Smart quotes‟ and ‚single‚"
        result = normalize_text(text)
        assert "smart quotes" in result
        assert "single" in result

    def test_normalize_text_with_emojis(self):
        text = "Hello 😊 world 🌍"
        result = normalize_text(text)
        assert "😊" not in result
        assert "🌍" not in result
        assert "hello" in result
        assert "world" in result

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Hello, world! How are you?", "hello world how are you"),
            ("Hello   world", "hello world"),
            ("", ""),
            ("!@#$%^&*()", ""),
        ],
    )
    def test_normalize_text_edge_cases(self, text, expected):
        result = normalize_text(text)
        assert result == expected
