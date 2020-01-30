from __future__ import annotations
from ..base import BaseParsedObject
import random

class ConceptLabels(BaseParsedObject):
    def __init__(self, is_common_word: bool, jlpt_level: int=None, wanikani_level: int=None):
        super().__init__()
        self.is_common_word = is_common_word
        self.jlpt_level = jlpt_level
        self.wanikani_level = wanikani_level

    def __str__(self):
        def append_str(first: bool, print_str: str, item: str) -> (bool, str):
            result_str = print_str
            if first:
                result_str += '{}'.format(item)
            else:
                result_str += ', {}'.format(item)
            return False, result_str

        print_str = 'Concept Labels:\n'
        first = True
        if self.is_common_word:
            print_str += 'Common Word'
            first = False
        if self.jlpt_level is not None:
            first, print_str = append_str(first, print_str, 'JLPT N{}'.format(self.jlpt_level))
        if self.wanikani_level is not None:
            first, print_str = append_str(first, print_str, 'WaniKani Level {}'.format(self.wanikani_level))
        
        print_str += '\n'
        return print_str

    @classmethod
    def buffer(self, concept_labels: ConceptLabels) -> ConceptLabels:
        return concept_labels

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [ConceptLabels(
            is_common_word=i%2==0, jlpt_level=i+1,
            wanikani_level=i+1
        ) for i in range(num_samples)]