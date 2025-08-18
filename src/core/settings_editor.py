from pathlib import Path
from ruamel.yaml import YAML
import copy

from ..data.models import Settings
from ..utils import data_handler

yaml = YAML()


class SettingsEditor:
    template = Path("src/data/settings_template.yaml")
    settings = data_handler.DATA_FOLDER / Path("settings.yaml")

    def __init__(self):
        try:
            self.template_data = (
                yaml.load(self.template.read_text(encoding="utf-8")) or {}
            )
        except Exception:
            self.template_data = {}

        try:
            user_data = yaml.load(data_handler.read(self.settings)) or {}
        except Exception:
            user_data = {}

        self._data = (
            {**self.template_data, **user_data}
            if isinstance(self.template_data, dict)
            else user_data
        )

        try:
            self._save()
        except Exception:
            pass

    def _save(self):
        node = (
            copy.deepcopy(self.template_data)
            if isinstance(self.template_data, dict)
            else {}
        )
        for key in node.keys():
            if key in self._data:
                node[key] = self._data[key]

        with self.settings.open("w", encoding="utf-8") as f:
            yaml.dump(node, f)
        return True

    def set(self, key, value):
        if key not in self.template_data:
            return False
        self._data[key] = value
        try:
            self._save()
            return True
        except Exception:
            return False

    def unset(self, key):
        if key in self.template_data:
            self._data[key] = self.template_data[key]
        else:
            self._data.pop(key, None)
        try:
            self._save()
            return True
        except Exception:
            return False

    def list(self) -> Settings:
        return Settings(**self._data)


if __name__ == "__main__":
    import sys

    editor = SettingsEditor()

    print("Loaded template keys:", list(editor.template_data.keys()))
    print("Current data:", editor._data)

    test_key = "llm_model"
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
