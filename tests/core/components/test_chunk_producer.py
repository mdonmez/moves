from src.core.components.chunk_producer import generate_chunks, get_candidate_chunks
from src.data.models import Chunk, Section


def test_generate_chunks_with_sufficient_words(sample_sections):
    chunks = generate_chunks(sample_sections, window_size=3)
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    for chunk in chunks:
        assert hasattr(chunk, "partial_content")
        assert hasattr(chunk, "source_sections")
        assert isinstance(chunk.partial_content, str)
        assert isinstance(chunk.source_sections, list)


def test_generate_chunks_with_insufficient_words():
    short_sections = [
        Section(content="Short", section_index=0),
        Section(content="Text", section_index=1),
    ]
    chunks = generate_chunks(short_sections, window_size=5)
    assert chunks == []


def test_generate_chunks_normalization():
    sections = [
        Section(content="This is SOME text.", section_index=0),
    ]
    chunks = generate_chunks(sections, window_size=3)
    assert "some" in chunks[0].partial_content.lower()
    assert "." not in chunks[0].partial_content


def test_get_candidate_chunks(sample_sections):
    all_chunks = [
        Chunk(partial_content="chunk1", source_sections=[sample_sections[0]]),
        Chunk(
            partial_content="chunk2",
            source_sections=[sample_sections[0], sample_sections[1]],
        ),
        Chunk(
            partial_content="chunk3",
            source_sections=[sample_sections[1], sample_sections[2]],
        ),
        Chunk(partial_content="chunk4", source_sections=[sample_sections[2]]),
    ]

    current_section = sample_sections[1]  # index 1
    candidates = get_candidate_chunks(current_section, all_chunks)

    assert len(candidates) >= 1
    for chunk in candidates:
        assert all(-1 <= int(s.section_index) <= 4 for s in chunk.source_sections)
        if len(chunk.source_sections) == 1:
            idx = int(chunk.source_sections[0].section_index)
            assert idx not in [-1, 4]  # Not at boundaries


def test_get_candidate_chunks_at_boundary():
    sections = [
        Section(content="First", section_index=0),
        Section(content="Second", section_index=1),
        Section(content="Third", section_index=2),
    ]
    all_chunks = [
        Chunk(partial_content="single", source_sections=[sections[0]]),
        Chunk(partial_content="multi", source_sections=[sections[0], sections[1]]),
    ]

    candidates = get_candidate_chunks(sections[0], all_chunks)
    assert len(candidates) == 2
    assert candidates[0].partial_content == "single"
    assert candidates[1].partial_content == "multi"
