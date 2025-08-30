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
)


class TestSection:
    def test_section_creation(self):
        section = Section(content="Test content", section_index=1)
        assert section.content == "Test content"
        assert section.section_index == 1

    def test_section_immutable(self):
        section = Section(content="Test", section_index=1)
        with pytest.raises(FrozenInstanceError):
            section.content = "New content"  # type: ignore


class TestChunk:
    def test_chunk_creation(self):
        sections = [Section("Content 1", 0), Section("Content 2", 1)]
        chunk = Chunk(partial_content="Partial", source_sections=sections)
        assert chunk.partial_content == "Partial"
        assert len(chunk.source_sections) == 2

    def test_chunk_immutable(self):
        chunk = Chunk("Partial", [])
        with pytest.raises(FrozenInstanceError):
            chunk.partial_content = "New"  # type: ignore


class TestSpeaker:
    def test_speaker_creation(self):
        speaker = Speaker(
            name="John Doe",
            speaker_id="john-doe-123",
            source_presentation=Path("/path/to/presentation.pdf"),
            source_transcript=Path("/path/to/transcript.txt"),
        )
        assert speaker.name == "John Doe"
        assert speaker.speaker_id == "john-doe-123"
        assert speaker.source_presentation == Path("/path/to/presentation.pdf")
        assert speaker.source_transcript == Path("/path/to/transcript.txt")


class TestSimilarityResult:
    def test_similarity_result_creation(self):
        chunk = Chunk("Content", [])
        result = SimilarityResult(chunk=chunk, score=0.95)
        assert result.chunk == chunk
        assert result.score == 0.95

    def test_similarity_result_immutable(self):
        chunk = Chunk("Content", [])
        result = SimilarityResult(chunk, 0.8)
        with pytest.raises(FrozenInstanceError):
            result.score = 0.9  # type: ignore


class TestSettings:
    def test_settings_creation(self):
        settings = Settings(model="gpt-4", key="api-key-123")
        assert settings.model == "gpt-4"
        assert settings.key == "api-key-123"


class TestProcessResult:
    def test_process_result_creation(self):
        result = ProcessResult(
            section_count=10, transcript_from="SOURCE", presentation_from="LOCAL"
        )
        assert result.section_count == 10
        assert result.transcript_from == "SOURCE"
        assert result.presentation_from == "LOCAL"

    def test_process_result_immutable(self):
        result = ProcessResult(5, "LOCAL", "SOURCE")
        with pytest.raises(FrozenInstanceError):
            result.section_count = 10  # type: ignore
