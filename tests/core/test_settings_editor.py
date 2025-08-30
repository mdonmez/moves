from unittest.mock import patch, MagicMock
from pathlib import Path
from core.settings_editor import SettingsEditor


class TestSettingsEditor:
    @patch("core.settings_editor.data_handler")
    @patch("core.settings_editor.tomlkit")
    @patch("core.settings_editor.Path")
    def test_settings_editor_init_with_existing_settings(
        self, mock_path, mock_tomlkit, mock_data_handler
    ):
        mock_template_path = MagicMock()
        mock_path.return_value = mock_template_path
        mock_template_path.read_text.return_value = "[model]\nname = 'gpt-4'"
        mock_data_handler.DATA_FOLDER = Path("/tmp/.moves")
        mock_data_handler.read.return_value = "[model]\nname = 'gpt-3.5'"
        mock_template_doc = MagicMock()
        mock_tomlkit.parse.side_effect = [mock_template_doc, MagicMock()]
        mock_template_doc.__iter__ = lambda self: iter({"model": {"name": "gpt-4"}})
        mock_tomlkit.dumps.return_value = "[model]\nname = 'gpt-4'"
        editor = SettingsEditor()
        assert editor._template_doc == mock_template_doc
        mock_data_handler.read.assert_called_once()

    @patch("core.settings_editor.data_handler")
    @patch("core.settings_editor.tomlkit")
    @patch("core.settings_editor.Path")
    def test_settings_editor_init_without_existing_settings(
        self, mock_path, mock_tomlkit, mock_data_handler
    ):
        mock_template_path = MagicMock()
        mock_path.return_value = mock_template_path
        mock_template_path.read_text.return_value = "[model]\nname = 'gpt-4'"
        mock_data_handler.DATA_FOLDER = Path("/tmp/.moves")
        mock_data_handler.read.side_effect = Exception("File not found")
        mock_template_doc = MagicMock()
        mock_tomlkit.parse.return_value = mock_template_doc
        mock_template_doc.__iter__ = lambda self: iter({"model": {"name": "gpt-4"}})
        mock_tomlkit.dumps.return_value = "[model]\nname = 'gpt-4'"
        editor = SettingsEditor()
        assert editor._template_doc == mock_template_doc
