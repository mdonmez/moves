import pytest
from unittest.mock import patch
from data.models import Chunk, SimilarityResult
from core.components.similarity_units.phonetic import Phonetic


class TestPhonetic:
    def test_get_phonetic_code(self):
        phonetic = Phonetic()
        code = phonetic._get_phonetic_code("test")
        assert isinstance(code, str)
        assert len(code) > 0

    def test_calculate_fuzz_ratio(self):
        phonetic = Phonetic()
        ratio = phonetic._calculate_fuzz_ratio("test", "test")
        assert isinstance(ratio, float)
        assert 0.0 <= ratio <= 1.0

    def test_compare_empty_candidates(self):
        phonetic = Phonetic()
        results = phonetic.compare("input", [])
        assert results == []

    @patch("core.components.similarity_units.phonetic.metaphone")
    @patch("core.components.similarity_units.phonetic.fuzz")
    def test_compare_with_candidates(self, mock_fuzz, mock_metaphone):
        # Mock metaphone
        mock_metaphone.return_value = "TST"

        # Mock fuzz ratio
        mock_fuzz.ratio.return_value = 80.0

        phonetic = Phonetic()
        chunk1 = Chunk("content1", [])
        chunk2 = Chunk("content2", [])

        results = phonetic.compare("input text", [chunk1, chunk2])

        assert len(results) == 2
        assert all(isinstance(r, SimilarityResult) for r in results)
        assert all(0.0 <= r.score <= 1.0 for r in results)

        # Results should be sorted by score descending
        assert results[0].score >= results[1].score

    @patch("core.components.similarity_units.phonetic.metaphone")
    def test_compare_exception_handling(self, mock_metaphone):
        mock_metaphone.side_effect = Exception("Metaphone error")

        phonetic = Phonetic()
        chunk = Chunk("content", [])

        with pytest.raises(RuntimeError, match="Phonetic similarity comparison failed"):
            phonetic.compare("input", [chunk])

    def test_caching(self):
        phonetic = Phonetic()

        # Call the same text multiple times
        code1 = phonetic._get_phonetic_code("test text")
        code2 = phonetic._get_phonetic_code("test text")

        assert code1 == code2

        # Verify caching by checking that metaphone is only called once
        with patch("core.components.similarity_units.phonetic.metaphone") as mock_meta:
            mock_meta.return_value = "TST"
            phonetic._get_phonetic_code("new text")
            phonetic._get_phonetic_code("new text")
            # Should only be called once due to caching
            assert mock_meta.call_count == 1
