import pytest
from pathlib import Path
from src.data.models import Speaker, Section


@pytest.fixture
def mock_speaker():
    return Speaker(
        name="Test Speaker",
        speaker_id="test-speaker-12345",
        source_presentation=Path("/dummy/presentation.pdf"),
        source_transcript=Path("/dummy/transcript.pdf"),
    )


@pytest.fixture
def sample_sections():
    return [
        Section(content="This is the first section.", section_index=0),
        Section(
            content="This is another longer section for testing purposes.",
            section_index=1,
        ),
        Section(content="A third section follows.", section_index=2),
    ]
