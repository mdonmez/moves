from pathlib import Path
from ruamel.yaml import YAML
from io import StringIO
import copy

from ..data.models import Settings
from ..utils import data_handler


yaml = YAML()


class SettingsEditor:
    template_path = Path("src/data/settings_template.yaml")
    settings_filename = Path("settings.yaml")

    def __init__(self):
        try:
            self.template_node = (
                yaml.load(self.template_path.read_text(encoding="utf-8")) or {}
            )
        except Exception:
            self.template_node = {}

        try:
            loaded = yaml.load(data_handler.read(self.settings_filename)) or {}
        except Exception:
            loaded = {}

        self._data = (
            {**self.template_node, **loaded}
            if isinstance(self.template_node, dict)
            else loaded
        )
        try:
            self._save()
        except Exception:
            pass

    def _save(self):
        node = (
            copy.deepcopy(self.template_node)
            if isinstance(self.template_node, dict)
            else dict(self._data)
        )
        node.update(self._data)
        buf = StringIO()
        yaml.dump(node, buf)
        return data_handler.write(self.settings_filename, buf.getvalue())

    def set(self, key, value):
        self._data[key] = value
        try:
            self._save()
            return True
        except Exception:
            return False

    def unset(self, key):
        if key in self.template_node:
            self._data[key] = self.template_node[key]
        else:
            self._data.pop(key, None)
        try:
            self._save()
            return True
        except Exception:
            return False

    def list(self):
        return Settings(
            llm_model=self._data.get("llm_model", ""),
            llm_api_key=self._data.get("llm_api_key", ""),
            selected_mic=int(self._data.get("selected_mic", 0)),
        )


if __name__ == "__main__":
    editor = SettingsEditor()
    print("Initial settings:", editor.list())
    print("Setting 'llm_model' to 'gpt-4'")
    editor.set("llm_model", "gpt-4")
    print("Updated settings:", editor.list())
    print("Unsetting 'llm_model'")
    editor.unset("llm_model")
    print("Settings after unset:", editor.list())
