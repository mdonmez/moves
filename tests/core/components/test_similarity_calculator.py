import pytest
from unittest.mock import MagicMock, patch
from data.models import Chunk, SimilarityResult
from core.components.similarity_calculator import SimilarityCalculator


class TestSimilarityCalculator:
    def test_similarity_calculator_init(self):
        calculator = SimilarityCalculator()
        assert calculator.semantic_weight == 0.6
        assert calculator.phonetic_weight == 0.4
        assert calculator.semantic is not None
        assert calculator.phonetic is not None

    def test_similarity_calculator_custom_weights(self):
        calculator = SimilarityCalculator(semantic_weight=0.7, phonetic_weight=0.3)
        assert calculator.semantic_weight == 0.7
        assert calculator.phonetic_weight == 0.3

    @pytest.mark.parametrize(
        "results,expected",
        [
            ([], {}),
            (
                [
                    SimilarityResult(Chunk("content1", []), 0.3),
                    SimilarityResult(Chunk("content2", []), 0.4),
                ],
                {0: 0.0, 1: 0.0},
            ),
            ([SimilarityResult(Chunk("content", []), 0.8)], {2: 1.0}),
            (
                [
                    SimilarityResult(Chunk("content1", []), 0.6),
                    SimilarityResult(Chunk("content2", []), 0.8),
                ],
                {3: 0.0, 4: 1.0},
            ),
        ],
    )
    def test_normalize_scores(self, results, expected):
        calculator = SimilarityCalculator()
        normalized = calculator._normalize_scores(results)
        for key, value in expected.items():
            if key in normalized:
                assert normalized[key] == value

    @patch("core.components.similarity_calculator.Semantic")
    @patch("core.components.similarity_calculator.Phonetic")
    def test_compare_empty_candidates(self, mock_phonetic, mock_semantic):
        calculator = SimilarityCalculator()
        results = calculator.compare("input", [])
        assert results == []

    @patch("core.components.similarity_calculator.Semantic")
    @patch("core.components.similarity_calculator.Phonetic")
    def test_compare_with_candidates(self, mock_phonetic, mock_semantic):
        mock_semantic_instance = MagicMock()
        mock_phonetic_instance = MagicMock()
        mock_semantic.return_value = mock_semantic_instance
        mock_phonetic.return_value = mock_phonetic_instance
        chunk1 = Chunk("content1", [])
        chunk2 = Chunk("content2", [])
        mock_semantic_instance.compare.return_value = [
            SimilarityResult(chunk1, 0.8),
            SimilarityResult(chunk2, 0.6),
        ]
        mock_phonetic_instance.compare.return_value = [
            SimilarityResult(chunk1, 0.7),
            SimilarityResult(chunk2, 0.9),
        ]
        calculator = SimilarityCalculator(semantic_weight=0.5, phonetic_weight=0.5)
        results = calculator.compare("input text", [chunk1, chunk2])
        assert len(results) == 2
        assert results[0].score >= results[1].score

    @patch("core.components.similarity_calculator.Semantic")
    @patch("core.components.similarity_calculator.Phonetic")
    def test_compare_exception_handling(self, mock_phonetic, mock_semantic):
        mock_semantic_instance = MagicMock()
        mock_semantic.return_value = mock_semantic_instance
        mock_semantic_instance.compare.side_effect = Exception("Semantic error")
        calculator = SimilarityCalculator()
        chunk = Chunk("content", [])
        with pytest.raises(RuntimeError, match="Similarity comparison failed"):
            calculator.compare("input", [chunk])
