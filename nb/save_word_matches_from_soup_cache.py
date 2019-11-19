import pickle
from logger import logger
from common_utils.file_utils import file_exists
from src.util.loaders import load_search_word_cache_handler
from src.lib.history_parsing.filter.soup_cache_filter import SoupCacheFilter
from src.tools.word_search.jisho_word_search import JishoSoupWordSearch
from src.conf.paths import PathConf
from src.lib.history_parsing.cache import CacheHandler
from common_utils.check_utils import check_file_exists
from src.lib.history_parsing.cache import SoupCacheHandler

def soup_cache_handler_buffer(handler: SoupCacheHandler) -> SoupCacheHandler:
    return handler

# TODO: Introduce soup cache handler
soup_dir = PathConf.jisho_soup_root_dir
progress_save_path = f"{soup_dir}/progress.pth"
check_file_exists(progress_save_path)
progress_dict = pickle.load(open(progress_save_path, 'rb'))
cache_handler = progress_dict['cache_handler']
cache_handler = soup_cache_handler_buffer(cache_handler)

word_filter = SoupCacheFilter(
    cache_list=cache_handler.cache_list,
)
word_filter.apply_tags()
words = word_filter.get_nongarbage_results()

word_matches_save_path = f"{PathConf.word_matches_save_dir}/soup_test.pkl"
results = None
if not file_exists(word_matches_save_path):
    results = []
else:
    results = pickle.load(open(word_matches_save_path, 'rb'))

word_search = JishoSoupWordSearch()

for i, word in zip(range(len(words)), words):
    search_word = word.search_word
    url = word.url
    if i < len(results):
        logger.cyan(f"===Index: {i} - Found in cache. Skipping.===")
        continue
    else:
        logger.cyan(f"============Index: {i}======================")

    logger.cyan(f"Search Word: {search_word}")
    logger.cyan(f"URL: {url}")
    matching_results = word_search.scrape_word_matches(
        search_word=search_word,
        soup_dir=PathConf.jisho_soup_root_dir
    )
    results.append({'search_word': search_word, 'matching_results': matching_results})

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
    pickle.dump(results, open(word_matches_save_path, 'wb'))
    