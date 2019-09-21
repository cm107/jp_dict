from ...submodules.logger.logger_handler import logger
from ...submodules.common_utils.check_utils import check_type_from_list
from .cache import Cache
from ...util.char_lists import wild_cards, eng_chars, typo_chars, \
    hiragana_chars, katakana_chars

class TaggedWordCache:
    def __init__(self, word_cache: Cache):
        if 'url' not in word_cache.item:
            logger.error(f"'url' not found in word_cache.item")
            logger.error(f"This is not a word cache.")
            raise Exception
        if 'search_word' not in word_cache.item:
            logger.error(f"'search_word' not found in word_cache.item")
            logger.error(f"This is not a word cache.")
            raise Exception
        self.search_word = word_cache.item['search_word']
        self.url = word_cache.item['url']
        self.hit_count = word_cache.hit_count
        self.times_usec = word_cache.times_usec

        self.contains_wildcard = None
        self.contains_eng_chars = None
        self.contains_typo_chars = None
        self.hiragana_tag = None
        self.katakana_tag = None

    def __str__(self):
        return f"Word: {self.search_word}, Hits: {self.hit_count}"

    def __repr__(self):
        return self.__str__()

class TaggedWordCacheHandler:
    def __init__(self):
        self.tagged_word_cache_list = []

    def add(self, tagged_word_cache: TaggedWordCache):
        self.tagged_word_cache_list.append(tagged_word_cache)

    def add_from_word_cache(self, word_cache: Cache):
        self.add(TaggedWordCache(word_cache))

    def tag_wildcards(self):
        for tagged_word_cache in self.tagged_word_cache_list:
            contains_wildcard = False
            for char in tagged_word_cache.search_word:
                if char in wild_cards:
                    contains_wildcard = True
                    break
            tagged_word_cache.contains_wildcard = contains_wildcard

    def tag_eng_chars(self):
        for tagged_word_cache in self.tagged_word_cache_list:
            contains_eng_chars = False
            for char in tagged_word_cache.search_word:
                if char in eng_chars:
                    contains_eng_chars = True
                    break
            tagged_word_cache.contains_eng_chars = contains_eng_chars

    def tag_typo_chars(self):
        for tagged_word_cache in self.tagged_word_cache_list:
            contains_typo_chars = False
            for char in tagged_word_cache.search_word:
                if char in typo_chars:
                    contains_typo_chars = True
                    break
            tagged_word_cache.contains_typo_chars = contains_typo_chars

    def tag_hiragana_chars(self):
        for tagged_word_cache in self.tagged_word_cache_list:
            hiragana_count = 0
            for char in tagged_word_cache.search_word:
                if char in hiragana_chars:
                    hiragana_count += 1
            if hiragana_count == 0:
                tagged_word_cache.hiragana_tag = 'none'
            elif hiragana_count < len(tagged_word_cache.search_word):
                tagged_word_cache.hiragana_tag = 'partial'
            else:
                tagged_word_cache.hiragana_tag = 'all'

    def tag_katakana_chars(self):
        for tagged_word_cache in self.tagged_word_cache_list:
            katakana_count = 0
            for char in tagged_word_cache.search_word:
                if char in katakana_chars:
                    katakana_count += 1
            if katakana_count == 0:
                tagged_word_cache.katakana_tag = 'none'
            elif katakana_count < len(tagged_word_cache.search_word):
                tagged_word_cache.katakana_tag = 'partial'
            else:
                tagged_word_cache.katakana_tag = 'all'

class TagFilter:
    @classmethod
    def check_invalid_target(self, category: str, target: str):
        if category == 'bool':
            if target not in ['true', 'false', 'none']:
                logger.error(f"Invalid target for category {category}: {target}")
                raise Exception
        elif category == 'char':
            if target not in ['all', 'partial', 'none']:
                logger.error(f"Invalid target for category {category}: {target}")
                raise Exception

    @classmethod
    def filter_by_wildcard_tag(self, tagged_word_cache_list: list, target: str) -> list:
        self.check_invalid_target('bool', target)
        result = []
        for tagged_word_cache in tagged_word_cache_list:
            if tagged_word_cache.contains_wildcard is None and target == 'none':
                result.append(tagged_word_cache)
            elif tagged_word_cache.contains_wildcard and target == 'true':
                result.append(tagged_word_cache)
            elif not tagged_word_cache.contains_wildcard and target == 'false':
                result.append(tagged_word_cache)
        return result

    @classmethod
    def filter_by_eng_chars_tag(self, tagged_word_cache_list: list, target: str) -> list:
        self.check_invalid_target('bool', target)
        result = []
        for tagged_word_cache in tagged_word_cache_list:
            if tagged_word_cache.contains_eng_chars is None and target == 'none':
                result.append(tagged_word_cache)
            elif tagged_word_cache.contains_eng_chars and target == 'true':
                result.append(tagged_word_cache)
            elif not tagged_word_cache.contains_eng_chars and target == 'false':
                result.append(tagged_word_cache)
        return result

    @classmethod
    def filter_by_typo_chars_tag(self, tagged_word_cache_list: list, target: str) -> list:
        self.check_invalid_target('bool', target)
        result = []
        for tagged_word_cache in tagged_word_cache_list:
            if tagged_word_cache.contains_typo_chars is None and target == 'none':
                result.append(tagged_word_cache)
            elif tagged_word_cache.contains_typo_chars and target == 'true':
                result.append(tagged_word_cache)
            elif not tagged_word_cache.contains_typo_chars and target == 'false':
                result.append(tagged_word_cache)
        return result

    @classmethod
    def filter_by_hiragana_tag(self, tagged_word_cache_list: list, target: str) -> list:
        self.check_invalid_target('char', target)
        result = []
        for tagged_word_cache in tagged_word_cache_list:
            if tagged_word_cache.contains_eng_chars is None:
                logger.error(f"tagged_word_cache not labeled\n{tagged_word_cache}")
                raise Exception
            elif tagged_word_cache.hiragana_tag == target:
                result.append(tagged_word_cache)
        return result

    @classmethod
    def filter_by_katakana_tag(self, tagged_word_cache_list: list, target: str) -> list:
        self.check_invalid_target('char', target)
        result = []
        for tagged_word_cache in tagged_word_cache_list:
            if tagged_word_cache.contains_eng_chars is None:
                logger.error(f"tagged_word_cache not labeled\n{tagged_word_cache}")
                raise Exception
            elif tagged_word_cache.katakana_tag == target:
                result.append(tagged_word_cache)
        return result

class SearchWordCacheFilter:
    def __init__(self, cache_list: list):
        self.tagged_word_cache_handler = TaggedWordCacheHandler()
        self.load_tagged_word_cached_handler(cache_list)

    def load_tagged_word_cached_handler(self, cache_list: list):
        for cache in cache_list:
            self.tagged_word_cache_handler.add_from_word_cache(cache)

    def apply_tags(self):
        self.tagged_word_cache_handler.tag_wildcards()
        self.tagged_word_cache_handler.tag_eng_chars()
        self.tagged_word_cache_handler.tag_typo_chars()
        self.tagged_word_cache_handler.tag_hiragana_chars()
        self.tagged_word_cache_handler.tag_katakana_chars()

    def get_filtered_results(
        self, no_wildcards: bool=True, no_eng_chars: bool=True, no_typo_chars: bool=True
    ) -> list:
        result = self.tagged_word_cache_handler.tagged_word_cache_list
        if no_wildcards:
            result = TagFilter.filter_by_wildcard_tag(result, target='false')
        if no_eng_chars:
            result = TagFilter.filter_by_eng_chars_tag(result, target='false')
        if no_typo_chars:
            result = TagFilter.filter_by_typo_chars_tag(result, target='false')
        return result

    def get_wildcard_results(self) -> list:
        result = self.tagged_word_cache_handler.tagged_word_cache_list
        return TagFilter.filter_by_wildcard_tag(result, target='true')

    def get_eng_char_results(self) -> list:
        result = self.tagged_word_cache_handler.tagged_word_cache_list
        return TagFilter.filter_by_eng_chars_tag(result, target='true')

    def get_typo_char_results(self) -> list:
        result = self.tagged_word_cache_handler.tagged_word_cache_list
        return TagFilter.filter_by_typo_chars_tag(result, target='true')

    def get_hiragana_tag_results(self, tag: str):
        """
        tag options: 'none', 'partial', 'all'
        """
        result = self.tagged_word_cache_handler.tagged_word_cache_list
        result = self.get_filtered_results(no_wildcards=True, no_eng_chars=True, no_typo_chars=True)
        return TagFilter.filter_by_hiragana_tag(result, target=tag)

    def get_katakana_tag_results(self, tag: str):
        """
        tag options: 'none', 'partial', 'all'
        """
        result = self.tagged_word_cache_handler.tagged_word_cache_list
        result = self.get_filtered_results(no_wildcards=True, no_eng_chars=True, no_typo_chars=True)
        return TagFilter.filter_by_katakana_tag(result, target=tag)

    def get_all_kanji_results(self):
        result = self.tagged_word_cache_handler.tagged_word_cache_list
        result = self.get_filtered_results(no_wildcards=True, no_eng_chars=True, no_typo_chars=True)
        result = TagFilter.filter_by_hiragana_tag(result, target='none')
        result = TagFilter.filter_by_katakana_tag(result, target='none')
        return result
