"""Tests for utils.data_handler module."""
import pytest
from pathlib import Path
from unittest.mock import patch

from utils import data_handler


def test_write_creates_file_and_directories(mock_data_folder):
    """Test write function creates directories and writes content."""
    test_path = Path("test/subdir/file.txt")
    test_data = "Hello, World!"
    
    result = data_handler.write(test_path, test_data)
    
    assert result is True
    full_path = mock_data_folder / test_path
    assert full_path.exists()
    assert full_path.is_file()
    assert full_path.read_text(encoding="utf-8") == test_data


def test_write_overwrites_existing_file(mock_data_folder):
    """Test write function overwrites existing files."""
    test_path = Path("existing_file.txt")
    original_data = "Original content"
    new_data = "New content"
    
    # Create initial file
    data_handler.write(test_path, original_data)
    # Overwrite it
    result = data_handler.write(test_path, new_data)
    
    assert result is True
    full_path = mock_data_folder / test_path
    assert full_path.read_text(encoding="utf-8") == new_data


def test_write_handles_unicode(mock_data_folder):
    """Test write function handles unicode content properly."""
    test_path = Path("unicode.txt")
    unicode_data = "Hello 世界! Café naïve résumé"
    
    result = data_handler.write(test_path, unicode_data)
    
    assert result is True
    full_path = mock_data_folder / test_path
    assert full_path.read_text(encoding="utf-8") == unicode_data


def test_read_returns_file_content(mock_data_folder):
    """Test read function returns correct file content."""
    test_path = Path("test_file.txt")
    test_data = "Test content\nwith multiple lines"
    
    # Create file first
    data_handler.write(test_path, test_data)
    
    result = data_handler.read(test_path)
    assert result == test_data


def test_read_raises_filenotfound_for_nonexistent_file(mock_data_folder):
    """Test read function raises FileNotFoundError for non-existent files."""
    test_path = Path("nonexistent.txt")
    
    with pytest.raises(FileNotFoundError) as exc_info:
        data_handler.read(test_path)
    
    assert "File not found: nonexistent.txt" in str(exc_info.value)


def test_read_raises_error_for_directory(mock_data_folder):
    """Test read function raises IsADirectoryError when path is directory."""
    test_path = Path("test_directory")
    full_path = mock_data_folder / test_path
    full_path.mkdir()
    
    with pytest.raises(IsADirectoryError) as exc_info:
        data_handler.read(test_path)
    
    assert "Path is a directory, not a file" in str(exc_info.value)


def test_list_returns_empty_for_nonexistent_path(mock_data_folder):
    """Test list function returns empty list for non-existent path."""
    test_path = Path("nonexistent")
    
    result = data_handler.list(test_path)
    assert result == []


def test_list_returns_sorted_contents(mock_data_folder):
    """Test list function returns sorted directory contents."""
    test_path = Path("test_dir")
    full_path = mock_data_folder / test_path
    full_path.mkdir()
    
    # Create some files and directories
    (full_path / "z_file.txt").write_text("content")
    (full_path / "a_file.txt").write_text("content")
    (full_path / "m_subdir").mkdir()
    
    result = data_handler.list(test_path)
    
    assert len(result) == 3
    # Results should be sorted by string representation
    result_names = [p.name for p in result]
    assert result_names == sorted(result_names)


def test_rename_moves_file_successfully(mock_data_folder):
    """Test rename function moves file to new name."""
    original_path = Path("original.txt")
    new_name = "renamed.txt"
    test_data = "Test content"
    
    # Create original file
    data_handler.write(original_path, test_data)
    
    result = data_handler.rename(original_path, new_name)
    
    assert result == Path(new_name)
    assert not (mock_data_folder / original_path).exists()
    assert (mock_data_folder / new_name).exists()
    assert (mock_data_folder / new_name).read_text(encoding="utf-8") == test_data


def test_rename_overwrites_existing_target(mock_data_folder):
    """Test rename function overwrites existing target file."""
    original_path = Path("original.txt")
    target_name = "target.txt"
    original_data = "Original content"
    target_data = "Target content"
    
    # Create both files
    data_handler.write(original_path, original_data)
    data_handler.write(Path(target_name), target_data)
    
    result = data_handler.rename(original_path, target_name)
    
    assert result == Path(target_name)
    assert not (mock_data_folder / original_path).exists()
    assert (mock_data_folder / target_name).read_text(encoding="utf-8") == original_data


def test_delete_removes_file(mock_data_folder):
    """Test delete function removes files."""
    test_path = Path("to_delete.txt")
    data_handler.write(test_path, "content")
    
    result = data_handler.delete(test_path)
    
    assert result is True
    assert not (mock_data_folder / test_path).exists()


def test_delete_removes_directory(mock_data_folder):
    """Test delete function removes directories."""
    test_path = Path("to_delete_dir")
    full_path = mock_data_folder / test_path
    full_path.mkdir()
    (full_path / "file.txt").write_text("content")
    
    result = data_handler.delete(test_path)
    
    assert result is True
    assert not full_path.exists()


def test_delete_raises_error_for_nonexistent_path(mock_data_folder):
    """Test delete function raises FileNotFoundError for non-existent path."""
    test_path = Path("nonexistent.txt")
    
    with pytest.raises(FileNotFoundError) as exc_info:
        data_handler.delete(test_path)
    
    assert "Path not found: nonexistent.txt" in str(exc_info.value)


def test_copy_file_to_directory(mock_data_folder):
    """Test copy function copies file to target directory."""
    source_path = Path("source.txt")
    target_path = Path("target_dir")
    test_data = "Test content"
    
    # Create source file
    data_handler.write(source_path, test_data)
    
    result = data_handler.copy(source_path, target_path)
    
    assert result is True
    # Original should still exist
    assert (mock_data_folder / source_path).exists()
    # Copy should exist in target directory
    target_file = mock_data_folder / target_path / source_path.name
    assert target_file.exists()
    assert target_file.read_text(encoding="utf-8") == test_data


def test_copy_directory_recursively(mock_data_folder):
    """Test copy function copies directories recursively."""
    source_path = Path("source_dir")
    target_path = Path("target_dir")
    
    # Create source directory structure
    source_full = mock_data_folder / source_path
    source_full.mkdir()
    (source_full / "file1.txt").write_text("content1")
    (source_full / "subdir").mkdir()
    (source_full / "subdir" / "file2.txt").write_text("content2")
    
    result = data_handler.copy(source_path, target_path)
    
    assert result is True
    # Check that all files were copied
    target_full = mock_data_folder / target_path
    assert (target_full / "file1.txt").exists()
    assert (target_full / "subdir" / "file2.txt").exists()
    assert (target_full / "file1.txt").read_text() == "content1"
    assert (target_full / "subdir" / "file2.txt").read_text() == "content2"


def test_copy_raises_error_for_nonexistent_source(mock_data_folder):
    """Test copy function raises FileNotFoundError for non-existent source."""
    source_path = Path("nonexistent.txt")
    target_path = Path("target")
    
    with pytest.raises(FileNotFoundError) as exc_info:
        data_handler.copy(source_path, target_path)
    
    assert "Source not found: nonexistent.txt" in str(exc_info.value)


@pytest.mark.parametrize("exception_type", [PermissionError, OSError])
def test_write_handles_exceptions(mock_data_folder, exception_type):
    """Test write function handles various exceptions properly."""
    test_path = Path("test.txt")
    
    with patch("pathlib.Path.write_text", side_effect=exception_type("Mock error")):
        with pytest.raises(RuntimeError) as exc_info:
            data_handler.write(test_path, "content")
        
        assert "Write operation failed" in str(exc_info.value)


@pytest.mark.parametrize("exception_type", [PermissionError, UnicodeDecodeError])
def test_read_handles_exceptions(mock_data_folder, exception_type):
    """Test read function handles various exceptions properly."""
    test_path = Path("test.txt")
    # Create file first
    data_handler.write(test_path, "content")
    
    if exception_type == UnicodeDecodeError:
        side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "Mock decode error")
    else:
        side_effect = exception_type("Mock error")
    
    with patch("pathlib.Path.read_text", side_effect=side_effect):
        with pytest.raises(RuntimeError) as exc_info:
            data_handler.read(test_path)
        
        assert "Read operation failed" in str(exc_info.value)