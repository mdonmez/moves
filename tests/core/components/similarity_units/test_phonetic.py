"""Tests for core.components.similarity_units.phonetic module."""
import pytest
from unittest.mock import patch, MagicMock

from data.models import Chunk, Section, SimilarityResult
from core.components.similarity_units.phonetic import Phonetic


@pytest.fixture
def sample_sections():
    """Create sample sections for testing."""
    return [
        Section(content="Introduction to machine learning", section_index=0),
        Section(content="Deep learning fundamentals", section_index=1),
        Section(content="Neural network architectures", section_index=2),
    ]


@pytest.fixture
def sample_chunks(sample_sections):
    """Create sample chunks for testing."""
    return [
        Chunk(partial_content="machine learning", source_sections=[sample_sections[0]]),
        Chunk(partial_content="deep learning", source_sections=[sample_sections[1]]),
        Chunk(partial_content="neural networks", source_sections=[sample_sections[2]]),
    ]


def test_phonetic_get_phonetic_code_basic():
    """Test _get_phonetic_code method with basic strings."""
    with patch('core.components.similarity_units.phonetic.metaphone') as mock_metaphone:
        mock_metaphone.return_value = "MSHN LRNK"
        
        result = Phonetic._get_phonetic_code("machine learning")
        
        mock_metaphone.assert_called_once_with("machine learning")
        assert result == "MSHNLRNK"  # Spaces should be removed


def test_phonetic_get_phonetic_code_removes_spaces():
    """Test _get_phonetic_code removes all spaces from metaphone result."""
    with patch('core.components.similarity_units.phonetic.metaphone') as mock_metaphone:
        mock_metaphone.return_value = "A B C D"
        
        result = Phonetic._get_phonetic_code("test")
        
        assert result == "ABCD"
        assert " " not in result


def test_phonetic_get_phonetic_code_caching():
    """Test _get_phonetic_code uses LRU caching."""
    with patch('core.components.similarity_units.phonetic.metaphone') as mock_metaphone:
        mock_metaphone.return_value = "TST"
        
        # Clear cache first
        Phonetic._get_phonetic_code.cache_clear()
        
        # Call twice with same input
        result1 = Phonetic._get_phonetic_code("test")
        result2 = Phonetic._get_phonetic_code("test")
        
        # Should only call metaphone once due to caching
        assert mock_metaphone.call_count == 1
        assert result1 == result2 == "TST"


def test_phonetic_calculate_fuzz_ratio_basic():
    """Test _calculate_fuzz_ratio method."""
    with patch('core.components.similarity_units.phonetic.fuzz.ratio') as mock_ratio:
        mock_ratio.return_value = 85
        
        result = Phonetic._calculate_fuzz_ratio("MSHN", "MSHN")
        
        mock_ratio.assert_called_once_with("MSHN", "MSHN")
        assert result == 0.85  # Should convert from 0-100 to 0-1 scale


def test_phonetic_calculate_fuzz_ratio_caching():
    """Test _calculate_fuzz_ratio uses LRU caching."""
    with patch('core.components.similarity_units.phonetic.fuzz.ratio') as mock_ratio:
        mock_ratio.return_value = 90
        
        # Clear cache first
        Phonetic._calculate_fuzz_ratio.cache_clear()
        
        # Call twice with same inputs
        result1 = Phonetic._calculate_fuzz_ratio("ABC", "ABD")
        result2 = Phonetic._calculate_fuzz_ratio("ABC", "ABD")
        
        # Should only call fuzz.ratio once due to caching
        assert mock_ratio.call_count == 1
        assert result1 == result2 == 0.9


@pytest.mark.parametrize("fuzz_score,expected_result", [
    (100, 1.0),
    (85, 0.85),
    (50, 0.5),
    (0, 0.0),
])
def test_phonetic_calculate_fuzz_ratio_conversion(fuzz_score, expected_result):
    """Test _calculate_fuzz_ratio converts scores correctly."""
    with patch('core.components.similarity_units.phonetic.fuzz.ratio') as mock_ratio:
        mock_ratio.return_value = fuzz_score
        
        result = Phonetic._calculate_fuzz_ratio("test1", "test2")
        assert result == expected_result


def test_phonetic_compare_empty_candidates():
    """Test compare method with empty candidates list."""
    phonetic = Phonetic()
    
    result = phonetic.compare("test input", [])
    
    assert result == []


def test_phonetic_compare_single_candidate(sample_chunks):
    """Test compare method with single candidate."""
    phonetic = Phonetic()
    
    with patch.object(Phonetic, '_get_phonetic_code') as mock_get_code:
        with patch.object(Phonetic, '_calculate_fuzz_ratio') as mock_fuzz:
            mock_get_code.side_effect = ["MSHN", "MSHNLRNK"]
            mock_fuzz.return_value = 0.85
            
            result = phonetic.compare("machine", [sample_chunks[0]])
            
            assert len(result) == 1
            assert isinstance(result[0], SimilarityResult)
            assert result[0].chunk == sample_chunks[0]
            assert result[0].score == 0.85


def test_phonetic_compare_multiple_candidates(sample_chunks):
    """Test compare method with multiple candidates and sorting."""
    phonetic = Phonetic()
    
    with patch.object(Phonetic, '_get_phonetic_code') as mock_get_code:
        with patch.object(Phonetic, '_calculate_fuzz_ratio') as mock_fuzz:
            # Mock phonetic codes for input and candidates
            mock_get_code.side_effect = ["LRNK", "MSHNLRNK", "TPLRNK", "NRLNTWRKS"]
            # Mock similarity scores: high for deep learning, medium for machine learning, low for neural
            mock_fuzz.side_effect = [0.6, 0.9, 0.3]
            
            result = phonetic.compare("learning", sample_chunks)
            
            assert len(result) == 3
            # Should be sorted by score (highest first)
            assert result[0].score == 0.9  # deep learning
            assert result[1].score == 0.6  # machine learning  
            assert result[2].score == 0.3  # neural networks
            
            # Verify chunks are correctly associated
            assert result[0].chunk == sample_chunks[1]  # deep learning
            assert result[1].chunk == sample_chunks[0]  # machine learning
            assert result[2].chunk == sample_chunks[2]  # neural networks


def test_phonetic_compare_identical_scores(sample_chunks):
    """Test compare method maintains order when scores are identical."""
    phonetic = Phonetic()
    
    with patch.object(Phonetic, '_get_phonetic_code') as mock_get_code:
        with patch.object(Phonetic, '_calculate_fuzz_ratio') as mock_fuzz:
            mock_get_code.side_effect = ["TST", "TST1", "TST2", "TST3"]
            mock_fuzz.side_effect = [0.5, 0.5, 0.5]  # All same score
            
            result = phonetic.compare("test", sample_chunks)
            
            assert len(result) == 3
            assert all(r.score == 0.5 for r in result)
            # Original order should be maintained for equal scores
            assert result[0].chunk == sample_chunks[0]
            assert result[1].chunk == sample_chunks[1]
            assert result[2].chunk == sample_chunks[2]


def test_phonetic_compare_exception_handling():
    """Test compare method handles exceptions properly."""
    phonetic = Phonetic()
    
    with patch.object(Phonetic, '_get_phonetic_code', side_effect=Exception("Mock error")):
        with pytest.raises(RuntimeError) as exc_info:
            phonetic.compare("test", [])
        
        assert "Phonetic similarity comparison failed" in str(exc_info.value)
        assert "Mock error" in str(exc_info.value)


def test_phonetic_integration_with_actual_metaphone():
    """Test phonetic comparison with actual metaphone (integration test)."""
    phonetic = Phonetic()
    
    # Create chunks with phonetically similar words
    sections = [Section(content="Test", section_index=i) for i in range(3)]
    chunks = [
        Chunk(partial_content="cat", source_sections=[sections[0]]),
        Chunk(partial_content="bat", source_sections=[sections[1]]),
        Chunk(partial_content="dog", source_sections=[sections[2]]),
    ]
    
    result = phonetic.compare("cat", chunks)
    
    assert len(result) == 3
    # "cat" should be most similar to itself
    assert result[0].chunk.partial_content == "cat"
    assert result[0].score > result[1].score
    assert result[0].score > result[2].score


def test_phonetic_cache_size_limits():
    """Test that LRU cache respects size limits."""
    # Clear caches first
    Phonetic._get_phonetic_code.cache_clear()
    Phonetic._calculate_fuzz_ratio.cache_clear()
    
    # Verify cache info is available
    assert hasattr(Phonetic._get_phonetic_code, 'cache_info')
    assert hasattr(Phonetic._calculate_fuzz_ratio, 'cache_info')
    
    # Check initial cache state
    assert Phonetic._get_phonetic_code.cache_info().currsize == 0
    assert Phonetic._calculate_fuzz_ratio.cache_info().currsize == 0


def test_phonetic_handles_unicode_text():
    """Test phonetic comparison handles unicode text properly."""
    phonetic = Phonetic()
    
    sections = [Section(content="Unicode test", section_index=0)]
    chunks = [Chunk(partial_content="café naïve", source_sections=sections)]
    
    # Should not raise an exception
    result = phonetic.compare("cafe naive", chunks)
    
    assert len(result) == 1
    assert isinstance(result[0], SimilarityResult)


def test_phonetic_handles_empty_strings():
    """Test phonetic comparison handles empty strings gracefully."""
    phonetic = Phonetic()
    
    sections = [Section(content="Empty test", section_index=0)]
    chunks = [Chunk(partial_content="", source_sections=sections)]
    
    result = phonetic.compare("", chunks)
    
    assert len(result) == 1
    assert isinstance(result[0], SimilarityResult)


def test_phonetic_method_signatures():
    """Test that phonetic methods have expected signatures."""
    # Test static method decorators
    assert hasattr(Phonetic._get_phonetic_code, '__wrapped__')  # LRU cache decorator
    assert hasattr(Phonetic._calculate_fuzz_ratio, '__wrapped__')  # LRU cache decorator
    
    # Test method existence
    assert hasattr(Phonetic, 'compare')
    assert callable(getattr(Phonetic, 'compare'))