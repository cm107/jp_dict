from __future__ import annotations
from typing import List
from enum import Enum, unique
from datetime import datetime
from common_utils.base.basic import BasicObject, BasicLoadableObject, \
    BasicLoadableHandler, BasicHandler

# TODO: Create an enum for category

class AnkiChange(
    BasicLoadableObject['AnkiChange'],
    BasicObject['AnkiChange']
):
    @unique
    class LogCategory(Enum):
        COLLECTION = 0
        DECK = 1
        CARD = 2
        NOTE = 3
        TAG = 4
        MODEL = 5

    @unique
    class LogSubcategory(Enum):
        CREATE = 0
        ADD = 1
        UPDATE = 2
        DELETE = 3

    def __init__(
        self,
        timestamp: datetime, # Required
        category: LogCategory,
        subcategory: LogSubcategory,
        deck_name: str=None, # Deck Related
        tag_name: str=None, # Tag Related
        model_name: str=None, # Model Related
        unique_id: str=None, field_name: str=None, # Note Related
        previous_value: str=None, new_value: str=None,
        comment: str=None, # Miscellaneous
        show_values: bool=True # Control Flags
    ):
        super().__init__()
        # Required
        self.timestamp = timestamp
        self.category = category
        self.subcategory = subcategory

        # Deck Related
        self.deck_name = deck_name

        # Tag Related
        self.tag_name = tag_name

        # Model Related
        self.model_name = model_name

        # Note Related
        self.unique_id = unique_id
        self.field_name = field_name
        self.previous_value = previous_value
        self.new_value = new_value

        # Miscellaneous
        self.comment = comment

        # Control Flags
        self.show_values = show_values
    
    def __str__(self):
        timestamp_str = self.timestamp.strftime('%Y/%m/%d %H:%M:%S')

        print_str = f'[{timestamp_str}] {self.category.name} {self.subcategory.name}'
        if self.category == self.LogCategory.COLLECTION:
            raise NotImplementedError
        elif self.category == self.LogCategory.DECK:
            if self.subcategory == self.LogSubcategory.CREATE:
                print_str += f'\nCreated Deck: {self.deck_name}'
            elif self.subcategory == self.LogSubcategory.DELETE:
                print_str += f'\nDeleted Deck: {self.deck_name}'
            else:
                raise IndexError
        elif self.category == self.LogCategory.CARD:
            raise NotADirectoryError
        elif self.category == self.LogCategory.NOTE:
            if self.subcategory == self.LogSubcategory.UPDATE:
                print_str += f'\nDeck: {self.deck_name}, Field: {self.field_name}'
                if self.show_values:
                    print_str += f'\nPrevious Value: {self.previous_value}'
                    print_str += f"\nNew Value: {self.new_value}"
            elif self.subcategory == self.LogSubcategory.ADD:
                print_str += f'\nDeck: {self.deck_name} - Added {self.field_name}: {self.new_value}'
        elif self.category == self.LogCategory.TAG:
            raise NotImplementedError
        elif self.category == self.LogCategory.MODEL:
            if self.subcategory == self.LogSubcategory.CREATE:
                print_str += f'\nCreated Model: {self.model_name}'
            elif self.subcategory == self.LogSubcategory.UPDATE:
                print_str += f'\nUpdated Model: {self.model_name}'
            else:
                raise IndexError
        else:
            raise IndexError
        
        if self.comment is not None:
            print_str += f'\nComment: {self.comment}'

        return print_str
    
    def to_dict(self) -> dict:
        item_dict = {
            'timestamp': self.timestamp.timestamp(),
            'category': self.category.name,
            'subcategory': self.subcategory.name
        }
        for key, val in self.to_constructor_dict().items():
            if key in item_dict:
                continue
            if val is None:
                continue
            else:
                item_dict[key] = val
        return item_dict

    
    @classmethod
    def from_dict(cls, item_dict: dict) -> AnkiChange:
        item_dict0 = item_dict.copy()
        item_dict0['timestamp'] = datetime.fromtimestamp(item_dict0['timestamp'])
        item_dict0['category'] = cls.LogCategory.__getattr__(item_dict0['category'])
        item_dict0['subcategory'] = cls.LogCategory.__getattr__(item_dict0['subcategory'])
        return AnkiChange(**item_dict0)

class AnkiChangeList(
    BasicLoadableHandler['AnkiChangeList', 'AnkiChange'],
    BasicHandler['AnkiChangeList', 'AnkiChange']
):
    def __init__(self, changes: List[AnkiChange]=None):
        super().__init__(obj_type=AnkiChange, obj_list=changes)
        self.changes = self.obj_list
    
    def __str__(self) -> str:
        print_str = ''
        for i, change in enumerate(self):
            if i == 0:
                print_str += f'{change}'
            else:
                print_str += f'\n\n{change}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> AnkiChangeList:
        return AnkiChangeList([AnkiChange.from_dict(item_dict) for item_dict in dict_list])
    
    def chronological_sort(self, reverse: bool=False):
        self.sort(attr_name='timestamp', reverse=reverse)
    
    @property
    def deck_names(self) -> List[str]:
        return list(set([change.deck_name for change in self]))

    @property
    def has_consistent_deck(self) -> bool:
        return len(self.deck_names) <= 1
    
    @property
    def unique_ids(self) -> List[str]:
        return list(set([change.unique_id for change in self]))

    @property
    def has_consistent_unique_id(self) -> bool:
        return len(self.unique_ids) <= 1

    @property
    def field_names(self) -> List[str]:
        return list(set([change.field_name for change in self]))

    @property
    def has_consistent_field(self) -> bool:
        unique_field_names = self.field_names
        return len(unique_field_names) <= 1
    
    def write_to_txt(self, save_path: str):
        f = open(save_path, 'w')
        f.write(str(self))
        f.close()
