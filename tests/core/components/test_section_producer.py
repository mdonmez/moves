"""Tests for core.components.section_producer module."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from data.models import Section
from core.components import section_producer


def test_convert_to_list():
    """Test convert_to_list converts Section objects to dictionaries."""
    sections = [
        Section(content="Introduction", section_index=0),
        Section(content="Overview", section_index=1),
        Section(content="Conclusion", section_index=2),
    ]
    
    result = section_producer.convert_to_list(sections)
    
    expected = [
        {"content": "Introduction", "section_index": 0},
        {"content": "Overview", "section_index": 1},
        {"content": "Conclusion", "section_index": 2},
    ]
    
    assert result == expected
    assert all(isinstance(item, dict) for item in result)
    assert all("content" in item and "section_index" in item for item in result)


def test_convert_to_list_empty():
    """Test convert_to_list handles empty section lists."""
    result = section_producer.convert_to_list([])
    assert result == []


def test_convert_to_objects():
    """Test convert_to_objects converts dictionaries to Section objects."""
    section_dicts = [
        {"content": "Introduction", "section_index": 0},
        {"content": "Overview", "section_index": 1},
        {"content": "Conclusion", "section_index": 2},
    ]
    
    result = section_producer.convert_to_objects(section_dicts)
    
    assert len(result) == 3
    assert all(isinstance(section, Section) for section in result)
    
    assert result[0].content == "Introduction"
    assert result[0].section_index == 0
    assert result[1].content == "Overview"
    assert result[1].section_index == 1
    assert result[2].content == "Conclusion"
    assert result[2].section_index == 2


def test_convert_to_objects_empty():
    """Test convert_to_objects handles empty dictionary lists."""
    result = section_producer.convert_to_objects([])
    assert result == []


def test_round_trip_conversion():
    """Test that converting to list and back preserves data."""
    original_sections = [
        Section(content="Test content 1", section_index=0),
        Section(content="Test content 2", section_index=5),
        Section(content="", section_index=10),  # Edge case: empty content
    ]
    
    # Convert to list and back
    as_list = section_producer.convert_to_list(original_sections)
    back_to_objects = section_producer.convert_to_objects(as_list)
    
    # Should be identical
    assert len(back_to_objects) == len(original_sections)
    for original, converted in zip(original_sections, back_to_objects):
        assert original.content == converted.content
        assert original.section_index == converted.section_index
        assert original == converted


@pytest.mark.parametrize("content,index", [
    ("Simple content", 0),
    ("Content with special chars: @#$%", 1),
    ("Multi-line\ncontent\ntest", 2),
    ("Unicode content: café naïve résumé", 3),
    ("", 4),  # Empty content
    ("Very long content " * 100, 5),  # Long content
])
def test_conversion_with_various_content(content, index):
    """Test conversions handle various content types."""
    section = Section(content=content, section_index=index)
    
    # Convert to list
    as_list = section_producer.convert_to_list([section])
    assert len(as_list) == 1
    assert as_list[0]["content"] == content
    assert as_list[0]["section_index"] == index
    
    # Convert back to object
    back_to_object = section_producer.convert_to_objects(as_list)
    assert len(back_to_object) == 1
    assert back_to_object[0].content == content
    assert back_to_object[0].section_index == index


def test_convert_to_objects_type_casting():
    """Test convert_to_objects properly casts types."""
    # Test with string index (should be cast to int)
    section_dict = {"content": "Test", "section_index": "5"}
    
    result = section_producer.convert_to_objects([section_dict])
    
    assert len(result) == 1
    assert isinstance(result[0].section_index, int)
    assert result[0].section_index == 5


def test_extract_pdf_mocked():
    """Test _extract_pdf function behavior with mocking."""
    mock_pdf_path = Path("/mock/path.pdf")
    
    with patch('core.components.section_producer.pymupdf') as mock_pymupdf:
        # Mock the pymupdf.open behavior
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Mocked PDF text content"
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_pymupdf.open.return_value.__enter__ = MagicMock(return_value=mock_doc)
        mock_pymupdf.open.return_value.__exit__ = MagicMock(return_value=None)
        
        result = section_producer._extract_pdf(mock_pdf_path, "presentation")
        
        mock_pymupdf.open.assert_called_once_with(mock_pdf_path)
        assert result == "Mocked PDF text content"


def test_call_llm_mocked():
    """Test _call_llm function behavior with mocking."""
    presentation_data = "Slide 1: Introduction\nSlide 2: Content"
    transcript_data = "Hello everyone, today we will talk about..."
    model = "gpt-4"
    api_key = "test-key"
    
    with patch('core.components.section_producer.instructor') as mock_instructor:
        with patch('core.components.section_producer.completion') as mock_completion:
            # Mock the instructor and completion behavior
            mock_response = MagicMock()
            mock_response.sections = [
                MagicMock(content="Section 1 content", section_index=0),
                MagicMock(content="Section 2 content", section_index=1),
            ]
            mock_completion.return_value = mock_response
            
            result = section_producer._call_llm(
                presentation_data, transcript_data, model, api_key
            )
            
            assert len(result) == 2
            assert result[0] == "Section 1 content"
            assert result[1] == "Section 2 content"


def test_generate_sections_integration_mocked():
    """Test generate_sections function with full mocking."""
    presentation_path = Path("/mock/presentation.pdf")
    transcript_path = Path("/mock/transcript.pdf")
    model = "gpt-4"
    api_key = "test-api-key"
    
    with patch.object(section_producer, '_extract_pdf') as mock_extract:
        with patch.object(section_producer, '_call_llm') as mock_call_llm:
            # Setup mocks
            mock_extract.side_effect = [
                "Presentation content from PDF",
                "Transcript content from PDF"
            ]
            mock_call_llm.return_value = [
                "First section content",
                "Second section content",
                "Third section content"
            ]
            
            result = section_producer.generate_sections(
                presentation_path, transcript_path, model, api_key
            )
            
            # Verify extract_pdf calls
            assert mock_extract.call_count == 2
            mock_extract.assert_any_call(presentation_path, "presentation")
            mock_extract.assert_any_call(transcript_path, "transcript")
            
            # Verify call_llm call
            mock_call_llm.assert_called_once_with(
                presentation_data="Presentation content from PDF",
                transcript_data="Transcript content from PDF",
                llm_model=model,
                llm_api_key=api_key
            )
            
            # Verify result
            assert len(result) == 3
            assert all(isinstance(section, Section) for section in result)
            assert result[0].content == "First section content"
            assert result[0].section_index == 0
            assert result[1].content == "Second section content"
            assert result[1].section_index == 1
            assert result[2].content == "Third section content"
            assert result[2].section_index == 2


def test_generate_sections_empty_llm_response():
    """Test generate_sections handles empty LLM response."""
    presentation_path = Path("/mock/presentation.pdf")
    transcript_path = Path("/mock/transcript.pdf")
    
    with patch.object(section_producer, '_extract_pdf') as mock_extract:
        with patch.object(section_producer, '_call_llm') as mock_call_llm:
            mock_extract.side_effect = ["Presentation", "Transcript"]
            mock_call_llm.return_value = []  # Empty response
            
            result = section_producer.generate_sections(
                presentation_path, transcript_path, "gpt-4", "key"
            )
            
            assert result == []


def test_convert_functions_handle_mixed_types():
    """Test conversion functions handle mixed data types properly."""
    # Test convert_to_list with sections having different content types
    sections = [
        Section(content="String content", section_index=0),
        Section(content="123", section_index=1),  # Numeric as string
        Section(content="", section_index=2),  # Empty
    ]
    
    as_list = section_producer.convert_to_list(sections)
    back_to_objects = section_producer.convert_to_objects(as_list)
    
    assert len(back_to_objects) == 3
    assert back_to_objects[0].content == "String content"
    assert back_to_objects[1].content == "123"
    assert back_to_objects[2].content == ""


def test_section_indexing_consistency():
    """Test that section indexing is preserved correctly."""
    # Test with non-sequential indices
    sections = [
        Section(content="First", section_index=5),
        Section(content="Second", section_index=1),
        Section(content="Third", section_index=10),
    ]
    
    as_list = section_producer.convert_to_list(sections)
    back_to_objects = section_producer.convert_to_objects(as_list)
    
    # Indices should be preserved exactly
    assert back_to_objects[0].section_index == 5
    assert back_to_objects[1].section_index == 1
    assert back_to_objects[2].section_index == 10


@pytest.mark.parametrize("extraction_type", ["presentation", "transcript"])
def test_extract_pdf_extraction_types(extraction_type):
    """Test _extract_pdf handles different extraction types."""
    mock_path = Path(f"/mock/{extraction_type}.pdf")
    
    with patch('core.components.section_producer.pymupdf') as mock_pymupdf:
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = f"Content for {extraction_type}"
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_pymupdf.open.return_value.__enter__ = MagicMock(return_value=mock_doc)
        mock_pymupdf.open.return_value.__exit__ = MagicMock(return_value=None)
        
        result = section_producer._extract_pdf(mock_path, extraction_type)
        
        assert result == f"Content for {extraction_type}"