import re
import unicodedata
from num2words import num2words


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text.lower())
    text = re.sub(
        r"[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff"
        r"\U0001f1e0-\U0001f1ff\U00002702-\U000027b0\U000024c2-\U0001f251]+",
        "",
        text,
        flags=re.UNICODE,
    )
    text = text.translate(
        str.maketrans(
            {
                "‘": "'",
                "’": "'",
                "‚": "'",
                "‛": "'",
                "“": '"',
                "”": '"',
                "„": '"',
                "‟": '"',
            }
        )
    )
    text = re.sub(r"\d+", lambda m: num2words(m.group(0)).replace("-", " "), text)
    text = re.sub(r"[^\w\s'\"`]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


if __name__ == "__main__":
    sample_text = "“Hello”, world! 123 ‘John’s’ text! „Smart qu'otes‟ test. 😊"
    print(normalize_text(sample_text))
