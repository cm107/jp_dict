from __future__ import annotations
from typing import List, Dict, TypeVar
from abc import abstractmethod, abstractclassmethod
from common_utils.base.basic import BasicLoadableObject, BasicObject, \
    BasicLoadableHandler, BasicHandler

T = TypeVar('T')

class BaseFields(
    BasicLoadableObject[T],
    BasicObject[T]
):
    def __init__(self):
        super().__init__()
    
    @property
    def number_of_fields(self) -> int:
        return len(list(self.to_constructor_dict().keys()))

    # @abstractmethod
    # def to_dict(self) -> dict:
    #     raise NotImplementedError

    # @classmethod
    # @abstractclassmethod
    # def from_dict(cls, item_dict: dict) -> T:
    #     raise NotImplementedError

class BasicFields(BaseFields['BasicFields']):
    def __init__(self, front: str='', back: str=''):
        super().__init__()
        self.front = front
        self.back = back
        self.to_dict()
    
    def to_dict(self) -> dict:
        return {
            'Front': self.front,
            'Back': self.back
        }

    @classmethod
    def from_dict(cls, item_dict: dict) -> BasicFields:
        return BasicFields(
            front=item_dict['Front'],
            back=item_dict['Back']
        )

class JapaneseStandardFields(BaseFields['JapaneseStandardFields']):
    def __init__(self, word: str, reading: str, meaning: str):
        super().__init__()
        self.word = word
        self.reading = reading
        self.meaning = meaning
    
    def to_dict(self) -> dict:
        return {
            'Word': self.word,
            'Reading': self.reading,
            'Meaning': self.meaning
        }
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> JapaneseStandardFields:
        return JapaneseStandardFields(
            word=item_dict['Word'],
            reading=item_dict['Reading'],
            meaning=item_dict['Meaning']
        )

class JapaneseStandardFieldsList(
    BasicLoadableHandler['JapaneseStandardFieldsList', 'JapaneseStandardFields'],
    BasicHandler['JapaneseStandardFieldsList', 'JapaneseStandardFields']
):
    def __init__(self, fields_list: List[JapaneseStandardFields]=None):
        super().__init__(obj_type=JapaneseStandardFields, obj_list=fields_list)
        self.fields_list = self.obj_list

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> JapaneseStandardFieldsList:
        return JapaneseStandardFieldsList([JapaneseStandardFields.from_dict(item_dict) for item_dict in dict_list])

class BasicFieldsList(
    BasicLoadableHandler['BasicFieldsList', 'BasicFields'],
    BasicHandler['BasicFieldsList', 'BasicFields']
):
    def __init__(self, fields_list: List[BasicFields]=None):
        super().__init__(obj_type=BasicFields, obj_list=fields_list)
        self.fields_list = self.obj_list

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> BasicFieldsList:
        return BasicFieldsList([BasicFields.from_dict(item_dict) for item_dict in dict_list])

class ParsedVocabularyFields(BasicLoadableObject['ParsedVocabularyFields']):
    def __init__(
        self,
        writing: str, reading: str,
        common: str, jlpt_level: str, wanikani_level: str,
        eng_definition: str, daijisen: str, seisenpan: str, ndz: str,
        links: str,
        jisho_search_link: str, kotobank_search_link: str,
        ejje_sentence_search_link: str, weblio_search_link: str,
        searched_words: str, search_word_hit_count: str,
        cumulative_search_localtimes: str,
        order_idx: str, unique_id: str,
        custom_definition: str='',
        auto_open_fields: str='',
        memo: str=''
    ):
        # Defined only when adding new card
        self.writing = writing
        self.reading = reading
        self.common = common
        self.jlpt_level = jlpt_level
        self.wanikani_level = wanikani_level
        self.eng_definition = eng_definition
        self.daijisen = daijisen
        self.seisenpan = seisenpan
        self.ndz = ndz
        self.links = links
        self.jisho_search_link = jisho_search_link
        self.kotobank_search_link = kotobank_search_link
        self.ejje_sentence_search_link = ejje_sentence_search_link
        self.weblio_search_link = weblio_search_link

        # Updated Regularly
        self.searched_words = searched_words
        self.search_word_hit_count = search_word_hit_count
        self.cumulative_search_localtimes = cumulative_search_localtimes
        self.order_idx = order_idx

        # Should NEVER Change, EVER!
        self.unique_id = unique_id

        # For user input (Update From Anki Only)
        self.custom_definition = custom_definition
        self.auto_open_fields = auto_open_fields
        self.memo = memo

class ParsedVocabularyFieldsList(
    BasicLoadableHandler['ParsedVocabularyFieldsList', 'ParsedVocabularyFields'],
    BasicHandler['ParsedVocabularyFieldsList', 'ParsedVocabularyFields']
):
    def __init__(self, fields_list: List[ParsedVocabularyFields]=None):
        super().__init__(obj_type=ParsedVocabularyFields, obj_list=fields_list)
        self.fields_list = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> ParsedVocabularyFieldsList:
        return ParsedVocabularyFieldsList([ParsedVocabularyFields.from_dict(item_dict) for item_dict in dict_list])

class ParsedKanjiFields(BasicLoadableObject['ParsedKanjiFields']):
    def __init__(
        self,
        kanji: str,
        lesson_name: str, frame_num: str,
        reading: str, stroke_count: str,
        keyword: str,
        new_shared_stories: str, shared_stories: str,
        hit_count: str, used_in: str,
        order_idx: str, unique_id: str,
        new_shared_stories_show_idx: str="", shared_stories_show_idx: str="",
        custom_keyword: str="", custom_reading: str="", custom_story: str=""
    ):
        super().__init__()
        # Defined only when adding new card
        self.kanji = kanji
        self.lesson_name = lesson_name
        self.frame_num = frame_num
        self.reading = reading
        self.stroke_count = stroke_count
        self.keyword = keyword
        self.new_shared_stories = new_shared_stories
        self.shared_stories = shared_stories

        # Updated Regularly
        self.hit_count = hit_count
        self.used_in = used_in
        self.order_idx = order_idx
        
        # Should NEVER Change, EVER!
        self.unique_id = unique_id

        # For user input (Update From Anki Only)
        self.new_shared_stories_show_idx = new_shared_stories_show_idx
        self.shared_stories_show_idx = shared_stories_show_idx
        self.custom_keyword = custom_keyword
        self.custom_reading = custom_reading
        self.custom_story = custom_story

class ParsedKanjiFieldsList(
    BasicLoadableHandler['ParsedKanjiFieldsList', 'ParsedKanjiFields'],
    BasicHandler['ParsedKanjiFieldsList', 'ParsedKanjiFields']
):
    def __init__(self, fields_list: List[ParsedKanjiFields]=None):
        super().__init__(obj_type=ParsedKanjiFields, obj_list=fields_list)
        self.fields_list = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> ParsedKanjiFieldsList:
        return ParsedKanjiFieldsList([ParsedKanjiFields.from_dict(item_dict) for item_dict in dict_list])

class NoteAddOptions(BasicLoadableObject['NoteAddOptions']):
    def __init__(
        self,
        allow_duplicate: bool=True, deck_name: str='Default',
        check_children: bool=False
    ):
        super().__init__()
        self.allow_duplicate = allow_duplicate
        self.duplicate_scope = 'deck'
        self.duplicate_scope_options = {
            'deckName': deck_name,
            'checkChildren': check_children
        }

    def to_dict(self) -> dict:
        return {
            'allowDuplicate': self.allow_duplicate,
            'duplicateScope': self.duplicate_scope,
            'duplicateScopeOptions': {
                'deckName': self.duplicate_scope_options['deckName'],
                'checkChildren': self.duplicate_scope_options['checkChildren']
            }
        }

    @classmethod
    def from_dict(cls, item_dict: dict) -> NoteAddOptions:
        return NoteAddOptions(
            allow_duplicate=item_dict['allowDuplicate'],
            deck_name=item_dict['duplicateScopeOptions']['deckName'],
            check_children=item_dict['duplicateScopeOptions']['checkChildren']
        )

class NoteAddParam(BasicLoadableObject['NoteAddParam']):
    def __init__(
        self, deck_name: str='Default', model_name: str='Basic',
        fields: BaseFields=None, options=None, tags: List[str]=None,
        audio=None, video=None, picture=None
    ):
        super().__init__()
        self.deck_name = deck_name
        self.model_name = model_name
        self.fields = fields if fields is not None else BasicFields()
        self.options = options if options is not None else NoteAddOptions()
        self.tags = tags if tags is not None else []
        self.audio = audio if audio is not None else []
        self.video = video if video is not None else []
        self.picture = picture if picture is not None else []
    
    def to_dict(self) -> dict:
        return {
            'deckName': self.deck_name,
            'modelName': self.model_name,
            'fields': self.fields.to_dict(),
            'options': self.options.to_dict(),
            'tags': self.tags,
            'audio': self.audio,
            'video': self.video,
            'picture': self.picture
        }
    
    @classmethod
    def from_dict(cls, item_dict: dict, fields_class: type=BasicFields) -> NoteAddParam:
        return NoteAddParam(
            deck_name=item_dict['deckName'],
            model_name=item_dict['modelName'],
            fields=fields_class.from_dict(item_dict['fields']),
            options=NoteAddOptions.from_dict(item_dict['options']),
            tags=item_dict['tags'],
            audio=item_dict['audio'],
            video=item_dict['video'],
            picture=item_dict['picture']
        )
    
    @classmethod
    def from_fields(cls, deck_name: str, fields: BaseFields, model_name: str, **kwargs) -> NoteAddParam:
        # assert isinstance(fields, BaseFields)
        if 'options' in kwargs:
            options = kwargs['options']
            if isinstance(options, dict):
                options = NoteAddOptions.from_dict(options)
        else:
            options = NoteAddOptions(
                allow_duplicate=kwargs['allow_duplicate'] if 'allow_duplicate' in kwargs else True,
                deck_name=deck_name,
                check_children=kwargs['check_children'] if 'check_children' in kwargs else False
            )
        tags = kwargs['tags'] if 'tags' in kwargs else []
        audio = kwargs['audio'] if 'audio' in kwargs else []
        video = kwargs['video'] if 'video' in kwargs else []
        picture = kwargs['picture'] if 'picture' in kwargs else []
        return NoteAddParam(
            deck_name=deck_name,
            model_name=model_name,
            fields=fields,
            options=options,
            tags=tags,
            audio=audio,
            video=video,
            picture=picture
        )

    @classmethod
    def basic(cls, deck_name: str, fields: BasicFields, **kwargs) -> NoteAddParam:
        return cls.from_fields(
            deck_name=deck_name,
            fields=fields,
            model_name='Basic',
            **kwargs
        )
    
    @classmethod
    def jp_standard(cls, deck_name: str, fields: JapaneseStandardFields, **kwargs) -> NoteAddParam:
        return cls.from_fields(
            deck_name=deck_name,
            fields=fields,
            model_name='jp_standard',
            **kwargs
        )
    
    @classmethod
    def basic_simple(cls, deck_name: str, front: str, back: str, **kwargs) -> NoteAddParam:
        return cls.basic(deck_name=deck_name, fields=BasicFields(front=front, back=back), **kwargs)

    @classmethod
    def parsed_vocab(cls, deck_name: str, fields: ParsedVocabularyFields, **kwargs) -> NoteAddParam:
        return cls.from_fields(
            deck_name=deck_name,
            fields=fields,
            model_name='parsed_vocab',
            **kwargs
        )
    
    @classmethod
    def parsed_kanji(cls, deck_name: str, fields: ParsedKanjiFields, **kwargs) -> NoteAddParam:
        return cls.from_fields(
            deck_name=deck_name,
            fields=fields,
            model_name='parsed_kanji',
            **kwargs
        )

class NoteAddParamList(
    BasicLoadableHandler['NoteAddParamList', 'NoteAddParam'],
    BasicHandler['NoteAddParamList', 'NoteAddParam']
):
    def __init__(self, notes: List[NoteAddParam]=None):
        super().__init__(obj_type=NoteAddParam, obj_list=notes)
        self.notes = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> NoteAddParamList:
        return NoteAddParamList([NoteAddParam.from_dict(item_dict) for item_dict in dict_list])

    @classmethod
    def basic(cls, deck_name: str, fields_list: BasicFieldsList, **kwargs) -> NoteAddParamList:
        notes = NoteAddParamList()
        for fields in fields_list:
            note = NoteAddParam.basic(deck_name=deck_name, fields=fields, **kwargs)
            notes.append(note)
        return notes

    @classmethod
    def basic_simple(cls, deck_name: str, front_list: List[str], back_list: List[str], **kwargs) -> NoteAddParamList:
        assert len(front_list) == len(back_list)
        fields_list = BasicFieldsList([BasicFields(front=front, back=back) for front, back in zip(front_list, back_list)])
        return cls.basic(deck_name=deck_name, fields_list=fields_list, **kwargs)

    @classmethod
    def from_basic_dict_list(cls, deck_name: str, basic_dict_list: List[Dict[str, str]], **kwargs) -> NoteAddParamList:
        fields_list = BasicFieldsList.from_dict_list(basic_dict_list)
        return cls.basic(deck_name=deck_name, fields_list=fields_list, **kwargs)
    
    @classmethod
    def jp_standard(cls, deck_name: str, fields_list: JapaneseStandardFieldsList, **kwargs) -> NoteAddParamList:
        notes = NoteAddParamList()
        for fields in fields_list:
            note = NoteAddParam.jp_standard(deck_name=deck_name, fields=fields, **kwargs)
            notes.append(note)
        return notes

    @classmethod
    def parsed_vocab(cls, deck_name: str, fields_list: ParsedVocabularyFieldsList, **kwargs) -> NoteAddParamList:
        notes = NoteAddParamList()
        for fields in fields_list:
            note = NoteAddParam.parsed_vocab(deck_name=deck_name, fields=fields, **kwargs)
            notes.append(note)
        return notes
    
    @classmethod
    def parsed_kanji(cls, deck_name: str, fields_list: ParsedKanjiFieldsList, **kwargs) -> NoteAddParamList:
        notes = NoteAddParamList()
        for fields in fields_list:
            note = NoteAddParam.parsed_kanji(deck_name=deck_name, fields=fields, **kwargs)
            notes.append(note)
        return notes