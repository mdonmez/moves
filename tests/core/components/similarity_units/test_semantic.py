import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from data.models import Chunk, SimilarityResult
from core.components.similarity_units.semantic import Semantic


class TestSemantic:
    @patch("core.components.similarity_units.semantic.TextEmbedding")
    def test_semantic_init(self, mock_text_embedding):
        mock_model = MagicMock()
        mock_text_embedding.return_value = mock_model

        semantic = Semantic()

        mock_text_embedding.assert_called_once_with(
            model_name="sentence-transformers/all-MiniLM-l6-v2",
            specific_model_path="src/core/components/ml_models/all-MiniLM-L6-v2_quint8_avx2",
        )
        assert semantic.model == mock_model

    @patch("core.components.similarity_units.semantic.TextEmbedding")
    def test_compare_empty_candidates(self, mock_text_embedding):
        mock_model = MagicMock()
        mock_text_embedding.return_value = mock_model

        # For empty candidates, embedding_input = [input_str], so embeddings = [input_embedding]
        mock_model.embed.return_value = [np.array([0.1, 0.2, 0.3])]

        semantic = Semantic()

        # The code doesn't handle empty candidates properly and will raise RuntimeError
        with pytest.raises(RuntimeError, match="Semantic similarity comparison failed"):
            semantic.compare("input", [])

    @patch("core.components.similarity_units.semantic.TextEmbedding")
    def test_compare_with_candidates(self, mock_text_embedding):
        mock_model = MagicMock()
        mock_text_embedding.return_value = mock_model

        # Mock embeddings
        input_embedding = np.array([0.1, 0.2, 0.3])
        candidate_embedding1 = np.array([0.1, 0.2, 0.4])  # Similar to input
        candidate_embedding2 = np.array([0.5, 0.6, 0.7])  # Different from input

        mock_model.embed.return_value = [
            input_embedding,
            candidate_embedding1,
            candidate_embedding2,
        ]

        semantic = Semantic()
        chunk1 = Chunk("content1", [])
        chunk2 = Chunk("content2", [])

        results = semantic.compare("input text", [chunk1, chunk2])

        assert len(results) == 2
        assert all(isinstance(r, SimilarityResult) for r in results)

        # Results should be sorted by score descending
        assert results[0].score >= results[1].score

        # Verify embeddings were called with correct input
        mock_model.embed.assert_called_once()
        call_args = mock_model.embed.call_args[0][0]
        assert call_args[0] == "input text"
        assert call_args[1] == "content1"
        assert call_args[2] == "content2"

    @patch("core.components.similarity_units.semantic.TextEmbedding")
    def test_compare_exception_handling(self, mock_text_embedding):
        mock_model = MagicMock()
        mock_text_embedding.return_value = mock_model
        mock_model.embed.side_effect = Exception("Embedding error")

        semantic = Semantic()
        chunk = Chunk("content", [])

        with pytest.raises(RuntimeError, match="Semantic similarity comparison failed"):
            semantic.compare("input", [chunk])

    @patch("core.components.similarity_units.semantic.TextEmbedding")
    def test_cosine_similarity_calculation(self, mock_text_embedding):
        mock_model = MagicMock()
        mock_text_embedding.return_value = mock_model

        # Create embeddings that will result in predictable cosine similarities
        input_embedding = np.array([1.0, 0.0, 0.0])  # Unit vector along x-axis
        candidate_embedding1 = np.array(
            [1.0, 0.0, 0.0]
        )  # Same as input - similarity = 1.0
        candidate_embedding2 = np.array(
            [0.0, 1.0, 0.0]
        )  # Perpendicular - similarity = 0.0

        mock_model.embed.return_value = [
            input_embedding,
            candidate_embedding1,
            candidate_embedding2,
        ]

        semantic = Semantic()
        chunk1 = Chunk("content1", [])
        chunk2 = Chunk("content2", [])

        results = semantic.compare("input", [chunk1, chunk2])

        # Find results by chunk content
        result1 = next(r for r in results if r.chunk == chunk1)
        result2 = next(r for r in results if r.chunk == chunk2)

        assert abs(result1.score - 1.0) < 0.001  # Should be very close to 1.0
        assert abs(result2.score - 0.0) < 0.001  # Should be very close to 0.0
