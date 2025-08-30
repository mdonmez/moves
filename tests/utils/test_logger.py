from pathlib import Path
from unittest.mock import patch, MagicMock
from utils.logger import Logger


class TestLogger:
    @patch("utils.logger.Path.home")
    @patch("utils.logger.inspect.stack")
    def test_logger_initialization(self, mock_stack, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_frame = MagicMock()
        mock_frame.filename = "/path/to/module.py"
        mock_stack.return_value = [None, mock_frame]
        logger = Logger()
        assert logger._logger.name == "moves.module"

    @patch("utils.logger.Path.home")
    @patch("utils.logger.inspect.stack")
    def test_logger_info(self, mock_stack, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_frame = MagicMock()
        mock_frame.filename = "/path/to/test.py"
        mock_stack.return_value = [None, mock_frame]
        logger = Logger()
        with patch.object(logger._logger, "info") as mock_info:
            logger.info("Test message")
            mock_info.assert_called_once_with("Test message")

    @patch("utils.logger.Path.home")
    @patch("utils.logger.inspect.stack")
    def test_logger_error(self, mock_stack, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_frame = MagicMock()
        mock_frame.filename = "/path/to/test.py"
        mock_stack.return_value = [None, mock_frame]
        logger = Logger()
        with patch.object(logger._logger, "error") as mock_error:
            logger.error("Test error")
            mock_error.assert_called_once_with("Test error")

    @patch("utils.logger.Path.home")
    @patch("utils.logger.inspect.stack")
    def test_logger_fallback_module_name(self, mock_stack, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_stack.side_effect = Exception("Stack inspection failed")
        logger = Logger()
        assert logger._logger.name == "moves.main"
