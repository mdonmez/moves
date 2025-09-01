"""Tests for basic functionality that can run without external dependencies."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_version_callback_success():
    """Test version_callback with successful version retrieval."""
    with patch('app.importlib.metadata.version') as mock_version:
        with patch('app.typer.echo') as mock_echo:
            mock_version.return_value = "1.2.3"
            
            from app import version_callback
            
            with pytest.raises(SystemExit):  # typer.Exit raises SystemExit
                version_callback(True)
            
            mock_version.assert_called_once_with("moves")
            mock_echo.assert_called_once_with("moves version 1.2.3")


def test_version_callback_exception():
    """Test version_callback handles exceptions gracefully."""
    with patch('app.importlib.metadata.version', side_effect=Exception("Mock error")):
        with patch('app.typer.echo') as mock_echo:
            from app import version_callback
            
            with pytest.raises(SystemExit):  # typer.Exit raises SystemExit
                version_callback(True)
            
            mock_echo.assert_called_once_with("Error retrieving version")


def test_version_callback_false_value():
    """Test version_callback does nothing when value is False."""
    with patch('app.typer.echo') as mock_echo:
        from app import version_callback
        
        # Should return None and not raise SystemExit
        result = version_callback(False)
        
        assert result is None
        mock_echo.assert_not_called()


def test_app_initialization():
    """Test that the main Typer app is properly initialized."""
    from app import app
    
    assert app is not None
    assert hasattr(app, 'info')
    assert "Presentation control, reimagined" in app.info.help


def test_speaker_app_initialization():
    """Test that the speaker sub-app is properly initialized."""
    from app import speaker_app
    
    assert speaker_app is not None
    assert hasattr(speaker_app, 'info')
    assert "speaker profiles" in speaker_app.info.help.lower()


def test_presentation_app_initialization():
    """Test that the presentation sub-app is properly initialized."""
    from app import presentation_app
    
    assert presentation_app is not None
    assert hasattr(presentation_app, 'info')
    assert "presentation" in presentation_app.info.help.lower()


def test_settings_app_initialization():
    """Test that the settings sub-app is properly initialized."""
    from app import settings_app
    
    assert settings_app is not None
    assert hasattr(settings_app, 'info')
    assert "settings" in settings_app.info.help.lower()


def test_main_callback():
    """Test the main callback function."""
    from app import main
    
    # Should be callable and not raise errors
    result = main()
    assert result is None  # Main callback returns None


def test_factory_functions_exist():
    """Test that factory functions are defined."""
    from app import (
        speaker_manager_instance,
        presentation_controller_instance,
        settings_editor_instance
    )
    
    # Functions should exist and be callable
    assert callable(speaker_manager_instance)
    assert callable(presentation_controller_instance)
    assert callable(settings_editor_instance)


# Simple integration tests for utility functions we know work
def test_basic_data_models_integration():
    """Test basic integration with data models."""
    from data.models import Section, Chunk, Speaker, Settings
    from pathlib import Path
    
    # Test creating and using basic models
    section = Section(content="Test", section_index=0)
    assert section.content == "Test"
    
    chunk = Chunk(partial_content="Test chunk", source_sections=[section])
    assert chunk.partial_content == "Test chunk"
    
    speaker = Speaker(
        name="Test Speaker",
        speaker_id="test-123",
        source_presentation=Path("/test/pres.pdf"),
        source_transcript=Path("/test/trans.pdf")
    )
    assert speaker.name == "Test Speaker"
    
    settings = Settings(model="gpt-4", key="test-key")
    assert settings.model == "gpt-4"


def test_basic_id_generator_integration():
    """Test basic integration with id_generator."""
    from utils import id_generator
    
    # Test speaker ID generation
    speaker_id = id_generator.generate_speaker_id("Test User")
    assert isinstance(speaker_id, str)
    assert "test-user" in speaker_id
    assert len(speaker_id) > len("test-user")
    
    # Test history ID generation  
    history_id = id_generator.generate_history_id()
    assert isinstance(history_id, str)
    assert "_" in history_id
    assert "-" in history_id


def test_data_handler_integration_with_temp_dir():
    """Test data_handler with temporary directory."""
    from utils import data_handler
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(data_handler, 'DATA_FOLDER', Path(tmpdir)):
            test_path = Path("test_file.txt")
            test_content = "Hello, World!"
            
            # Test write and read
            assert data_handler.write(test_path, test_content)
            read_content = data_handler.read(test_path)
            assert read_content == test_content
            
            # Test list
            items = data_handler.list(Path("."))
            assert len(items) >= 1
            
            # Test delete
            assert data_handler.delete(test_path)
            
            # Test file no longer exists
            with pytest.raises(FileNotFoundError):
                data_handler.read(test_path)