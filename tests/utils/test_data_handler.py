import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from utils import data_handler


class TestDataHandler:
    @patch("utils.data_handler.Path.home")
    def test_data_folder_path(self, mock_home):
        mock_home.return_value = Path("/home/user")
        from utils import data_handler

        assert ".moves" in str(data_handler.DATA_FOLDER)

    @patch("utils.data_handler.Path.home")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    def test_write_success(self, mock_write, mock_mkdir, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_write.return_value = None
        mock_mkdir.return_value = None
        result = data_handler.write(Path("test/file.txt"), "test data")
        assert result is True
        mock_mkdir.assert_called_once()
        mock_write.assert_called_once_with("test data", encoding="utf-8")

    @patch("utils.data_handler.Path.home")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    def test_write_failure(self, mock_write, mock_mkdir, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_write.side_effect = Exception("Write failed")
        with pytest.raises(RuntimeError, match="Write operation failed"):
            data_handler.write(Path("test/file.txt"), "test data")

    @patch("utils.data_handler.Path.home")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.read_text")
    def test_read_success(self, mock_read, mock_is_file, mock_exists, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_read.return_value = "file content"
        result = data_handler.read(Path("test/file.txt"))
        assert result == "file content"

    @patch("utils.data_handler.Path.home")
    @patch("pathlib.Path.exists")
    def test_read_file_not_found(self, mock_exists, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_exists.return_value = False
        with pytest.raises(FileNotFoundError):
            data_handler.read(Path("test/file.txt"))

    @patch("utils.data_handler.Path.home")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    def test_read_is_directory(self, mock_is_file, mock_exists, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_exists.return_value = True
        mock_is_file.return_value = False
        with pytest.raises(IsADirectoryError):
            data_handler.read(Path("test/dir"))

    @patch("utils.data_handler.Path.home")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.iterdir")
    def test_list_success(self, mock_iterdir, mock_exists, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_exists.return_value = True
        mock_file1 = MagicMock()
        mock_file1.__str__ = MagicMock(return_value="/tmp/.moves/test/file1.txt")
        mock_file2 = MagicMock()
        mock_file2.__str__ = MagicMock(return_value="/tmp/.moves/test/file2.txt")
        mock_iterdir.return_value = [mock_file1, mock_file2]
        result = data_handler.list(Path("test"))
        assert len(result) == 2

    @patch("utils.data_handler.Path.home")
    @patch("pathlib.Path.exists")
    def test_list_nonexistent(self, mock_exists, mock_home):
        mock_home.return_value = Path("/tmp")
        mock_exists.return_value = False
        result = data_handler.list(Path("nonexistent"))
        assert result == []
