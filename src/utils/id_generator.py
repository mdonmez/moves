from datetime import datetime
import re
import unicodedata
import secrets

from data.models import SpeakerId, HistoryId


def generate_speaker_id(name: str) -> SpeakerId:
    slug = (
        re.sub(
            r"\s+",
            "-",
            re.sub(
                r"[^\w\s-]",
                "",
                unicodedata.normalize("NFKD", name)
                .encode("ascii", "ignore")
                .decode("ascii"),
            ),
        )
        .strip("-")
        .lower()
    )
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    suffix = "".join(secrets.choice(alphabet) for _ in range(5))
    speaker_id = f"{slug}-{suffix}"
    return speaker_id


def generate_history_id() -> HistoryId:
    history_id = datetime.now().strftime("%Y%m%d_%H-%M-%S")
    return history_id


if __name__ == "__main__":
    print(generate_speaker_id("John Doe"))
    print(generate_history_id())
