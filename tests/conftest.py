import pytest
import sys
from pathlib import Path


src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def sample_speaker_data():
    from data.models import Speaker

    return Speaker(
        name="John Doe",
        speaker_id="john-doe-12345",
        source_presentation=Path("/path/to/presentation.pdf"),
        source_transcript=Path("/path/to/transcript.txt"),
    )


@pytest.fixture
def sample_chunks():
    from data.models import Chunk, Section

    section = Section("Sample content", 0)
    return [
        Chunk("First chunk content", [section]),
        Chunk("Second chunk content", [section]),
        Chunk("Third chunk content", [section]),
    ]
