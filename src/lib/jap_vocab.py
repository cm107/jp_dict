from __future__ import annotations
from .base import BaseParsedObject

class JapaneseVocab(BaseParsedObject):
    def __init__(self, writing: str, reading: str):
        super().__init__()
        self.writing = writing
        self.reading = reading

    def __str__(self):
        return "Japanese Vocab:\n{} ({})\n".format(self.writing, self.reading)

    @classmethod
    def buffer(self, jap_vocab: JapaneseVocab) -> JapaneseVocab:
        return jap_vocab

    @classmethod
    def from_kana_maps(self, kana_maps: list) -> JapaneseVocab:
        reading = ''
        writing = ''
        for kana_map in kana_maps:
            reading += kana_map['reading']
            writing += kana_map['written_form']
        return JapaneseVocab(writing=writing, reading=reading)

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [
            JapaneseVocab(writing=f'Writing {i}', reading=f'Reading {i}') \
                for i in range(num_samples)
        ]

class OtherForm(BaseParsedObject):
    def __init__(self, kanji_writing: str, kana_writing: str):
        super().__init__()
        self.kanji_writing = kanji_writing
        self.kana_writing = kana_writing

    def __str__(self):
        return "{} 【{}】".format(self.kanji_writing, self.kana_writing)

    @classmethod
    def buffer(self, other_form: OtherForm) -> OtherForm:
        return other_form

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [
            OtherForm(kanji_writing=f'Kanji Writing {i}', kana_writing=f'Kana Writing {i}') \
                for i in range(num_samples)
        ]

class OtherForms(BaseParsedObject):
    def __init__(self, other_form_list: list):
        super().__init__()
        self.other_form_list = other_form_list

    def __str__(self):
        print_str = ''
        for i in range(len(self.other_form_list)):
            if i < len(self.other_form_list) - 1:
                print_str += '{}, '.format(self.other_form_list[i].__str__())
            else:
                print_str += '{}'.format(self.other_form_list[i].__str__())
        return print_str

    @classmethod
    def buffer(self, other_forms: OtherForms) -> OtherForms:
        return other_forms

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        other_form_list_list = []
        for i in range(num_samples):
            other_form_list = []
            for j in range(3):
                other_form_list.append(OtherForm(kanji_writing=f'Kanji Writing {i}_{j}', kana_writing=f'Kana Writing {i}_{j}'))
            other_form_list_list.append(other_form_list)
        return [OtherForms(other_form_list=other_form_list) for other_form_list in other_form_list_list]