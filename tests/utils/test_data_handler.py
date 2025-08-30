import pytest
from pathlib import Path
from src.utils import data_handler


@pytest.fixture(autouse=True)
def mock_data_folder(monkeypatch, tmp_path):
    monkeypatch.setattr(data_handler, "DATA_FOLDER", tmp_path)
    return tmp_path


def test_write_and_read(mock_data_folder):
    test_path = Path("testdir/testfile.txt")
    test_content = "Hello, world!"

    data_handler.write(test_path, test_content)

    full_path = mock_data_folder / test_path
    assert full_path.exists()
    assert full_path.read_text(encoding="utf-8") == test_content

    read_content = data_handler.read(test_path)
    assert read_content == test_content


def test_list(mock_data_folder):
    test_dir = Path("list_test")
    (mock_data_folder / test_dir).mkdir()
    (mock_data_folder / test_dir / "file1.txt").touch()
    (mock_data_folder / test_dir / "dir1").mkdir()

    items = data_handler.list(test_dir)
    item_names = {item.name for item in items}

    assert len(items) == 2
    assert "file1.txt" in item_names
    assert "dir1" in item_names


def test_delete_file(mock_data_folder):
    test_path = Path("delete_me.txt")
    full_path = mock_data_folder / test_path
    full_path.touch()

    assert full_path.exists()
    data_handler.delete(test_path)
    assert not full_path.exists()


def test_delete_directory(mock_data_folder):
    test_path = Path("delete_dir")
    full_path = mock_data_folder / test_path
    full_path.mkdir()
    (full_path / "file.txt").touch()

    assert full_path.exists()
    data_handler.delete(test_path)
    assert not full_path.exists()


def test_rename(mock_data_folder):
    old_path = Path("old_name.txt")
    (mock_data_folder / old_path).write_text("content")

    new_path_relative = data_handler.rename(old_path, "new_name.txt")

    assert not (mock_data_folder / old_path).exists()
    assert (mock_data_folder / "new_name.txt").exists()
    assert new_path_relative == Path("new_name.txt")
