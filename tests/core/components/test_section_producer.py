import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.components.section_producer import _extract_pdf


class TestSectionProducer:
    @patch("core.components.section_producer.pymupdf")
    def test_extract_pdf_transcript(self, mock_pymupdf):
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "This is page text."
        mock_doc.__iter__ = lambda self: iter([mock_page])
        mock_pymupdf.open.return_value.__enter__.return_value = mock_doc
        pdf_path = Path("/path/to/test.pdf")
        result = _extract_pdf(pdf_path, "transcript")
        assert isinstance(result, str)
        assert len(result) > 0
        mock_pymupdf.open.assert_called_once_with(pdf_path)

    @patch("core.components.section_producer.pymupdf")
    def test_extract_pdf_presentation(self, mock_pymupdf):
        mock_doc = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Slide 1 content"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Slide 2 content"
        mock_doc.__iter__ = lambda self: iter([mock_page1, mock_page2])
        mock_pymupdf.open.return_value.__enter__.return_value = mock_doc
        pdf_path = Path("/path/to/test.pdf")
        result = _extract_pdf(pdf_path, "presentation")
        assert isinstance(result, str)
        assert "# Slide Page 0" in result
        assert "# Slide Page 1" in result
        assert "Slide 1 content" in result
        assert "Slide 2 content" in result

    @patch("core.components.section_producer.pymupdf")
    def test_extract_pdf_exception_handling(self, mock_pymupdf):
        mock_pymupdf.open.side_effect = Exception("PDF read error")
        pdf_path = Path("/path/to/test.pdf")
        with pytest.raises(Exception):
            _extract_pdf(pdf_path, "transcript")
