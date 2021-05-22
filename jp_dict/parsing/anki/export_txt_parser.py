from __future__ import annotations
from typing import List
import os
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, \
    BasicHandler

class AnkiExportTextDatum(BasicLoadableObject['AnkiExportTextDatum']):
    def __init__(self, writing: str, reading: str, definition: str):
        super().__init__()
        self.writing = writing
        self.reading = reading
        self.definition = definition
    
    def __str__(self) -> str:
        print_str = f'Writing: {self.writing}'
        print_str += f'\nReading: {self.reading}'
        print_str += f'\nDefinition: {self.definition}'
        return print_str

    @classmethod
    def from_line(self, text: str) -> AnkiExportTextDatum:
        parts = text.split('\t')
        parts = [part for part in parts if part not in ['', '\n']]
        if len(parts) == 3:
            writing, reading, definition = parts
        elif len(parts) == 2:
            writing, definition = parts
            reading = None
        elif len(parts) > 3:
            writing, reading = parts[:2]
            definition = '\t'.join(parts[2:])
        elif len(parts) == 1:
            print(f"Warning: Found line with only 1 part. Couldn't split into writing and reading: {parts}")
            writing = parts[0]
            reading = ''
            definition = ''
        else:
            raise Exception(f'len(parts) == {len(parts)} not in [2, 3]\nparts:\n{parts}')
        
        return AnkiExportTextDatum(
            writing=writing, reading=reading,
            definition=definition
        )


class AnkiExportTextData(
    BasicLoadableHandler['AnkiExportTextData', 'AnkiExportTextDatum'],
    BasicHandler['AnkiExportTextData', 'AnkiExportTextDatum']
):
    def __init__(self, data: List[AnkiExportTextDatum]=None):
        super().__init__(obj_type=AnkiExportTextDatum, obj_list=data)
        self.data = self.obj_list
    
    def __str__(self) -> str:
        print_str = ''
        for i, datum in enumerate(self):
            if i == 0:
                print_str += datum.__str__()
            else:
                print_str += f'\n\n{datum.__str__()}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> AnkiExportTextData:
        return AnkiExportTextData([AnkiExportTextDatum.from_dict(item_dict) for item_dict in dict_list])

    @classmethod
    def parse_from_txt(cls, path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Couldn't find file: {path}")
        f = open(path, 'r')

        data = AnkiExportTextData()
        for line in f.readlines():
            line.replace('\n', '')
            datum = AnkiExportTextDatum.from_line(line)
            data.append(datum)
        f.close()

        return data
    
    def contains(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self[0], key):
                raise AttributeError(f"{type(self[0]).__name__} has no attribute: {key}")

        for datum in self:
            hits = {key: val == datum.__dict__[key] for key, val in kwargs.items()}
            if all(list(hits.values())):
                return True
        
        return False

def parse_kanji_anki_export(path: str, field_idx: int) -> List[str]:
    kanji_list = []
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Couldn't find file: {path}")
    f = open(path, 'r')

    for line in f.readlines():
        parts = line.split('\t')
        parts = [part for part in parts if part not in ['', '\n']]
        kanji = parts[field_idx]
        if len(kanji) == 0:
            raise Exception
        elif len(kanji) == 1:
            kanji_list.append(kanji)
        else:
            kanji_list.extend(list(kanji.replace('・', '')))
    f.close()

    return kanji_list
