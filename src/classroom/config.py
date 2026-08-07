import json
import shutil
from pathlib import Path
import logging

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

        try:
            with self.file.open("r", encoding="utf-8") as f:
                self.data = json.load(f)
        except json.JSONDecodeError:
            corrupt_file = self.file.with_suffix(".json.corrupt")

            logging.warning(
                f"Warning: configuration file is corrupted. "
                f"A backup was created at: {corrupt_file}"
            )

            shutil.move(self.file, corrupt_file)
            self.data = {}

    def get(self, key, default=None):
        self._ensure_loaded()
        return self.data.get(key, default)

    def get_list(self, key):
        return self.get(key, [])

    def set(self, key, value):
        self._ensure_loaded()
        self.data[key] = value
        return self

    def add(self, key, value):
        self._ensure_loaded()

        values = self.data.setdefault(key, [])
        values.append(value)

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


class NoneSerializer:
    def to_json(self, object):
        return object

    def from_json(self, jsonObject):
        return jsonObject

class Config:
    def __init__(self, key, serializer=NoneSerializer()):
        self.key = key
        self.serializer = serializer

    def save(self, value):
        config.set(self.key, self.serializer.to_json(value)).save()

    def get(self):
        return self.serializer.from_json(config.get(self.key))

    def delete(self):
        config.remove(self.key).save()


class ListConfig(Config):

    def get(self):
        return [self.serializer.from_json(value) for value in config.get_list(self.key)]

    def add(self, value):
        config.add(self.key, self.serializer.to_json(value)).save()

    def remove(self, value):
        values = self.get()
        json_value = self.serializer.to_json(value)
        if json_value in values:
            values.remove(json_value)
            config.set(self.key, values).save()


    def add_if_missing(self, value):
        values = self.get()
        json_value = self.serializer.to_json(value)
        if json_value in values:
            values.append(json_value)
            config.set(self.key, values).save()

