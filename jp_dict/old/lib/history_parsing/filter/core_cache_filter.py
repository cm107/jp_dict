from __future__ import annotations
from abc import ABCMeta
from .tagged_cache_filter import TaggedCacheFilter
from .core import TaggedCacheHandler

class CacheFilter(metaclass=ABCMeta):
    def __init__(self, cache_list: list):
        self.tagged_cache_handler = self.get_tagged_cache_handler()
        self.cache_list = cache_list
        self.load_index = -1

    def get_tagged_cache_handler(self) -> TaggedCacheHandler:
        ''' To override '''
        raise NotImplementedError

    def is_fully_loaded(self) -> bool:
        return self.load_index == len(self.cache_list) - 1

    def load_tagged_cache_handler(self, batch_size: int=1):
        batch_count = 0
        for i, cache in enumerate(self.cache_list):
            if batch_count == batch_size:
                break
            elif i <= self.load_index:
                continue
            self.tagged_cache_handler.add_from_cache(cache)
            self.load_index = i
            batch_count += 1

    def apply_tags(self, start_from: int=None, verbose: bool=False):
        self.tagged_cache_handler.tag_garbage_characters(start_from=start_from, verbose=verbose)
        self.tagged_cache_handler.tag_japanese_chars(start_from=start_from, verbose=verbose)

    def get_filtered_results(
        self, no_wildcards: bool=True, no_eng_chars: bool=True, no_typo_chars: bool=True
    ) -> list:
        result = self.tagged_cache_handler.tagged_cache_list
        if no_wildcards:
            result = TaggedCacheFilter.filter_by_wildcard_tag(result, target='false')
        if no_eng_chars:
            result = TaggedCacheFilter.filter_by_eng_chars_tag(result, target='false')
        if no_typo_chars:
            result = TaggedCacheFilter.filter_by_typo_chars_tag(result, target='false')
        return result

    def get_wildcard_results(self) -> list:
        result = self.tagged_cache_handler.tagged_cache_list
        return TaggedCacheFilter.filter_by_wildcard_tag(result, target='true')

    def get_eng_char_results(self) -> list:
        result = self.tagged_cache_handler.tagged_cache_list
        return TaggedCacheFilter.filter_by_eng_chars_tag(result, target='true')

    def get_typo_char_results(self) -> list:
        result = self.tagged_cache_handler.tagged_cache_list
        return TaggedCacheFilter.filter_by_typo_chars_tag(result, target='true')

    def get_garbage_char_results(self) -> list:
        result = self.tagged_cache_handler.tagged_cache_list
        return TaggedCacheFilter.filter_by_garbage_chars_tag_group(result, target='true')

    def get_nongarbage_results(self):
        result = self.tagged_cache_handler.tagged_cache_list
        return TaggedCacheFilter.filter_by_garbage_chars_tag_group(result, target='false')

    def get_hiragana_tag_results(self, tag: str):
        """
        tag options: 'none', 'partial', 'all'
        """
        result = self.get_nongarbage_results()
        return TaggedCacheFilter.filter_by_hiragana_tag(result, target=tag)

    def get_katakana_tag_results(self, tag: str):
        """
        tag options: 'none', 'partial', 'all'
        """
        result = self.get_nongarbage_results()
        return TaggedCacheFilter.filter_by_katakana_tag(result, target=tag)

    def get_kanji_tag_results(self, tag: str):
        """
        tag options: 'none', 'partial', 'all'
        """
        result = self.get_nongarbage_results()
        return TaggedCacheFilter.filter_by_kanji_tag(result, target=tag)