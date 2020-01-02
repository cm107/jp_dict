from __future__ import annotations
from abc import ABCMeta, abstractmethod
from logger import logger
from ..cache import Cache
from ....util.char_lists import wild_cards, eng_chars, typo_chars, \
    hiragana_chars, katakana_chars, misc_kana_chars, space_chars

class TaggedCache(metaclass=ABCMeta):
    def __init__(self, cache: Cache):
        self.cache = cache
        self.search_word, self.url = self.get_search_word_and_url(cache=cache)
        self.hit_count = cache.hit_count
        self.times_usec = cache.times_usec
        self.newest_time_usec = max(cache.times_usec)
        self.oldest_time_usec = min(cache.times_usec)

        # Garbage Character Tags
        self.contains_wildcard = None
        self.contains_eng_chars = None
        self.contains_typo_chars = None
        self.contains_space = None

        # Japanese Character Tags
        self.hiragana_tag = None
        self.katakana_tag = None
        self.kanji_tag = None

        # Word Results
        self.word_results = []

    def __str__(self):
        print_str = f"Word: {self.search_word}, Hits: {self.hit_count}, "
        print_str += f"Garbage: [{self.contains_wildcard}, {self.contains_eng_chars}, {self.contains_typo_chars}, {self.contains_space}], "
        print_str += f"Japanese: [{self.hiragana_tag}, {self.katakana_tag}, {self.kanji_tag}]"
        return print_str

    def __repr__(self):
        return self.__str__()

    @classmethod
    @abstractmethod
    def buffer(self, tagged_cache: TaggedCache) -> TaggedCache:
        return tagged_cache

    @abstractmethod
    def copy(self) -> TaggedCache:
        return TaggedCache(cache=self.cache)

    @abstractmethod
    def get_search_word_and_url(self, cache: Cache) -> (str, str):
        ''' To override '''
        raise NotImplementedError

    def is_not_processed_for_garbage_chars_yet(self) -> bool:
        return self.contains_wildcard is None \
            or self.contains_eng_chars is None \
            or self.contains_typo_chars is None \
            or self.contains_space is None

    def is_garbage_word(self) -> bool:
        return self.contains_wildcard or self.contains_eng_chars or self.contains_typo_chars or self.contains_space

    def is_not_processed_for_japanese_chars_yet(self) -> bool:
        return self.hiragana_tag is None \
            or self.katakana_tag is None \
            or self.kanji_tag is None

    def is_not_processed_for_word_results_yet(self) -> bool:
        return self.word_results is None

    def register_word_results(self, word_results: list):
        self.word_results = word_results

class TaggedCacheHandler(metaclass=ABCMeta):
    def __init__(self):
        self.tagged_cache_list = []

    @abstractmethod
    def add(self, tagged_cache: TaggedCache):
        ''' To override '''
        raise NotImplementedError

    @abstractmethod
    def add_from_cache(self, cache: Cache):
        ''' To override '''
        raise NotImplementedError

    def tag_wildcards(self, start_from: int=None, verbose: bool=False):
        for i, tagged_cache in enumerate(self.tagged_cache_list):
            if start_from is not None and i < start_from:
                if verbose:
                    logger.info(f"{i}: Wildcard -> Skipped")
                continue
            contains_wildcard = False
            for char in tagged_cache.search_word:
                if char in wild_cards:
                    contains_wildcard = True
                    break
            tagged_cache.contains_wildcard = contains_wildcard
            if verbose:
                logger.info(f"{i}: Wildcards -> {contains_wildcard}")


    def tag_eng_chars(self, start_from: int=None, verbose: bool=False):
        for i, tagged_cache in enumerate(self.tagged_cache_list):
            if start_from is not None and i < start_from:
                if verbose:
                    logger.info(f"{i}: English Characters -> Skipped")
                continue
            contains_eng_chars = False
            for char in tagged_cache.search_word:
                if char in eng_chars:
                    contains_eng_chars = True
                    break
            tagged_cache.contains_eng_chars = contains_eng_chars
            if verbose:
                logger.info(f"{i}: English Characters -> {contains_eng_chars}")

    def tag_typo_chars(self, start_from: int=None, verbose: bool=False):
        for i, tagged_cache in enumerate(self.tagged_cache_list):
            if start_from is not None and i < start_from:
                if verbose:
                    logger.info(f"{i}: Typos -> Skipped")
                continue
            contains_typo_chars = False
            for char in tagged_cache.search_word:
                if char in typo_chars:
                    contains_typo_chars = True
                    break
            tagged_cache.contains_typo_chars = contains_typo_chars
            if verbose:
                logger.info(f"{i}: Typos -> {contains_typo_chars}")

    def tag_spaces(self, start_from: int=None, verbose: bool=False):
        for i, tagged_cache in enumerate(self.tagged_cache_list):
            if start_from is not None and i < start_from:
                if verbose:
                    logger.info(f"{i}: Spaces -> Skipped")
                continue
            contains_space = False
            for char in tagged_cache.search_word:
                if char in space_chars:
                    contains_space = True
                    break
            tagged_cache.contains_space = contains_space
            if verbose:
                logger.info(f"{i}: Spaces -> {contains_space}")

    def tag_garbage_characters(self, start_from: int=None, verbose: bool=False):
        self.tag_wildcards(start_from=start_from, verbose=verbose)
        self.tag_eng_chars(start_from=start_from, verbose=verbose)
        self.tag_typo_chars(start_from=start_from, verbose=verbose)
        self.tag_spaces(start_from=start_from, verbose=verbose)

    def tag_japanese_chars(self, start_from: int=None, verbose: bool=False):
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
        for i, tagged_cache in enumerate(self.tagged_cache_list):
            if start_from is not None and i < start_from:
                if verbose:
                    logger.info(f"{i}: Japanese Characters -> Skipped")
                continue
            # Confirm Word Doesn't Contain Garbage Characters
            if tagged_cache.is_not_processed_for_garbage_chars_yet():
                logger.error(f"The following tagged_cache has not been processed for garbage yet.")
                logger.error(tagged_cache)
                raise Exception
            if tagged_cache.is_garbage_word():
                if verbose:
                    logger.info(f"{i}: Japanese Characters -> Skipped because garbage")
                continue

            # Count Japanese Characters
            hiragana_count = 0
            katakana_count = 0
            kanji_count = 0
            prev_char = None
            for char in tagged_cache.search_word:
                if char in hiragana_chars:
                    hiragana_count += 1
                elif char in katakana_chars:
                    katakana_count += 1
                elif char in misc_kana_chars:
                    if prev_char is None:
                        logger.error(f"Encountered miscellaneous character {char} with no preceeding character.")
                        logger.error(tagged_cache.search_word)
                        raise Exception
                    if prev_char in hiragana_chars:
                        hiragana_count += 1
                    elif prev_char in katakana_chars:
                        katakana_count += 1
                    else:
                        logger.error(f"Miscellaneous character {char} follows a non-kana character:")
                        logger.error(tagged_cache.search_word)
                        raise Exception
                else:
                    kanji_count += 1
                prev_char = char

            # Assign Hiragana Tag
            if hiragana_count == 0:
                tagged_cache.hiragana_tag = 'none'
            elif hiragana_count < len(tagged_cache.search_word):
                tagged_cache.hiragana_tag = 'partial'
            else:
                tagged_cache.hiragana_tag = 'all'
            
            # Assign Katakana Tag
            if katakana_count == 0:
                tagged_cache.katakana_tag = 'none'
            elif katakana_count < len(tagged_cache.search_word):
                tagged_cache.katakana_tag = 'partial'
            else:
                tagged_cache.katakana_tag = 'all'

            # Assign Kanji Tag
            if kanji_count == 0:
                tagged_cache.kanji_tag = 'none'
            elif kanji_count < len(tagged_cache.search_word):
                tagged_cache.kanji_tag = 'partial'
            else:
                tagged_cache.kanji_tag = 'all'
            if verbose:
                logger.info(f"{i}: Japanese Characters -> Hiragana={tagged_cache.hiragana_tag}")
                logger.info(f"{i}: Japanese Characters -> Katakana={tagged_cache.katakana_tag}")
                logger.info(f"{i}: Japanese Characters -> Kanji={tagged_cache.kanji_tag}")
