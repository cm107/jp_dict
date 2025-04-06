from __future__ import annotations
from abc import abstractmethod
import json
import os

class SerializableObj:
    def to_dict(self) -> dict:
        _dict = self.__dict__.copy()
        for key, val in _dict.items():
            if val is None:
                continue
            if isinstance(val, SerializableObj):
                _dict[key] = val.to_dict()
        return _dict
    
    @classmethod
    def from_dict(cls, item_dict: dict):
        return cls(**item_dict)
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f'File not found: {path}')
        with open(path, 'r', encoding='utf-8') as f:
            return cls.from_dict(json.load(f))

class SettingsObj(SerializableObj):
    @abstractmethod
    def save_to_meta(self):
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def load_from_meta(cls):
        raise NotImplementedError
