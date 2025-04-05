from __future__ import annotations
from abc import abstractmethod
from .serializable_obj import SerializableObject
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .meta import MetaDirectory

class MetaDirectoryModule(SerializableObject):
    def __init__(self, meta: MetaDirectory):
        self._meta = meta

    @abstractmethod
    def convert_to_dict(self, item_dict: dict):
        pass

    def to_dict(self) -> dict:
        _dict = self.__dict__.copy()
        del _dict['_meta']
        self.convert_to_dict(_dict)
        return _dict

    @classmethod
    @abstractmethod
    def extract_prepostinit(cls, item_dict: dict) -> tuple[dict, dict]:
        return item_dict, {}
    
    @classmethod
    def from_dict(cls, meta: MetaDirectory, item_dict: dict):
        preinit, postinit = cls.extract_prepostinit(item_dict)
        obj = cls(meta, **preinit)
        for key, val in postinit.items():
            setattr(obj, key, val)
        return obj
