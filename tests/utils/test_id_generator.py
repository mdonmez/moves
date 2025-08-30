from src.utils.id_generator import generate_speaker_id, generate_history_id
import re


def test_generate_speaker_id():
    name = "Test User"
    speaker_id = generate_speaker_id(name)
    parts = speaker_id.split("-")

    assert len(parts) == 3
    assert parts[0] == "test"
    assert parts[1] == "user"
    assert len(parts[2]) == 5
    assert parts[2].isalnum()


def test_generate_history_id():
    history_id = generate_history_id()
    pattern = r"^\d{8}_\d{2}-\d{2}-\d{2}$"
    assert re.match(pattern, history_id)
    assert isinstance(history_id, str)
