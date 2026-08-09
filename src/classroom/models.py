from dataclasses import dataclass
import re
from urllib.parse import urlparse


class ModelSerializer :

    def __init__(self, cls):
        self.cls = cls

    def to_json(self, object):
        return str(object)

    def from_json(self, jsonObject):
        return self.cls.from_str(jsonObject)


@dataclass(frozen=True)
class Course:
    organization: str
    year: str
    semester: str
    course: str

    def __post_init__(self):
        for field_name, value in ( ("organization", self.organization),("year", self.year),("semester", self.semester),("course", self.course),):
            if not re.fullmatch(r"[a-z0-9-]+", value):
                raise ValueError(
                    f"{field_name} must contain only lowercase letters, numbers and hyphens"
                )
    @property
    def name(self):
        return f"{self.organization}-{self.year}s{self.semester}c{self.course}"

    def __str__(self):
        return self.name

    @classmethod
    def from_str(cls, name):
        if name is None:
            return None

        organization, rest = name.rsplit("-", 1)
        year, rest = rest.split("s", 1)
        semester, course = rest.split("c", 1)

        return cls(
            organization=organization,
            year=year,
            semester=semester,
            course=course,
        )



@dataclass
class RepoTemplate:
    owner: str
    name: str
    private: bool = False
    include_all_branches: bool = False
    default_branch: str | None = None

    @classmethod
    def from_str(cls, value, private=False):
        value = value.strip().rstrip("/")

        if value.startswith(("http://", "https://")):
            parsed = urlparse(value)
            parts = parsed.path.strip("/").split("/")
        else:
            parts = value.split("/")

        if len(parts) != 2 or not all(parts):
            raise ValueError(
                "Template must be a GitHub repository URL or have the form 'owner/repository'"
            )

        owner, name = parts
        name = name.removesuffix(".git")

        return cls(owner=owner, name=name, private=private)

    @property
    def repository(self):
        return f"{self.owner}/{self.name}"

    def __str__(self):
        return self.repository