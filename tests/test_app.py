import pytest
from unittest.mock import patch
from app import version_callback


class TestApp:
    @patch("importlib.metadata.version")
    def test_version_callback_with_version(self, mock_version):
        mock_version.return_value = "1.2.3"
        with patch("app.typer.echo") as mock_echo:
            with pytest.raises(Exception):
                version_callback(True)
            mock_echo.assert_called_with("moves version 1.2.3")

    @patch("importlib.metadata.version")
    def test_version_callback_without_version(self, mock_version):
        mock_version.side_effect = Exception("No version found")
        with patch("app.typer.echo") as mock_echo:
            with pytest.raises(Exception):
                version_callback(True)
            mock_echo.assert_called_with("moves version 0.2.0")

    def test_version_callback_false(self):
        with patch("app.typer.echo") as mock_echo:
            version_callback(False)
            mock_echo.assert_not_called()
