from __future__ import annotations
from ..base import BaseParsedObject
from .definition import Definitions
from .jap_vocab import OtherForms
from .misc import Notes

class VocabularyEntry(BaseParsedObject):
    def __init__(self, definitions: Definitions=None, other_forms: OtherForms=None, notes: Notes=None):
        super().__init__()
        self.definitions = definitions
        self.other_forms = other_forms
        self.notes = notes

    def __str__(self):
        print_str = ''
        if self.definitions is not None:
            print_str += 'Definitions:\n{}\n'.format(self.definitions)
        if self.other_forms is not None:
            print_str += 'Other Forms:\n{}\n\n'.format(self.other_forms)
        if self.notes is not None:
            print_str += 'Notes:\n{}\n\n'.format(self.notes)
        return print_str

    def __repr__(self):
        return self.__str__()

    @classmethod
    def buffer(self, vocab_entry: VocabularyEntry) -> VocabularyEntry:
        return vocab_entry

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [
            VocabularyEntry(
                definitions=definitions,
                other_forms=other_forms,
                notes=notes
            ) for definitions, other_forms, notes in \
                zip(
                    Definitions.sample(num_samples),
                    OtherForms.sample(num_samples),
                    Notes.sample(num_samples)
                )
        ]