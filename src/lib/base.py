from __future__ import annotations
from abc import ABCMeta, abstractmethod
from logger import logger

class BaseParsedObject(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self) -> str:
        ''' To override '''
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()

    def __key(self) -> tuple:
        return tuple([self.__class__] + list(self.__dict__.values()))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__key() == other.__key()
        return NotImplemented

    @abstractmethod
    def buffer(self) -> object:
        ''' To override as classmethod'''
        raise NotImplementedError

    def copy(self):
        return type(self)(*self.__dict__.values())

    @abstractmethod
    def sample(self, num_samples: int=1) -> list:
        ''' To override as classmethod'''
        raise NotImplementedError
