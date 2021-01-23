from __future__ import annotations
from typing import List
from tqdm import tqdm
from .jisho_structs import DictionaryEntry, DictionaryEntryList
from common_utils.base.basic import BasicLoadableIdObject, BasicLoadableIdHandler, BasicLoadableObject, BasicLoadableHandler, BasicHandler

class DictionaryEntryMatch(BasicLoadableIdObject['DictionaryEntryMatch']):
    def __init__(self, id: int=None, entry: DictionaryEntry=None, search_words: List[str]=None, history_group_id_list: List[int]=None):
        super().__init__(id=id)
        self.entry = entry
        self.search_words = search_words if search_words is not None else []
        self.history_group_id_list = history_group_id_list if history_group_id_list is not None else []
    
    def custom_str(self, indent: int=0) -> str:
        tab = lambda x: '\t' * x
        print_str = self.entry.custom_str(indent=indent)
        print_str += f'\n{tab(indent)}Search Words: {self.search_words}'
        print_str += f'\n{tab(indent)}History Group IDs: {self.history_group_id_list}'
        return print_str

    @classmethod
    def from_dict(cls, item_dict: dict) -> DictionaryEntryMatch:
        return DictionaryEntryMatch(
            id=item_dict['id'] if 'id' in item_dict else None,
            entry=DictionaryEntry.from_dict(item_dict['entry']) if item_dict['entry'] is not None else None,
            search_words=item_dict['search_words'],
            history_group_id_list=item_dict['history_group_id_list'] if 'history_group_id_list' in item_dict else None
        )
    
    @property
    def unique_search_word(self) -> str:
        if len(self.search_words) == 1:
            return self.search_words[0]
        elif len(self.search_words) == 0:
            raise ValueError(f"len({type(self).__name__}.search_words) == 0")
        else:
            raise ValueError(f"len({type(self).__name__}.search_words) > 1")

class DictionaryEntryMatchList(
    BasicLoadableIdHandler['DictionaryEntryMatchList', 'DictionaryEntryMatch'],
    BasicHandler['DictionaryEntryMatchList', 'DictionaryEntryMatch']
):
    def __init__(self, matches: List[DictionaryEntryMatch]=None):
        super().__init__(obj_type=DictionaryEntryMatch, obj_list=matches)
        self.matches = self.obj_list

    def custom_str(self, indent: int=0, num_line_breaks: int=2) -> str:
        print_str = ''
        first = True
        line_breaks = lambda x: '\n' * x
        for entry in self:
            if first:
                print_str += entry.custom_str(indent=indent)
                first = False
            else:
                print_str += f'{line_breaks(num_line_breaks)}{entry.custom_str(indent=indent)}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> DictionaryEntryMatchList:
        return DictionaryEntryMatchList([DictionaryEntryMatch.from_dict(item_dict) for item_dict in dict_list])
    
    @property
    def search_words(self) -> List[str]:
        result = []
        for item in self:
            result.extend(item.search_words)
        return sorted(list(set(result)), reverse=False)

    @property
    def entries(self) -> DictionaryEntryList:
        return DictionaryEntryList([item.entry for item in self])

    def add_pruned_matches(self, handler: SearchWordMatchesHandler, mode: int=0, show_pbar: bool=True, leave_pbar: bool=True, debug_verbose: bool=False):
        """
        Possible modes
            0: Process only first entry only. Ignore if entry already exists in matches.
            1: Process every entry. Ignore if any entry already exists in matches. Otherwise add first entry.
            2: Process every entry. Add first entry that doesn't already exist in matches, if any.
        
        Pros and Cons of each mode:
            0:
                Pros: Moderately fast and resolves most non-unique cases.
                Cons: Overlooks some useful entries that are not listed first. May also pick up some redundant entries.
            1:
                Pros: Strictly avoids redundant entries while resolving some non-unique cases.
                Cons: Slow. Can ignores non-trivial entries if the same written form has already been matched.
            2:
                Pros: Focuses on finding as many matches as possible, including those that have already been matched with the same written form.
                Cons: Slow. Can pick up many redundant entries.
        
        TODO:   Test each mode while comparing the number of pruned matches.
        """
        def process_first_match_only(handler: SearchWordMatchesHandler, pbar: tqdm=None):
            for match in handler.first_matches:
                if pbar is not None:
                    pbar.set_description(match.unique_search_word)
                found = False
                for item in self:
                    # if item.entry == match.entry:
                    if item.entry.same_entry_as(match.entry, strict=False):
                        if match.unique_search_word not in item.search_words:
                            item.search_words.append(match.unique_search_word)
                            item.history_group_id_list.extend(match.history_group_id_list)
                        else:
                            raise Exception(f"Encountered duplicate search_word: {match.unique_search_word}")
                        found = True
                        if debug_verbose:
                            print(f'{item.entry.word_representation.simple_repr}: {item.search_words}')
                        break
                if not found:
                    match.id = len(self)
                    self.append(match)
                if pbar is not None:
                    pbar.update()

        pbar = tqdm(total=len(handler), unit='item(s)', leave=leave_pbar) if show_pbar else None

        if mode == 0:
            # Process only first entry of non-unique.
            # Ignore if entry already exists in matches.
            process_first_match_only(handler=handler, pbar=pbar)
        elif mode == 1:
            # Process every entry of non-unique.
            # Ignore if any entry already exists in matches.
            # Otherwise add first entry.
            for sw_matches in handler:
                if pbar is not None:
                    pbar.set_description(sw_matches.search_word)
                found = False
                for item in self:
                    for entry in sw_matches.matches:
                        # if item.entry == entry:
                        if item.entry.same_entry_as(entry, strict=False):
                            if sw_matches.search_word not in item.search_words:
                                item.search_words.append(sw_matches.search_word)
                                item.history_group_id_list.append(sw_matches.history_group_id)
                            else:
                                raise Exception(f"Encountered duplicate search_word: {sw_matches.search_word}")
                            found = True
                            if debug_verbose:
                                print(f'{item.entry.word_representation.simple_repr}: {item.search_words}')
                            break
                    if found:
                        break
                if found:
                    pass
                else:
                    entry_match = DictionaryEntryMatch(
                        entry=sw_matches.matches[0],
                        search_words=[sw_matches.search_word],
                        history_group_id_list=[sw_matches.history_group_id]
                    )
                    entry_match.id = len(self)
                    self.append(entry_match)
                if pbar is not None:
                    pbar.update()
        elif mode == 2:
            # Process every entry of non-unique.
            # Add first entry that doesn't already exist in matches, if any.
            for sw_matches in handler:
                if pbar is not None:
                    pbar.set_description(sw_matches.search_word)
                first_nonmatched_entry = None
                first_matched_item = None
                for entry in sw_matches.matches:
                    matched_item = None
                    for item in self:
                        # if item.entry == entry:
                        if item.entry.same_entry_as(entry, strict=False):
                            if matched_item is None:
                                matched_item = item
                            else:
                                pass
                    if matched_item is None:
                        first_nonmatched_entry = entry
                        break
                    else:
                        first_matched_item = matched_item
                if first_nonmatched_entry is not None:
                    entry_match = DictionaryEntryMatch(
                        entry=first_nonmatched_entry,
                        search_words=[sw_matches.search_word],
                        history_group_id_list=[sw_matches.history_group_id]
                    )
                    entry_match.id = len(self)
                    self.append(entry_match)
                elif first_matched_item is not None:
                    if sw_matches.search_word not in first_matched_item.search_words:
                        first_matched_item.search_words.append(sw_matches.search_word)
                        first_matched_item.history_group_id_list.append(sw_matches.history_group_id)
                        if debug_verbose:
                            print(f'{first_matched_item.entry.word_representation.simple_repr}: {first_matched_item.search_words}')
                    else:
                        raise Exception(f"Encountered duplicate search_word: {sw_matches.search_word}")
                else:
                    pass
                if pbar is not None:
                    pbar.update()
        else:
            raise ValueError(f"Invalid mode: {mode}")

        if pbar is not None:
            pbar.close()

class SearchWordMatches(BasicLoadableObject['SearchWordMatches']):
    def __init__(self, search_word: str, matches: DictionaryEntryList=None, history_group_id: int=None):
        super().__init__()
        self.search_word = search_word
        self.matches = matches if matches is not None else DictionaryEntryList()
        self.history_group_id = history_group_id
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> SearchWordMatches:
        return SearchWordMatches(
            search_word=item_dict['search_word'],
            matches=DictionaryEntryList.from_dict_list(item_dict['matches']) if item_dict['matches'] is not None else None,
            history_group_id=item_dict['history_group_id'] if 'history_group_id' in item_dict else None
        )
    
    @property
    def first_match(self) -> DictionaryEntryMatch:
        return DictionaryEntryMatch(
            search_words=[self.search_word],
            entry=self.matches[0] if self.matches is not None else None,
            history_group_id_list=[self.history_group_id]
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

    @property
    def unique(self) -> SearchWordMatchesHandler:
        return SearchWordMatchesHandler([sw_matches for sw_matches in self if len(sw_matches.matches) == 1])
    
    @property
    def non_unique(self) -> SearchWordMatchesHandler:
        return SearchWordMatchesHandler([sw_matches for sw_matches in self if len(sw_matches.matches) > 1])

    @property
    def search_words(self) -> List[str]:
        return [sw_matches.search_word for sw_matches in self]
    
    @property
    def first_matches(self) -> DictionaryEntryMatchList:
        return DictionaryEntryMatchList([obj.first_match for obj in self])