"""Tests for data.models module."""
import pytest
from pathlib import Path
from dataclasses import FrozenInstanceError

from data.models import (
    Section,
    Chunk,
    Speaker,
    SimilarityResult,
    Settings,
    ProcessResult,
    SpeakerId,
    HistoryId
)


def test_section_creation():
    """Test Section dataclass creation and immutability."""
    section = Section(content="Test content", section_index=1)
    
    assert section.content == "Test content"
    assert section.section_index == 1
    
    # Test immutability
    with pytest.raises(FrozenInstanceError):
        section.content = "New content"


def test_section_equality():
    """Test Section equality comparison."""
    section1 = Section(content="Test content", section_index=1)
    section2 = Section(content="Test content", section_index=1)
    section3 = Section(content="Different content", section_index=1)
    
    assert section1 == section2
    assert section1 != section3


def test_chunk_creation():
    """Test Chunk dataclass creation and immutability."""
    sections = [
        Section(content="Section 1", section_index=0),
        Section(content="Section 2", section_index=1)
    ]
    chunk = Chunk(partial_content="Partial content", source_sections=sections)
    
    assert chunk.partial_content == "Partial content"
    assert chunk.source_sections == sections
    assert len(chunk.source_sections) == 2
    
    # Test immutability
    with pytest.raises(FrozenInstanceError):
        chunk.partial_content = "New content"


def test_chunk_with_empty_sections():
    """Test Chunk can be created with empty sections list."""
    chunk = Chunk(partial_content="Content", source_sections=[])
    
    assert chunk.partial_content == "Content"
    assert chunk.source_sections == []


def test_speaker_creation():
    """Test Speaker dataclass creation and mutability."""
    source_presentation = Path("/path/to/presentation.pdf")
    source_transcript = Path("/path/to/transcript.pdf")
    
    speaker = Speaker(
        name="John Doe",
        speaker_id="john-doe-abc123",
        source_presentation=source_presentation,
        source_transcript=source_transcript
    )
    
    assert speaker.name == "John Doe"
    assert speaker.speaker_id == "john-doe-abc123"
    assert speaker.source_presentation == source_presentation
    assert speaker.source_transcript == source_transcript


def test_speaker_mutability():
    """Test Speaker dataclass is mutable (not frozen)."""
    speaker = Speaker(
        name="John Doe",
        speaker_id="john-doe-abc123",
        source_presentation=Path("/old/path.pdf"),
        source_transcript=Path("/old/transcript.pdf")
    )
    
    # Should be able to modify speaker attributes
    speaker.name = "Jane Doe"
    speaker.source_presentation = Path("/new/path.pdf")
    
    assert speaker.name == "Jane Doe"
    assert speaker.source_presentation == Path("/new/path.pdf")


def test_similarity_result_creation():
    """Test SimilarityResult dataclass creation and immutability."""
    sections = [Section(content="Test", section_index=0)]
    chunk = Chunk(partial_content="Test content", source_sections=sections)
    
    result = SimilarityResult(chunk=chunk, score=0.85)
    
    assert result.chunk == chunk
    assert result.score == 0.85
    
    # Test immutability
    with pytest.raises(FrozenInstanceError):
        result.score = 0.95


def test_similarity_result_score_types():
    """Test SimilarityResult accepts different numeric types for score."""
    sections = [Section(content="Test", section_index=0)]
    chunk = Chunk(partial_content="Test content", source_sections=sections)
    
    # Test with int
    result1 = SimilarityResult(chunk=chunk, score=1)
    assert result1.score == 1
    
    # Test with float
    result2 = SimilarityResult(chunk=chunk, score=0.75)
    assert result2.score == 0.75


def test_settings_creation():
    """Test Settings dataclass creation and mutability."""
    settings = Settings(model="gpt-4", key="sk-test-key")
    
    assert settings.model == "gpt-4"
    assert settings.key == "sk-test-key"


def test_settings_mutability():
    """Test Settings dataclass is mutable."""
    settings = Settings(model="gpt-3.5-turbo", key="old-key")
    
    settings.model = "gpt-4"
    settings.key = "new-key"
    
    assert settings.model == "gpt-4"
    assert settings.key == "new-key"


def test_process_result_creation():
    """Test ProcessResult dataclass creation and immutability."""
    result = ProcessResult(
        section_count=5,
        transcript_from="SOURCE",
        presentation_from="LOCAL"
    )
    
    assert result.section_count == 5
    assert result.transcript_from == "SOURCE"
    assert result.presentation_from == "LOCAL"
    
    # Test immutability
    with pytest.raises(FrozenInstanceError):
        result.section_count = 10


@pytest.mark.parametrize("transcript_from", ["SOURCE", "LOCAL"])
@pytest.mark.parametrize("presentation_from", ["SOURCE", "LOCAL"])
def test_process_result_literal_types(transcript_from, presentation_from):
    """Test ProcessResult accepts only valid literal values."""
    result = ProcessResult(
        section_count=3,
        transcript_from=transcript_from,
        presentation_from=presentation_from
    )
    
    assert result.transcript_from == transcript_from
    assert result.presentation_from == presentation_from


def test_speaker_id_type_alias():
    """Test SpeakerId is a string type alias."""
    speaker_id: SpeakerId = "test-speaker-123"
    assert isinstance(speaker_id, str)
    assert speaker_id == "test-speaker-123"


def test_history_id_type_alias():
    """Test HistoryId is a string type alias."""
    history_id: HistoryId = "20231225_14-30-45"
    assert isinstance(history_id, str)
    assert history_id == "20231225_14-30-45"


def test_section_with_empty_content():
    """Test Section can be created with empty content."""
    section = Section(content="", section_index=0)
    assert section.content == ""
    assert section.section_index == 0


def test_section_with_large_index():
    """Test Section can handle large section indices."""
    section = Section(content="Test", section_index=1000000)
    assert section.section_index == 1000000


def test_chunk_with_large_content():
    """Test Chunk can handle large content strings."""
    large_content = "x" * 10000
    sections = [Section(content="Test", section_index=0)]
    chunk = Chunk(partial_content=large_content, source_sections=sections)
    
    assert len(chunk.partial_content) == 10000
    assert chunk.partial_content == large_content


def test_speaker_with_absolute_paths():
    """Test Speaker works with absolute paths."""
    presentation_path = Path("/home/user/presentation.pdf").resolve()
    transcript_path = Path("/home/user/transcript.pdf").resolve()
    
    speaker = Speaker(
        name="Test Speaker",
        speaker_id="test-speaker-123",
        source_presentation=presentation_path,
        source_transcript=transcript_path
    )
    
    assert speaker.source_presentation.is_absolute()
    assert speaker.source_transcript.is_absolute()


def test_speaker_with_relative_paths():
    """Test Speaker works with relative paths."""
    presentation_path = Path("docs/presentation.pdf")
    transcript_path = Path("docs/transcript.pdf")
    
    speaker = Speaker(
        name="Test Speaker",
        speaker_id="test-speaker-123",
        source_presentation=presentation_path,
        source_transcript=transcript_path
    )
    
    assert speaker.source_presentation == presentation_path
    assert speaker.source_transcript == transcript_path


def test_similarity_result_ordering():
    """Test SimilarityResult can be ordered by score."""
    sections = [Section(content="Test", section_index=0)]
    chunk = Chunk(partial_content="Test", source_sections=sections)
    
    results = [
        SimilarityResult(chunk=chunk, score=0.3),
        SimilarityResult(chunk=chunk, score=0.8),
        SimilarityResult(chunk=chunk, score=0.5),
    ]
    
    sorted_results = sorted(results, key=lambda r: r.score, reverse=True)
    
    assert sorted_results[0].score == 0.8
    assert sorted_results[1].score == 0.5
    assert sorted_results[2].score == 0.3


def test_dataclass_string_representations():
    """Test string representations of dataclasses are informative."""
    section = Section(content="Test content", section_index=1)
    assert "Test content" in str(section)
    assert "1" in str(section)
    
    settings = Settings(model="gpt-4", key="test-key")
    assert "gpt-4" in str(settings)
    assert "test-key" in str(settings)