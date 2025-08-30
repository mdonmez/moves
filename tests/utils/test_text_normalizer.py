import pytest
from src.utils.text_normalizer import normalize_text


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("Hello World!", "hello world"),
        ("  leading and trailing spaces  ", "leading and trailing spaces"),
        (
            "123 numbers become words",
            "one hundred and twenty three numbers become words",
        ),
        ("Punctuation, should be removed.", "punctuation should be removed"),
        ("“Smart Quotes”", '"smart quotes"'),
        ("İstanbul", "istanbul"),
    ],
)
def test_normalize_text(input_text, expected_output):
    assert normalize_text(input_text) == expected_output
