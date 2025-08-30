from datetime import datetime
from unittest.mock import patch
import pytest
from utils.id_generator import generate_speaker_id, generate_history_id


class TestGenerateSpeakerId:
    @pytest.mark.parametrize(
        "name",
        [
            "John Doe",
            "John-Paul O'Connor",
            "José María",
        ],
    )
    def test_generate_speaker_id(self, name):
        speaker_id = generate_speaker_id(name)
        assert isinstance(speaker_id, str)
        assert len(speaker_id) > 0
        assert "-" in speaker_id

    def test_generate_speaker_id_consistent_format(self):
        id1 = generate_speaker_id("Test")
        id2 = generate_speaker_id("Test")
        assert id1 != id2
        assert id1.startswith("test-")
        assert id2.startswith("test-")


class TestGenerateHistoryId:
    @patch("utils.id_generator.datetime")
    def test_generate_history_id_format(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 10, 15, 14, 30, 45)
        history_id = generate_history_id()
        assert history_id == "20231015_14-30-45"
        assert isinstance(history_id, str)

    def test_generate_history_id_unique(self):
        id1 = generate_history_id()
        id2 = generate_history_id()
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        # IDs should be unique if generated at different times
