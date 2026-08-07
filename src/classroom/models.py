from dataclasses import dataclass
import re

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