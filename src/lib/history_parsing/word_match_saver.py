import pickle

from logger import logger
from common_utils.file_utils import file_exists
from common_utils.check_utils import check_file_exists

from ...tools.word_search.jisho_word_search import JishoSoupWordSearch
from ...conf.paths import PathConf
from .filter.soup_cache_filter import SoupCacheFilter
from .cache import SoupCacheHandler

def soup_cache_handler_buffer(handler: SoupCacheHandler) -> SoupCacheHandler:
    return handler

class SoupWordMatchSaver:
    def __init__(
        self, progress_save_path: str=f"{PathConf.jisho_soup_root_dir}/progress.pth",
        word_matches_save_path: str=f"{PathConf.word_matches_save_dir}/soup_test.pkl"
    ):
        check_file_exists(progress_save_path)
        progress_dict = pickle.load(open(progress_save_path, 'rb'))
        cache_handler = progress_dict['cache_handler']
        cache_handler = soup_cache_handler_buffer(cache_handler)

        self.word_filter = SoupCacheFilter(
            cache_list=cache_handler.cache_list,
        )
        self.word_search = JishoSoupWordSearch()
        self.word_matches_save_path = word_matches_save_path
        if not file_exists(self.word_matches_save_path):
            self.results = []
        else:
            self.results = pickle.load(open(word_matches_save_path, 'rb'))

    def run(self):
        previous_url = None

        for i in range(len(self.word_filter.cache_list)):
            if i < len(self.results):
                logger.cyan(f"===Index: {i} - Found in cache. Skipping.===")
                continue
            else:
                logger.cyan(f"============Index: {i}======================")
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
                matching_results = self.word_search.scrape_word_matches(
                    search_word=search_word,
                    soup_dir=PathConf.jisho_soup_root_dir
                )
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
            pickle.dump(self.results, open(self.word_matches_save_path, 'wb'))