from .definition import Definitions
from .jap_vocab import OtherForms
from .misc import Notes

class VocabularyEntry:
    def __init__(self, definitions: Definitions=None, other_forms: OtherForms=None, notes: Notes=None):
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