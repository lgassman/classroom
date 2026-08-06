import json
from pathlib import Path

from platformdirs import user_config_dir


class AllConfig:
    def __init__(self, app_name="classroom"):
        config_dir = Path(user_config_dir(app_name))
        config_dir.mkdir(parents=True, exist_ok=True)

        self.file = config_dir / "config.json"
        self.data = None

    def _ensure_loaded(self):
        if self.data is not None:
            return

        if not self.file.exists():
            self.data = {}
            return

        with self.file.open("r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get(self, key, default=None):
        self._ensure_loaded()
        return self.data.get(key, default)

    def set(self, key, value):
        self._ensure_loaded()
        self.data[key] = value
        return self

    def remove(self, key):
        self._ensure_loaded()
        self.data.pop(key, None)
        return self

    def save(self):
        self._ensure_loaded()

        with self.file.open("w", encoding="utf-8") as f:
            json.dump(
                self.data,
                f,
                indent=2,
                ensure_ascii=False,
            )

config = AllConfig()
class Config:
    def __init__(self, key): 
        self.key = key

    def save(self, value):
        config.set(self.key, value).save()

    def get(self):
        return config.get(self.key)

    def delete(self):
        config.remove().save()

client_config = Config("client")

