from __future__ import annotations

class JapaneseVocab:
    def __init__(self, kana_maps: dict):
        self.kana_maps = kana_maps
        reading = ''
        writing = ''
        for kana_map in kana_maps:
            reading += kana_map['reading']
            writing += kana_map['written_form']
        self.writing = writing
        self.reading = reading

    def __str__(self):
        return "Japanese Vocab:\n{} ({})\n".format(self.writing, self.reading)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def buffer(self, jap_vocab: JapaneseVocab) -> JapaneseVocab:
        return jap_vocab

    def copy(self) -> JapaneseVocab:
        return JapaneseVocab(kana_maps=self.kana_maps)

class OtherForm:
    def __init__(self, kanji_writing: str, kana_writing: str):
        self.kanji_writing = kanji_writing
        self.kana_writing = kana_writing

    def __str__(self):
        return "{} 【{}】".format(self.kanji_writing, self.kana_writing)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def buffer(self, other_form: OtherForm) -> OtherForm:
        return other_form

    def copy(self) -> OtherForm:
        return OtherForm(kanji_writing=self.kanji_writing, kana_writing=self.kana_writing)

class OtherForms:
    def __init__(self, other_form_list: list):
        self.other_form_list = other_form_list

    def __str__(self):
        print_str = ''
        for i in range(len(self.other_form_list)):
            if i < len(self.other_form_list) - 1:
                print_str += '{}, '.format(self.other_form_list[i].__str__())
            else:
                print_str += '{}'.format(self.other_form_list[i].__str__())
        return print_str

    def __repr__(self):
        return self.__str__()

    @classmethod
    def buffer(self, other_forms: OtherForms) -> OtherForms:
        return other_forms

    def copy(self) -> OtherForms:
        return OtherForms(other_form_list=self.other_form_list)