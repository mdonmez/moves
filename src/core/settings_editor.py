from pathlib import Path
import tomlkit
import copy
from typing import Dict, Any
from importlib import resources

from data.models import Settings
from utils import data_handler


class SettingsEditor:
    settings = data_handler.DATA_FOLDER / "settings.toml"

    def __init__(self):
        # Use importlib.resources to access the template file from the package
        try:
            import data
            template_text = resources.read_text(data, "settings_template.toml")
        except (ImportError, FileNotFoundError):
            # Fallback for development
            template_path = Path("src/data/settings_template.toml")
            template_text = template_path.read_text(encoding="utf-8")
        
        self._template_doc = tomlkit.parse(template_text)
        self._template_defaults: Dict[str, Any] = dict(self._template_doc)

        try:
            user_data = dict(tomlkit.parse(data_handler.read(self.settings)))
        except Exception:
            user_data = {}

        self._data = {**self._template_defaults, **user_data}

        self._save()

    def _save(self) -> bool:
        try:
            self.settings.parent.mkdir(parents=True, exist_ok=True)
            node = copy.deepcopy(self._template_doc)

            for key in self._template_defaults.keys():
                if key in self._data:
                    node[key] = self._data[key]

            with self.settings.open("w", encoding="utf-8") as f:
                f.write(tomlkit.dumps(node))
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to save settings: {e}") from e

    def set(self, key: str, value: Any) -> bool:
        if key not in self._template_defaults:
            return False

        self._data[key] = value
        try:
            self._save()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to set key '{key}': {e}") from e

    def unset(self, key: str) -> bool:
        if key in self._template_defaults:
            self._data[key] = self._template_defaults[key]
        else:
            self._data.pop(key, None)

        try:
            self._save()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to unset key '{key}': {e}") from e

    def list(self) -> Settings:
        return Settings(**self._data)


if __name__ == "__main__":
    import sys

    editor = SettingsEditor()

    print("Current data:", editor._data)

    test_key = "model"
    print(f"\n[SET] {test_key} -> 'gpt-4'")
    result = editor.set(test_key, "gpt-4")
    print("Result:", result)
    print("Data after set:", editor._data)

    print(f"\n[UNSET] {test_key}")
    result = editor.unset(test_key)
    print("Result:", result)
    print("Data after unset:", editor._data)

    print("\n[LIST]")
    settings_obj = editor.list()
    print(settings_obj)

    print("\n=== Test Completed ===")
    sys.exit(0)
