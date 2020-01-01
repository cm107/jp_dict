from __future__ import annotations
from logger import logger
from ..cache import Cache
from .core import TaggedCache, TaggedCacheHandler
from .core_cache_filter import CacheFilter

class TaggedWordCache(TaggedCache):
    def __init__(self, cache: Cache):
        super().__init__(cache=cache)

    def __str__(self):
        print_str = f"Word: {self.search_word}, Hits: {self.hit_count}, "
        print_str += f"Garbage: [{self.contains_wildcard}, {self.contains_eng_chars}, {self.contains_typo_chars}], "
        print_str += f"Japanese: [{self.hiragana_tag}, {self.katakana_tag}, {self.kanji_tag}]"
        return print_str

    @classmethod
    def buffer(self, tagged_cache: TaggedWordCache) -> TaggedWordCache:
        return tagged_cache

    def copy(self) -> TaggedWordCache:
        return TaggedWordCache(cache=self.cache)

    def get_search_word_and_url(self, cache: Cache) -> (str, str):
        if 'url' not in cache.item:
            logger.error(f"'url' not found in cache.item")
            logger.error(f"This is not a word cache.")
            raise Exception
        if 'search_word' not in cache.item:
            logger.error(f"'search_word' not found in cache.item")
            logger.error(f"This is not a word cache.")
            raise Exception
        search_word = cache.item['search_word']
        url = cache.item['url']
        return search_word, url

class TaggedWordCacheHandler(TaggedCacheHandler):
    def __init__(self):
        super().__init__()

    def add(self, tagged_cache: TaggedWordCache):
        self.tagged_cache_list.append(tagged_cache)

    def add_from_cache(self, cache: Cache):
        self.add(TaggedWordCache(cache))

class SearchWordCacheFilter(CacheFilter):
    def __init__(self, cache_list: list):
        super().__init__(cache_list=cache_list)

    def get_tagged_cache_handler(self) -> TaggedWordCacheHandler:
        return TaggedWordCacheHandler()
