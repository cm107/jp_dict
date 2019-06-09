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

class OtherForm:
    def __init__(self, kanji_writing: str, kana_writing: str):
        self.kanji_writing = kanji_writing
        self.kana_writing = kana_writing

    def __str__(self):
        return "{} 【{}】".format(self.kanji_writing, self.kana_writing)

    def __repr__(self):
        return self.__str__()

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