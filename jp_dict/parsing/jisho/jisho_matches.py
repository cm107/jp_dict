from __future__ import annotations
from typing import List
from .jisho_structs import DictionaryEntryList
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler

class SearchWordMatches(BasicLoadableObject['SearchWordMatches']):
    def __init__(self, search_word: str, matches: DictionaryEntryList=None):
        super().__init__()
        self.search_word = search_word
        self.matches = matches if matches is not None else DictionaryEntryList()
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> SearchWordMatches:
        return SearchWordMatches(
            search_word=item_dict['search_word'],
            matches=DictionaryEntryList.from_dict_list(item_dict['matches'])
        )

class SearchWordMatchesHandler(
    BasicLoadableHandler['SearchWordMatchesHandler', 'SearchWordMatches'],
    BasicHandler['SearchWordMatchesHandler', 'SearchWordMatches']
):
    def __init__(self, matches_list: List[SearchWordMatches]=None):
        super().__init__(obj_type=SearchWordMatches, obj_list=matches_list)
        self.matches_list = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> SearchWordMatchesHandler:
        return SearchWordMatchesHandler([SearchWordMatches.from_dict(item_dict) for item_dict in dict_list])

    def get_unique(self) -> SearchWordMatchesHandler:
        return SearchWordMatchesHandler([sw_matches for sw_matches in self if len(sw_matches.matches) == 1])
    
    @property
    def search_words(self) -> List[str]:
        return [sw_matches.search_word for sw_matches in self]