"""Tests for core.components.similarity_calculator module."""
import pytest
from unittest.mock import MagicMock, patch

from data.models import Chunk, Section, SimilarityResult
from core.components.similarity_calculator import SimilarityCalculator


@pytest.fixture
def sample_sections():
    """Create sample sections for testing."""
    return [
        Section(content="Machine learning introduction", section_index=0),
        Section(content="Deep learning concepts", section_index=1),
        Section(content="Neural network basics", section_index=2),
    ]


@pytest.fixture
def sample_chunks(sample_sections):
    """Create sample chunks for testing."""
    return [
        Chunk(partial_content="machine learning", source_sections=[sample_sections[0]]),
        Chunk(partial_content="deep learning", source_sections=[sample_sections[1]]),
        Chunk(partial_content="neural networks", source_sections=[sample_sections[2]]),
    ]


@pytest.fixture
def mock_similarity_units():
    """Mock the semantic and phonetic similarity units."""
    with patch('core.components.similarity_calculator.Semantic') as mock_semantic_class:
        with patch('core.components.similarity_calculator.Phonetic') as mock_phonetic_class:
            mock_semantic = MagicMock()
            mock_phonetic = MagicMock()
            mock_semantic_class.return_value = mock_semantic
            mock_phonetic_class.return_value = mock_phonetic
            yield mock_semantic, mock_phonetic


def test_similarity_calculator_initialization():
    """Test SimilarityCalculator initialization with default weights."""
    with patch('core.components.similarity_calculator.Semantic'):
        with patch('core.components.similarity_calculator.Phonetic'):
            calc = SimilarityCalculator()
            
            assert calc.semantic_weight == 0.6
            assert calc.phonetic_weight == 0.4
            assert calc.semantic is not None
            assert calc.phonetic is not None


def test_similarity_calculator_custom_weights():
    """Test SimilarityCalculator initialization with custom weights."""
    with patch('core.components.similarity_calculator.Semantic'):
        with patch('core.components.similarity_calculator.Phonetic'):
            calc = SimilarityCalculator(semantic_weight=0.7, phonetic_weight=0.3)
            
            assert calc.semantic_weight == 0.7
            assert calc.phonetic_weight == 0.3


def test_normalize_scores_empty_list():
    """Test _normalize_scores with empty results list."""
    with patch('core.components.similarity_calculator.Semantic'):
        with patch('core.components.similarity_calculator.Phonetic'):
            calc = SimilarityCalculator()
            
            result = calc._normalize_scores([])
            assert result == {}


def test_normalize_scores_no_valid_scores(sample_chunks):
    """Test _normalize_scores when no scores are >= 0.5."""
    with patch('core.components.similarity_calculator.Semantic'):
        with patch('core.components.similarity_calculator.Phonetic'):
            calc = SimilarityCalculator()
            
            # Create results with all scores < 0.5
            results = [
                SimilarityResult(chunk=sample_chunks[0], score=0.3),
                SimilarityResult(chunk=sample_chunks[1], score=0.2),
                SimilarityResult(chunk=sample_chunks[2], score=0.4),
            ]
            
            normalized = calc._normalize_scores(results)
            
            assert len(normalized) == 3
            assert all(score == 0.0 for score in normalized.values())


def test_normalize_scores_all_same_valid_scores(sample_chunks):
    """Test _normalize_scores when all valid scores are the same."""
    with patch('core.components.similarity_calculator.Semantic'):
        with patch('core.components.similarity_calculator.Phonetic'):
            calc = SimilarityCalculator()
            
            # Create results with same valid scores
            results = [
                SimilarityResult(chunk=sample_chunks[0], score=0.8),
                SimilarityResult(chunk=sample_chunks[1], score=0.8),
                SimilarityResult(chunk=sample_chunks[2], score=0.3),  # Below threshold
            ]
            
            normalized = calc._normalize_scores(results)
            
            # Valid scores should normalize to 1.0, invalid to 0.0
            chunk0_id = id(sample_chunks[0])
            chunk1_id = id(sample_chunks[1])
            chunk2_id = id(sample_chunks[2])
            
            assert normalized[chunk0_id] == 1.0
            assert normalized[chunk1_id] == 1.0
            assert normalized[chunk2_id] == 0.0


def test_normalize_scores_different_valid_scores(sample_chunks):
    """Test _normalize_scores with different valid scores."""
    with patch('core.components.similarity_calculator.Semantic'):
        with patch('core.components.similarity_calculator.Phonetic'):
            calc = SimilarityCalculator()
            
            # Create results with different valid scores
            results = [
                SimilarityResult(chunk=sample_chunks[0], score=0.9),  # max
                SimilarityResult(chunk=sample_chunks[1], score=0.5),  # min valid
                SimilarityResult(chunk=sample_chunks[2], score=0.7),  # middle
            ]
            
            normalized = calc._normalize_scores(results)
            
            chunk0_id = id(sample_chunks[0])
            chunk1_id = id(sample_chunks[1])
            chunk2_id = id(sample_chunks[2])
            
            # Should normalize between 0 and 1 based on range
            assert normalized[chunk0_id] == 1.0  # (0.9 - 0.5) / (0.9 - 0.5)
            assert normalized[chunk1_id] == 0.0  # (0.5 - 0.5) / (0.9 - 0.5)
            assert normalized[chunk2_id] == 0.5  # (0.7 - 0.5) / (0.9 - 0.5)


def test_compare_empty_candidates(mock_similarity_units):
    """Test compare method with empty candidates list."""
    mock_semantic, mock_phonetic = mock_similarity_units
    calc = SimilarityCalculator()
    
    result = calc.compare("test input", [])
    assert result == []


def test_compare_single_candidate(mock_similarity_units, sample_chunks):
    """Test compare method with single candidate."""
    mock_semantic, mock_phonetic = mock_similarity_units
    
    # Setup mock returns
    mock_semantic.compare.return_value = [
        SimilarityResult(chunk=sample_chunks[0], score=0.8)
    ]
    mock_phonetic.compare.return_value = [
        SimilarityResult(chunk=sample_chunks[0], score=0.7)
    ]
    
    calc = SimilarityCalculator()
    result = calc.compare("machine", [sample_chunks[0]])
    
    assert len(result) == 1
    assert isinstance(result[0], SimilarityResult)
    assert result[0].chunk == sample_chunks[0]
    # Score should be weighted average of normalized scores
    # Both scores are >= 0.5 and same, so normalized to 1.0 each
    # Final: 0.6 * 1.0 + 0.4 * 1.0 = 1.0
    assert result[0].score == 1.0


def test_compare_multiple_candidates_weighted_scoring(mock_similarity_units, sample_chunks):
    """Test compare method with multiple candidates and proper weighted scoring."""
    mock_semantic, mock_phonetic = mock_similarity_units
    
    # Setup semantic results (higher scores)
    mock_semantic.compare.return_value = [
        SimilarityResult(chunk=sample_chunks[0], score=0.9),  # machine learning
        SimilarityResult(chunk=sample_chunks[1], score=0.6),  # deep learning  
        SimilarityResult(chunk=sample_chunks[2], score=0.5),  # neural networks
    ]
    
    # Setup phonetic results (different scores)
    mock_phonetic.compare.return_value = [
        SimilarityResult(chunk=sample_chunks[0], score=0.5),  # machine learning
        SimilarityResult(chunk=sample_chunks[1], score=0.8),  # deep learning
        SimilarityResult(chunk=sample_chunks[2], score=0.7),  # neural networks
    ]
    
    calc = SimilarityCalculator(semantic_weight=0.6, phonetic_weight=0.4)
    result = calc.compare("learning", sample_chunks)
    
    assert len(result) == 3
    # Should be sorted by final weighted score (highest first)
    assert result[0].chunk == sample_chunks[1]  # Should have highest combined score
    assert result[1].chunk == sample_chunks[0]
    assert result[2].chunk == sample_chunks[2]


def test_compare_calls_both_similarity_units(mock_similarity_units, sample_chunks):
    """Test compare method calls both semantic and phonetic units."""
    mock_semantic, mock_phonetic = mock_similarity_units
    
    mock_semantic.compare.return_value = [
        SimilarityResult(chunk=sample_chunks[0], score=0.8)
    ]
    mock_phonetic.compare.return_value = [
        SimilarityResult(chunk=sample_chunks[0], score=0.7)
    ]
    
    calc = SimilarityCalculator()
    input_text = "test input"
    
    calc.compare(input_text, sample_chunks)
    
    # Verify both units were called with correct parameters
    mock_semantic.compare.assert_called_once_with(input_text, sample_chunks)
    mock_phonetic.compare.assert_called_once_with(input_text, sample_chunks)


def test_compare_exception_handling(mock_similarity_units, sample_chunks):
    """Test compare method handles exceptions properly."""
    mock_semantic, mock_phonetic = mock_similarity_units
    
    # Make semantic comparison raise an exception
    mock_semantic.compare.side_effect = Exception("Semantic error")
    
    calc = SimilarityCalculator()
    
    with pytest.raises(RuntimeError) as exc_info:
        calc.compare("test", sample_chunks)
    
    assert "Similarity comparison failed" in str(exc_info.value)
    assert "Semantic error" in str(exc_info.value)


@pytest.mark.parametrize("semantic_weight,phonetic_weight", [
    (1.0, 0.0),  # Only semantic
    (0.0, 1.0),  # Only phonetic
    (0.5, 0.5),  # Equal weights
    (0.8, 0.2),  # Heavy semantic
    (0.3, 0.7),  # Heavy phonetic
])
def test_compare_different_weight_combinations(mock_similarity_units, sample_chunks, semantic_weight, phonetic_weight):
    """Test compare method with different weight combinations."""
    mock_semantic, mock_phonetic = mock_similarity_units
    
    mock_semantic.compare.return_value = [
        SimilarityResult(chunk=sample_chunks[0], score=0.9)
    ]
    mock_phonetic.compare.return_value = [
        SimilarityResult(chunk=sample_chunks[0], score=0.5)
    ]
    
    calc = SimilarityCalculator(semantic_weight=semantic_weight, phonetic_weight=phonetic_weight)
    result = calc.compare("test", [sample_chunks[0]])
    
    assert len(result) == 1
    # Since both scores are valid and same chunk, normalized scores are 1.0 each
    expected_score = semantic_weight * 1.0 + phonetic_weight * 1.0
    assert result[0].score == expected_score


def test_normalize_scores_mixed_valid_invalid(sample_chunks):
    """Test _normalize_scores with mix of valid and invalid scores."""
    with patch('core.components.similarity_calculator.Semantic'):
        with patch('core.components.similarity_calculator.Phonetic'):
            calc = SimilarityCalculator()
            
            results = [
                SimilarityResult(chunk=sample_chunks[0], score=0.9),   # valid
                SimilarityResult(chunk=sample_chunks[1], score=0.3),   # invalid
                SimilarityResult(chunk=sample_chunks[2], score=0.6),   # valid
            ]
            
            normalized = calc._normalize_scores(results)
            
            chunk0_id = id(sample_chunks[0])
            chunk1_id = id(sample_chunks[1])
            chunk2_id = id(sample_chunks[2])
            
            # Valid scores: 0.9 (max), 0.6 (min valid)
            # Normalized: (0.9-0.6)/(0.9-0.6) = 1.0, (0.6-0.6)/(0.9-0.6) = 0.0
            assert normalized[chunk0_id] == 1.0
            assert normalized[chunk1_id] == 0.0  # Invalid score
            assert normalized[chunk2_id] == 0.0  # Min valid score


def test_similarity_calculator_preserves_chunk_references(mock_similarity_units, sample_chunks):
    """Test that SimilarityCalculator preserves original chunk references."""
    mock_semantic, mock_phonetic = mock_similarity_units
    
    mock_semantic.compare.return_value = [
        SimilarityResult(chunk=sample_chunks[0], score=0.8),
        SimilarityResult(chunk=sample_chunks[1], score=0.7),
    ]
    mock_phonetic.compare.return_value = [
        SimilarityResult(chunk=sample_chunks[0], score=0.6),
        SimilarityResult(chunk=sample_chunks[1], score=0.5),
    ]
    
    calc = SimilarityCalculator()
    result = calc.compare("test", sample_chunks[:2])
    
    # Verify that the exact same chunk objects are returned
    result_chunks = [r.chunk for r in result]
    assert sample_chunks[0] in result_chunks
    assert sample_chunks[1] in result_chunks
    
    # Verify identity (not just equality)
    for r in result:
        assert r.chunk in sample_chunks[:2]