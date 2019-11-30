from abc import ABCMeta, abstractmethod
import pickle

from logger import logger
from common_utils.file_utils import file_exists
from common_utils.check_utils import check_file_exists

from ...tools.word_search.jisho_word_search import JishoSoupWordSearch, JishoUrlWordSearch
from ...conf.paths import PathConf
from .filter.core import CacheFilter
from .filter.soup_cache_filter import SoupCacheFilter
from .filter.search_word_cache_filter import SearchWordCacheFilter
from .cache import CacheHandler

class WordMatchSaver(metaclass=ABCMeta):
    def __init__(self, cache_save_path: str, word_matches_save_path: str, cache_handler_key: str):
        cache_handler = self._load_cache_handler(
            cache_save_path=cache_save_path,
            key=cache_handler_key
        )

        self.word_matches_save_path = word_matches_save_path
        self.results, self.word_filter = self._load_checkpoint(
            word_matches_save_path=self.word_matches_save_path,
            cache_handler=cache_handler
        )

    def _load_cache_handler(self, cache_save_path: str, key: str) -> CacheHandler:
        check_file_exists(cache_save_path)
        cache_dict = pickle.load(open(cache_save_path, 'rb'))
        cache_handler = cache_dict[key]
        return cache_handler

    def _load_checkpoint(self, word_matches_save_path: str, cache_handler: CacheHandler) -> (list, CacheFilter):
        if not file_exists(self.word_matches_save_path):
            results = []
            word_filter = CacheFilter(
                cache_list=cache_handler.cache_list,
            )
        else:
            checkpoint = pickle.load(open(word_matches_save_path, 'rb'))
            results = checkpoint['results']
            word_filter = checkpoint['word_filter']
        return results, word_filter

    def _save_checkpoint(self, results: list, word_filter: CacheFilter):
        checkpoint = {
            'results': results,
            'word_filter': word_filter
        }
        pickle.dump(checkpoint, open(self.word_matches_save_path, 'wb'))

    @abstractmethod
    def scrape_word_matches(self, search_word: str) -> list:
        ''' To override '''
        raise NotImplementedError

    @abstractmethod
    def get_word_filter(self) -> CacheFilter:
        ''' To override '''
        raise NotImplementedError

    def run(self):
        previous_url = None

        for i in range(len(self.word_filter.cache_list)):
            if i < len(self.results):
                logger.cyan(f"===Word {i+1}/{len(self.word_filter.cache_list)} - Found in cache. Skipping.===")
                self.word_filter.load_index = i
                continue
            else:
                logger.cyan(f"============Word {i+1}/{len(self.word_filter.cache_list)}======================")
            self.word_filter.load_tagged_cache_handler(batch_size=1)
            self.word_filter.apply_tags(start_from=self.word_filter.load_index)
            word = self.word_filter.tagged_cache_handler.tagged_cache_list[-1]
            logger.green(word)
            search_word = word.search_word
            url = word.url
            if previous_url is None:
                previous_url = url
            else:
                if previous_url == url:
                    logger.error(f"Was about to add the same url twice for search_word: {search_word}")
                    logger.error(f"url: {url}")
                    raise Exception
                else:
                    previous_url = url
            logger.cyan(f"Search Word: {search_word}")
            logger.cyan(f"URL: {url}")
            if not word.is_garbage_word():
                matching_results = self.scrape_word_matches(search_word=search_word)
            else:
                matching_results = []
            self.results.append({'search_word': search_word, 'matching_results': matching_results})
            logger.yellow('================================')
            logger.purple(search_word)
            logger.yellow('================================')
            if len(matching_results) > 0:
                for i, matching_word in zip(range(len(matching_results)), matching_results):
                    if i > 0:
                        logger.yellow('--------------------------------')
                    logger.green(matching_word)
            else:
                logger.red("No matching results found.")
            self._save_checkpoint(results=self.results, word_filter=self.word_filter)

class SoupWordMatchSaver(WordMatchSaver):
    def __init__(
        self,
        cache_save_path: str=f"{PathConf.jisho_soup_root_dir}/progress.pth",
        word_matches_save_path: str=f"{PathConf.word_matches_save_dir}/soup_test.pkl"
    ):
        super().__init__(
            cache_save_path=cache_save_path,
            word_matches_save_path=word_matches_save_path,
            cache_handler_key='cache_handler'
        )
        self.word_search = JishoSoupWordSearch()

    def scrape_word_matches(self, search_word: str) -> list:
        return self.word_search.scrape_word_matches(
            search_word=search_word,
            soup_dir=PathConf.jisho_soup_root_dir
        )

    def get_word_filter(self) -> SoupCacheFilter:
        return self.word_filter

class SearchWordMatchSaver(WordMatchSaver):
    def __init__(
        self,
        cache_save_path: str=f"{PathConf.jisho_history_word_list_save_path}",
        word_matches_save_path: str=f"{PathConf.word_matches_save_dir}/test.pkl"
    ):
        super().__init__(
            cache_save_path=cache_save_path,
            word_matches_save_path=word_matches_save_path,
            cache_handler_key='search_word_cache_handler'
        )
        self.word_search = JishoUrlWordSearch()

    def scrape_word_matches(self, search_word: str) -> list:
        return self.word_search.scrape_word_matches(
            search_word=search_word,
            page_limit=1
        )

    def get_word_filter(self) -> SearchWordCacheFilter:
        return self.word_filter