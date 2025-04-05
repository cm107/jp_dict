import json
import os
from .error import CLIError

class SerializableObject:
    def to_dict(self) -> dict:
        return self.__dict__
    
    @classmethod
    def from_dict(cls, itemDict: dict):
        return cls(**itemDict)

    def save(self, path: str):
        json.dump(
            self.to_dict(), open(path, 'w'),
            ensure_ascii=False, indent=2
        )

    @classmethod
    def load(cls, path: str):
        if not os.path.isfile(path):
            raise CLIError(f"File not found: {path=}")
        return cls.from_dict(
            json.load(open(path, 'r'))
        )
