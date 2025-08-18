from pathlib import Path
import shutil

DATA_FOLDER = Path.home() / ".moves"


def write(path: Path, data: str) -> bool:
    full_path = DATA_FOLDER / Path(path)
    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(data, encoding="utf-8")
        return True
    except Exception as e:
        raise RuntimeError(f"Write operation failed for {path}: {e}") from e


def read(path: Path) -> str:
    full_path = DATA_FOLDER / Path(path)
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not full_path.is_file():
        raise IsADirectoryError(f"Path is a directory, not a file: {path}")
    try:
        data = full_path.read_text(encoding="utf-8")
        return data
    except Exception as e:
        raise RuntimeError(f"Read operation failed for {path}: {e}") from e


def list(path: Path) -> list[str]:
    full_path = DATA_FOLDER / Path(path)
    if not full_path.exists():
        return []

    items = []
    try:
        for item in full_path.iterdir():
            if item.is_file():
                items.append(item.name)
            elif item.is_dir():
                items.append(item.name + "/")
        return sorted(items)
    except Exception as e:
        raise RuntimeError(f"List operation failed for {path}: {e}") from e


def rename(path: Path, new_name: str) -> Path:
    full_path = DATA_FOLDER / Path(path)
    if not full_path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    new_path = full_path.parent / new_name
    if new_path.exists():
        raise FileExistsError(f"Target already exists: {new_name}")

    try:
        shutil.move(str(full_path), str(new_path))
        return new_path.relative_to(DATA_FOLDER)
    except Exception as e:
        raise RuntimeError(
            f"Rename operation failed for {path} to {new_name}: {e}"
        ) from e


def delete(path: Path) -> bool:
    full_path = DATA_FOLDER / Path(path)
    if not full_path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    try:
        if full_path.is_file():
            full_path.unlink()
        elif full_path.is_dir():
            shutil.rmtree(full_path)
        else:
            full_path.unlink()
        return True
    except Exception as e:
        raise RuntimeError(f"Delete operation failed for {path}: {e}") from e


def copy(source: Path, target: Path) -> bool:
    source_path = DATA_FOLDER / Path(source)
    target_path = DATA_FOLDER / Path(target)

    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source}")

    if not target_path.exists():
        try:
            target_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(
                f"Failed to create target directory {target}: {e}"
            ) from e

    try:
        if source_path.is_file():
            dest_file = target_path / source_path.name
            shutil.copy2(source_path, dest_file)
            return True
        elif source_path.is_dir():
            for item in source_path.rglob("*"):
                relative_path = item.relative_to(source_path)
                dest_item = target_path / relative_path
                if item.is_dir():
                    dest_item.mkdir(parents=True, exist_ok=True)
                else:
                    dest_item.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_item)
            return True
        else:
            raise RuntimeError(f"Source path is neither file nor directory: {source}")
    except Exception as e:
        raise RuntimeError(
            f"Copy operation failed from {source} to {target}: {e}"
        ) from e


if __name__ == "__main__":
    test_folder = Path("test_dir/")
    test_file = test_folder / "test.txt"

    input("Step 1: Write a file (press Enter)")
    write(test_file, "Hello, world!")
    print(f"Wrote to: {test_file}\n")

    input("Step 4: Read the file (press Enter)")
    content = read(test_file)
    print(f"Content of {test_file}:\n{content}\n")

    input("Step 5: List directory (press Enter)")
    items = list(test_folder)
    print(f"Contents of {test_folder}:\n{items}\n")

    input("Step 6: Test copy method (press Enter)")
    copy_target = Path("copy_test/")
    copy(test_file, copy_target)
    print(f"Copied {test_file} to {copy_target}")
    copied_items = list(copy_target)
    print(f"Contents of {copy_target}: {copied_items}\n")

    input("Step 7: Rename the file (press Enter)")
    new_file = "renamed.txt"
    renamed_path = rename(test_file, new_file)
    print(f"Renamed to: {renamed_path}\n")

    input("Step 8: Delete the file (press Enter)")
    delete(test_folder / new_file)
    print("File deleted.\n")

    input("Step 9: Delete the folders (press Enter)")
    delete(test_folder)
    delete(copy_target)
    print("Folders deleted.\n")

    print("All tests done.")
