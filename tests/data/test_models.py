import pytest
from dataclasses import FrozenInstanceError
from src.data.models import Chunk, SimilarityResult, ProcessResult


def test_section_is_immutable(sample_sections):
    section = sample_sections[0]
    with pytest.raises(FrozenInstanceError):
        section.content = "New content"
    with pytest.raises(FrozenInstanceError):
        section.section_index = 99


def test_chunk_is_immutable(sample_sections):
    chunk = Chunk(partial_content="some content", source_sections=sample_sections)
    with pytest.raises(FrozenInstanceError):
        chunk.partial_content = "new content"  # type: ignore
    with pytest.raises(FrozenInstanceError):
        chunk.source_sections = []  # type: ignore


def test_similarity_result_is_immutable(sample_sections):
    chunk = Chunk(partial_content="c", source_sections=sample_sections)
    result = SimilarityResult(chunk=chunk, score=0.9)
    with pytest.raises(FrozenInstanceError):
        result.score = 0.5  # type: ignore
    with pytest.raises(FrozenInstanceError):
        result.chunk = None  # type: ignore


def test_process_result_is_immutable():
    result = ProcessResult(
        section_count=10, transcript_from="SOURCE", presentation_from="LOCAL"
    )
    with pytest.raises(FrozenInstanceError):
        result.section_count = 5  # type: ignore
