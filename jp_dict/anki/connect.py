import json
import urllib.request
from typing import List, Dict
from .note_structs import NoteAddParam, NoteAddParamList, \
    BaseFields, BasicFields, BasicFieldsList

class AnkiConnect:
    def __init__(self, base_url: str='http://localhost:8765'):
        self.base_url = base_url

    def request(self, action, **params):
        return {'action': action, 'params': params, 'version': 6}

    def invoke(self, action, **params):
        requestJson = json.dumps(self.request(action, **params)).encode('utf-8')
        response = json.load(urllib.request.urlopen(urllib.request.Request(self.base_url, requestJson)))
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']
    
    def create_deck(self, deck: str, verbose: bool=True):
        self.invoke('createDeck', deck=deck)
        if verbose:
            print(f'Created deck: {deck}')
    
    def get_deck_names(self, exclude_default: bool=False) -> List[str]:
        result = self.invoke('deckNames')
        if exclude_default:
            result = [name for name in result if name != 'Default']
        return result
    
    def get_deck_names_and_ids(self) -> Dict[str, int]:
        result = self.invoke('deckNamesAndIds')
        return result
    
    def get_corresponding_decks_of_cards(self, cards: List[int]) -> Dict[str, List[int]]:
        result = self.invoke('getDecks', cards=cards)
        return result
    
    def move_cards(self, cards: List[int], dst_deck: str, verbose: bool=True):
        is_new_deck = not dst_deck in self.get_deck_names()
        self.invoke('changeDeck', cards=cards, deck=dst_deck)
        if verbose:
            if is_new_deck:
                print(f'Moved cards {cards} to new deck: {dst_deck}')
            else:
                print(f'Moved cards {cards} to deck: {dst_deck}')

    def delete_deck(self, deck: str, cards_too: bool=True, verbose: bool=True):
        if not isinstance(deck, list):
            decks = [deck]
        else:
            decks = deck
        
        self.invoke('deleteDecks', decks=decks, cardsToo=cards_too)

        if verbose:
            if not cards_too:
                print(f'Deleted decks: {decks}')
            else:
                print(f'Deleted decks and cards: {decks}')
    
    def cards_are_due(self, cards: List[int]) -> List[bool]:
        result = self.invoke('are_Due', cards=cards)
        return result
    
    def get_intervals_of_cards(self, cards: List[int]) -> List[List[int]]:
        result = self.invoke('getIntervals', cards=cards, complete=True)
        return result
    
    def find_cards(self, query: str) -> List[int]:
        result = self.invoke('findCards', query=query)
        return result
    
    def cards2notes(self, cards: List[int]) -> List[int]:
        result = self.invoke('cardsToNotes', cards=cards)
        return result
    
    def cards_info(self, cards: List[int]) -> List[dict]:
        result = self.invoke('cardsInfo', cards=cards)
        return result
    
    def add_note(self, note: NoteAddParam) -> int:
        note0 = note.to_dict() if isinstance(note, NoteAddParam) else note
        result = self.invoke('addNote', note=note0)
        return result
    
    def add_basic_note(self, deck_name: str, fields: BasicFields, **kwargs) -> int:
        result = self.add_note(
            note=NoteAddParam.basic(
                deck_name=deck_name,
                fields=fields
            )
        )
        return result

    def add_basic_simple_note(self, deck_name: str, front: str, back: str, **kwargs) -> int:
        result = self.add_note(
            note=NoteAddParam.basic_simple(
                deck_name=deck_name,
                front=front, back=back,
                **kwargs
            )
        )
        return result
    
    def add_notes(self, notes: NoteAddParamList) -> List[int]:
        notes0 = notes.to_dict_list() if isinstance(notes, NoteAddParamList) else notes
        result = self.invoke('addNotes', notes=notes0)
        return result
    
    def add_basic_notes(self, deck_name: str, fields_list: BasicFieldsList, **kwargs) -> List[int]:
        result = self.add_notes(
            notes=NoteAddParamList.basic(
                deck_name=deck_name,
                fields_list=fields_list,
                **kwargs
            )
        )
        return result

    def add_basic_simple_notes(self, deck_name: str, front_list: List[str], back_list: List[str], **kwargs) -> List[int]:
        result = self.add_notes(
            notes=NoteAddParamList.basic_simple(
                deck_name=deck_name,
                front=front_list,
                back=back_list,
                **kwargs
            )
        )
        return result
    
    def add_notes_from_basic_dict_list(self, deck_name: str, basic_dict_list: List[Dict[str, str]], **kwargs) -> List[int]:
        result = self.add_notes(
            notes=NoteAddParamList.from_basic_dict_list(
                deck_name=deck_name,
                basic_dict_list=basic_dict_list,
                **kwargs
            )
        )
        return result
    
    def can_add_notes(self, notes: NoteAddParamList) -> List[bool]:
        notes0 = notes.to_dict_list() if isinstance(notes, NoteAddParamList) else notes
        result = self.invoke('canAddNotes', notes=notes0)
        return result
    
    def update_note_fields(self, note_id: int, fields: BaseFields, audio=None, video=None, image=None):
        assert isinstance(fields, BaseFields)
        note_dict = {
            'id': note_id,
            'fields': fields.to_dict()
        }
        if audio is not None:
            note_dict['audio'] = audio
        if video is not None:
            note_dict['video'] = video
        if image is not None:
            note_dict['image'] = image
        self.invoke('updateNoteFields', note=note_dict)
    
    def add_tag(self, note_ids: List[int], tag: str):
        self.invoke('addTags', notes=note_ids, tags=tag)
    
    def remove_tag(self, note_ids: List[int], tag: str):
        self.invoke('removeTags', notes=note_ids, tags=tag)
    
    def get_tags(self) -> List[str]:
        result = self.invoke('getTags')
        return result
    
    def clear_unused_tags(self):
        self.invoke('clearUnusedTags')
    
    def replace_tag(self, note_ids: List[int], src_tag: str, dst_tag: str):
        self.invoke('replaceTags', notes=note_ids, tag_to_replace=src_tag, replace_with_tag=dst_tag)
    
    def replace_tag_in_all_notes(self, src_tag: str, dst_tag: str):
        self.invoke('replaceTagsInAllNotes', tag_to_replace=src_tag, replace_with_tag=dst_tag)

    def find_notes(self, query: str) -> List[int]:
        """Refer to query syntax.
        https://docs.ankiweb.net/#/searching
        """
        result = self.invoke('findNotes', query=query)
        return result
    
    def get_notes_info(self, note_ids: List[int]) -> List[dict]:
        result = self.invoke('notesInfo', notes=note_ids)
        return result
    
    def delete_notes(self, note_ids: List[int]):
        self.invoke('deleteNotes', notes=note_ids)
    
    def remove_empty_notes(self):
        self.invoke('removeEmptyNotes')