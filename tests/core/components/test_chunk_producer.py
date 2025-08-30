from data.models import Section, Chunk
from core.components.chunk_producer import generate_chunks, get_candidate_chunks


class TestChunkProducer:
    def test_generate_chunks_empty_sections(self):
        result = generate_chunks([])
        assert result == []

    def test_generate_chunks_insufficient_words(self):
        sections = [Section("Short text", 0)]
        result = generate_chunks(sections, window_size=5)
        assert result == []

    def test_generate_chunks_basic(self):
        sections = [
            Section("This is a test section with enough words", 0),
            Section("Another section with more content here", 1),
        ]
        result = generate_chunks(sections, window_size=3)
        assert len(result) > 0
        assert all(isinstance(chunk, Chunk) for chunk in result)

    def test_generate_chunks_window_size(self):
        sections = [Section("word1 word2 word3 word4 word5", 0)]
        result = generate_chunks(sections, window_size=3)
        assert len(result) == 3

    def test_get_candidate_chunks(self):
        sections = [Section("content", i) for i in range(10)]
        chunks = [Chunk("chunk content", [sections[i]]) for i in range(10)]
        current_section = sections[5]
        candidates = get_candidate_chunks(current_section, chunks)
        expected_indices = {4, 5, 6, 7}
        actual_indices = {
            chunk.source_sections[0].section_index for chunk in candidates
        }
        assert actual_indices == expected_indices

    def test_get_candidate_chunks_edge_cases(self):
        sections = [Section("content", i) for i in range(3)]
        chunks = [Chunk("chunk content", [sections[i]]) for i in range(3)]
        current_section = sections[0]
        candidates = get_candidate_chunks(current_section, chunks)
        assert len(candidates) >= 1
        current_section = sections[2]
        candidates = get_candidate_chunks(current_section, chunks)
        assert len(candidates) >= 1
