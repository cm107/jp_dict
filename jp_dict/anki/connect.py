import json
import urllib.request
from typing import List, Dict
from tqdm import tqdm
from .note_structs import NoteAddParam, NoteAddParamList, \
    BaseFields, BasicFields, BasicFieldsList, ParsedVocabularyFields, \
    ParsedKanjiFields
from .model_structs import CardTemplateList, CardTemplate

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
    
    def add_note_sequence(self, notes: NoteAddParamList, show_pbar: bool=True, leave_pbar: bool=True) -> List[int]:
        result = []
        pbar = tqdm(total=len(notes), unit='note(s)', leave=leave_pbar) if show_pbar else None
        if pbar is not None:
            pbar.set_description('Adding Notes')
        for note in notes:
            # try:
            #     result0 = self.add_note(note)
            # except:
            #     print('Exception!')
            #     if pbar is not None:
            #         pbar.update()
            #     continue
            result0 = self.add_note(note)
            result.append(result0)
            if pbar is not None:
                pbar.update()
        if pbar is not None:
            pbar.close()
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
    
    def get_model_names(self) -> List[str]:
        result = self.invoke('modelNames')
        return result
    
    def get_model_names_and_ids(self) -> Dict[str, int]:
        result = self.invoke('modelNamesAndIds')
        return result
    
    def get_model_field_names(self, model_name: str) -> List[str]:
        result = self.invoke('modelFieldNames', modelName=model_name)
        return result
    
    def get_model_field_names_on_templates(self, model_name: str) -> Dict[str, List[List[str]]]:
        result = self.invoke('modelFieldsOnTemplates', modelName=model_name)
        return result
    
    def create_model(self, model_name: str, field_names: List[str], css: str, card_templates: CardTemplateList) -> dict:
        # for field in card_templates.fields:
        #     assert field in field_names
        result = self.invoke(
            'createModel',
            modelName=model_name,
            inOrderFields=field_names,
            css=css,
            cardTemplates=card_templates.to_dict_list()
        )
        return result
    
    def get_model_templates(self, model_name: str) -> Dict[str, Dict[str, str]]:
        result = self.invoke('modelTemplates', modelName=model_name)
        return result

    def update_model_templates(self, model_name: str, card_templates: CardTemplateList):
        self.invoke(
            'updateModelTemplates',
            model={
                'name': model_name,
                'templates': card_templates.get_update_format_dict()
            }
        )
    
    def get_model_styling(self, model_name: str) -> Dict[str, str]:
        result = self.invoke('modelStyling', modelName=model_name)
        return result

    def update_model_styling(self, model_name: str, css: str):
        self.invoke(
            'updateModelStyling',
            model={
                'name': model_name,
                'css': css
            }
        )

    def create_jp_standard_model(self) -> dict:
        from textwrap import dedent
        self.create_model(
            model_name='jp_standard',
            field_names=['Word', 'Reading', 'Meaning'],
            css=dedent("""
            .card {
                font-family: arial;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
            }
            """),
            card_templates=CardTemplateList([
                CardTemplate(
                    name='Card 1',
                    front=dedent("""
                    {{Word}}
                    """),
                    back=dedent("""
                    {{Word}}
                    <hr id=answer>
                    Reading: {{Reading}}
                    <br>
                    Definition:
                    <br>
                    {{Meaning}}
                    """)
                ),
                CardTemplate(
                    name='Card 2',
                    front=dedent("""
                    {{Meaning}}
                    """),
                    back=dedent("""
                    {{Word}}
                    <hr id=answer>
                    Reading: {{Reading}}
                    <br>
                    Definition:
                    <br>
                    {{Meaning}}
                    """)
                ),
            ])
        )
    
    def _get_parsed_vocab_templates(self) -> (str, CardTemplateList):
        from textwrap import dedent
        from common_utils.path_utils import get_script_dir
        
        back_path = f"{get_script_dir()}/templates/parsed_vocab_back.html"
        back_text = ''.join(open(back_path, 'r').readlines()).replace('\n', '')
        css_path = f"{get_script_dir()}/templates/parsed_vocab_back.css"
        css_text = ''.join(open(css_path, 'r').readlines()).replace('\n', '')
        return css_text, CardTemplateList([
            CardTemplate(
                name='Card 1',
                front=dedent("""
                {{writing}}
                """).replace('\n', ''),
                back=back_text
            )
        ])

    def update_parsed_vocab_templates_and_styling(self):
        css_text, card_templates = self._get_parsed_vocab_templates()
        self.update_model_templates(model_name='parsed_vocab', card_templates=card_templates)
        self.update_model_styling(model_name='parsed_vocab', css=css_text)

    def create_parsed_vocab_model(self) -> dict:
        css_text, card_templates = self._get_parsed_vocab_templates()
        self.create_model(
            model_name='parsed_vocab',
            field_names=ParsedVocabularyFields.get_constructor_params(),
            css=css_text,
            card_templates=card_templates
        )
    
    def _get_parsed_kanji_templates(self) -> (str, CardTemplateList):
        from textwrap import dedent
        from common_utils.path_utils import get_script_dir
        
        back_path = f"{get_script_dir()}/templates/parsed_kanji.html"
        back_text = ''.join(open(back_path, 'r').readlines()).replace('\n', '')
        css_path = f"{get_script_dir()}/templates/parsed_kanji.css"
        css_text = ''.join(open(css_path, 'r').readlines()).replace('\n', '')
        return css_text, CardTemplateList([
            CardTemplate(
                name='Card 1',
                front=dedent("""
                {{kanji}}
                """).replace('\n', ''),
                back=back_text
            )
        ])

    def update_parsed_kanji_templates_and_styling(self):
        css_text, card_templates = self._get_parsed_kanji_templates()
        self.update_model_templates(model_name='parsed_kanji', card_templates=card_templates)
        self.update_model_styling(model_name='parsed_kanji', css=css_text)

    def create_parsed_kanji_model(self) -> dict:
        css_text, card_templates = self._get_parsed_kanji_templates()
        self.create_model(
            model_name='parsed_kanji',
            field_names=ParsedKanjiFields.get_constructor_params(),
            css=css_text,
            card_templates=card_templates
        )

    def gui_card_browse(self, query: str) -> List[int]:
        result = self.invoke('guiBrowse', query=query)
        return result