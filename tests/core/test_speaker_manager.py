import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from data.models import Speaker
from core.speaker_manager import SpeakerManager


class TestSpeakerManager:
    @patch("core.speaker_manager.data_handler")
    @patch("core.speaker_manager.id_generator")
    def test_add_speaker_success(self, mock_id_gen, mock_data_handler):
        mock_data_handler.DATA_FOLDER = Path("/tmp/.moves")
        mock_data_handler.write.return_value = True
        mock_id_gen.generate_speaker_id.return_value = "john-doe-abc12"
        manager = SpeakerManager()
        with patch.object(manager, "list", return_value=[]):
            speaker = manager.add(
                "John Doe", Path("/path/to/pres.pdf"), Path("/path/to/trans.txt")
            )
            assert speaker.name == "John Doe"
            assert speaker.speaker_id == "john-doe-abc12"
            assert speaker.source_presentation == Path("/path/to/pres.pdf").resolve()
            assert speaker.source_transcript == Path("/path/to/trans.txt").resolve()

    @patch("core.speaker_manager.data_handler")
    def test_add_speaker_duplicate_name(self, mock_data_handler):
        mock_data_handler.DATA_FOLDER = Path("/tmp/.moves")
        manager = SpeakerManager()
        existing_speaker = Speaker(
            name="some-name",
            speaker_id="john-doe-abc12",
            source_presentation=Path("/old/pres.pdf"),
            source_transcript=Path("/old/trans.txt"),
        )
        with patch.object(manager, "list", return_value=[existing_speaker]):
            with pytest.raises(
                ValueError,
                match="can't be a same with one of the existing speakers' IDs",
            ):
                manager.add(
                    "john-doe-abc12",
                    Path("/path/to/pres.pdf"),
                    Path("/path/to/trans.txt"),
                )

    @patch("core.speaker_manager.data_handler")
    def test_list_speakers(self, mock_data_handler):
        mock_data_handler.DATA_FOLDER = Path("/tmp/.moves")
        mock_speaker_dir = MagicMock()
        mock_speaker_dir.is_dir.return_value = True
        mock_speaker_dir.name = "john-doe-abc12"
        mock_data_handler.list.return_value = [mock_speaker_dir]
        mock_data_handler.read.return_value = '{"name": "John Doe", "speaker_id": "john-doe-abc12", "source_presentation": "/path/pres.pdf", "source_transcript": "/path/trans.txt"}'
        manager = SpeakerManager()
        speakers = manager.list()
        assert len(speakers) == 1
        assert speakers[0].name == "John Doe"
