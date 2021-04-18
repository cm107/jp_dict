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

    @abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    @abstractclassmethod
    def from_dict(cls, item_dict: dict) -> T:
        raise NotImplementedError

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

class NoteAddOptions(BasicLoadableObject['NoteAddOptions']):
    def __init__(
        self,
        allow_duplicate: bool=False, deck_name: str='Default',
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
    def basic(cls, deck_name: str, fields: BasicFields, **kwargs) -> NoteAddParam:
        if 'options' in kwargs:
            options = kwargs['options']
            if isinstance(options, dict):
                options = NoteAddOptions.from_dict(options)
        else:
            options = NoteAddOptions(
                allow_duplicate=kwargs['allow_duplicate'] if 'allow_duplicate' in kwargs else False,
                deck_name=deck_name,
                check_children=kwargs['check_children'] if 'check_children' in kwargs else False
            )
        tags = kwargs['tags'] if 'tags' in kwargs else []
        audio = kwargs['audio'] if 'audio' in kwargs else []
        video = kwargs['video'] if 'video' in kwargs else []
        picture = kwargs['picture'] if 'picture' in kwargs else []
        return NoteAddParam(
            deck_name=deck_name,
            model_name='Basic',
            fields=fields,
            options=options,
            tags=tags,
            audio=audio,
            video=video,
            picture=picture
        )
    
    @classmethod
    def basic_simple(cls, deck_name: str, front: str, back: str, **kwargs) -> NoteAddParam:
        return cls.basic(deck_name=deck_name, fields=BasicFields(front=front, back=back), **kwargs)

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