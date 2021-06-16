from __future__ import annotations
from ..base import BaseParsedObject

class Notes(BaseParsedObject):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def __str__(self):
        return self.text

    @classmethod
    def buffer(self, notes: Notes) -> Notes:
        return notes

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [Notes(text=f'Text {i}') for i in range(num_samples)]

class Link(BaseParsedObject):
    def __init__(self, text: str, url: str):
        super().__init__()
        self.text = text
        self.url = url

    def __str__(self):
        return f'[{self.text}]({self.url})'

    @classmethod
    def buffer(self, link: Link) -> Link:
        return link

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [
            Link(text=f'Text {i}', url=f'URL {i}') \
                for i in range(num_samples)
        ]