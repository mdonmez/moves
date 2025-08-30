from unittest.mock import patch
from data.models import Section
from core.presentation_controller import PresentationController


class TestPresentationController:
    @patch("core.presentation_controller.SimilarityCalculator")
    def test_presentation_controller_init(self, mock_similarity_calc):
        sections = [
            Section("Section 1", 0),
            Section("Section 2", 1),
            Section("Section 3", 2),
        ]
        start_section = sections[0]
        controller = PresentationController(sections, start_section, window_size=10)
        assert controller.sections == sections
        assert controller.current_section == start_section
        assert controller.window_size == 10
        assert controller.frame_duration == 0.1
        assert controller.sample_rate == 16000
        mock_similarity_calc.assert_called_once()

    @patch("core.presentation_controller.SimilarityCalculator")
    def test_presentation_controller_init_default_window(self, mock_similarity_calc):
        sections = [Section("Section 1", 0)]
        start_section = sections[0]
        controller = PresentationController(sections, start_section)
        assert controller.window_size == 12
