from ...submodules.logger.logger_handler import logger
from ...submodules.common_utils.check_utils import check_type_from_list
from .cache import Cache
from ...util.char_lists import wild_cards, eng_chars, typo_chars, \
    hiragana_chars, katakana_chars, misc_kana_chars

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

        # Garbage Character Tags
        self.contains_wildcard = None
        self.contains_eng_chars = None
        self.contains_typo_chars = None

        # Japanese Character Tags
        self.hiragana_tag = None
        self.katakana_tag = None
        self.kanji_tag = None

    def __str__(self):
        print_str = f"Word: {self.search_word}, Hits: {self.hit_count}, "
        print_str += f"Garbage: [{self.contains_wildcard}, {self.contains_eng_chars}, {self.contains_typo_chars}], "
        print_str += f"Japanese: [{self.hiragana_tag}, {self.katakana_tag}, {self.kanji_tag}]"
        return print_str

    def __repr__(self):
        return self.__str__()

    def is_not_processed_for_garbage_chars_yet(self):
        return self.contains_wildcard is None \
            or self.contains_eng_chars is None \
            or self.contains_typo_chars is None

    def is_garbage_word(self):
        return self.contains_wildcard or self.contains_eng_chars or self.contains_typo_chars

    def is_not_processed_for_japanese_chars_yet(self):
        return self.hiragana_tag is None \
            or self.katakana_tag is None \
            or self.kanji_tag is None

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

    def tag_garbage_characters(self):
        self.tag_wildcards()
        self.tag_eng_chars()
        self.tag_typo_chars()

    def tag_japanese_chars(self):
        """
        Assumes garbage tags have already been assigned.
        Ignores all garbage tagged words.
        Assumes that all non-garbage tagged words are composed
        entirely of hiragana, katakana, and kanji characters.
        Any characters that are not hiragana or katakana characters
        are assumed to be kanji characters.
        If there are any garbage characters in the word that haven't
        been accounted for in garbage tagging, they will be counted
        as kanji.
        """
        for tagged_word_cache in self.tagged_word_cache_list:
            # Confirm Word Doesn't Contain Garbage Characters
            if tagged_word_cache.is_not_processed_for_garbage_chars_yet():
                logger.error(f"The following tagged_word_cache has not been processed for garbage yet.")
                logger.error(tagged_word_cache)
                raise Exception
            if tagged_word_cache.is_garbage_word():
                continue

            # Count Japanese Characters
            hiragana_count = 0
            katakana_count = 0
            kanji_count = 0
            prev_char = None
            for char in tagged_word_cache.search_word:
                if char in hiragana_chars:
                    hiragana_count += 1
                elif char in katakana_chars:
                    katakana_count += 1
                elif char in misc_kana_chars:
                    if prev_char is None:
                        logger.error(f"Encountered miscellaneous character {char} with no preceeding character.")
                        logger.error(tagged_word_cache.search_word)
                        raise Exception
                    if prev_char in hiragana_chars:
                        hiragana_count += 1
                    elif prev_char in katakana_chars:
                        katakana_count += 1
                    else:
                        logger.error(f"Miscellaneous character {char} follows a non-kana character:")
                        logger.error(tagged_word_cache.search_word)
                        raise Exception
                else:
                    kanji_count += 1
                prev_char = char

            # Assign Hiragana Tag
            if hiragana_count == 0:
                tagged_word_cache.hiragana_tag = 'none'
            elif hiragana_count < len(tagged_word_cache.search_word):
                tagged_word_cache.hiragana_tag = 'partial'
            else:
                tagged_word_cache.hiragana_tag = 'all'
            
            # Assign Katakana Tag
            if katakana_count == 0:
                tagged_word_cache.katakana_tag = 'none'
            elif katakana_count < len(tagged_word_cache.search_word):
                tagged_word_cache.katakana_tag = 'partial'
            else:
                tagged_word_cache.katakana_tag = 'all'

            # Assign Kanji Tag
            if kanji_count == 0:
                tagged_word_cache.kanji_tag = 'none'
            elif kanji_count < len(tagged_word_cache.search_word):
                tagged_word_cache.kanji_tag = 'partial'
            else:
                tagged_word_cache.kanji_tag = 'all'

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
    def filter_by_garbage_chars_tag_group(self, tagged_word_cache_list: list, target: str) -> list:
        self.check_invalid_target('bool', target)
        result = []
        for tagged_word_cache in tagged_word_cache_list:
            if tagged_word_cache.is_not_processed_for_japanese_chars_yet() is None and target == 'none':
                result.append(tagged_word_cache)
            elif tagged_word_cache.is_garbage_word() and target == 'true':
                result.append(tagged_word_cache)
            elif not tagged_word_cache.is_garbage_word() and target == 'false':
                result.append(tagged_word_cache)
        return result

    @classmethod
    def filter_by_hiragana_tag(self, tagged_word_cache_list: list, target: str) -> list:
        self.check_invalid_target('char', target)
        result = []
        for tagged_word_cache in tagged_word_cache_list:
            if tagged_word_cache.is_not_processed_for_japanese_chars_yet():
                logger.error(f"tagged_word_cache not labeled:\n{tagged_word_cache}")
                raise Exception
            if tagged_word_cache.hiragana_tag == target:
                result.append(tagged_word_cache)
        return result

    @classmethod
    def filter_by_katakana_tag(self, tagged_word_cache_list: list, target: str) -> list:
        self.check_invalid_target('char', target)
        result = []
        for tagged_word_cache in tagged_word_cache_list:
            if tagged_word_cache.is_not_processed_for_japanese_chars_yet():
                logger.error(f"tagged_word_cache not labeled:\n{tagged_word_cache}")
                raise Exception
            if tagged_word_cache.katakana_tag == target:
                result.append(tagged_word_cache)
        return result

    @classmethod
    def filter_by_kanji_tag(self, tagged_word_cache_list: list, target: str) -> list:
        self.check_invalid_target('char', target)
        result = []
        for tagged_word_cache in tagged_word_cache_list:
            if tagged_word_cache.is_not_processed_for_japanese_chars_yet():
                logger.error(f"tagged_word_cache not labeled:\n{tagged_word_cache}")
                raise Exception
            if tagged_word_cache.kanji_tag == target:
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
        self.tagged_word_cache_handler.tag_garbage_characters()
        self.tagged_word_cache_handler.tag_japanese_chars()

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

    def get_garbage_char_results(self) -> list:
        result = self.tagged_word_cache_handler.tagged_word_cache_list
        return TagFilter.filter_by_garbage_chars_tag_group(result, target='true')

    def get_nongarbage_results(self):
        result = self.tagged_word_cache_handler.tagged_word_cache_list
        return TagFilter.filter_by_garbage_chars_tag_group(result, target='false')

    def get_hiragana_tag_results(self, tag: str):
        """
        tag options: 'none', 'partial', 'all'
        """
        result = self.get_nongarbage_results()
        return TagFilter.filter_by_hiragana_tag(result, target=tag)

    def get_katakana_tag_results(self, tag: str):
        """
        tag options: 'none', 'partial', 'all'
        """
        result = self.get_nongarbage_results()
        return TagFilter.filter_by_katakana_tag(result, target=tag)

    def get_kanji_tag_results(self, tag: str):
        """
        tag options: 'none', 'partial', 'all'
        """
        result = self.get_nongarbage_results()
        return TagFilter.filter_by_kanji_tag(result, target=tag)
