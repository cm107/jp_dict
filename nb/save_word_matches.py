import pickle
from src.submodules.logger.logger_handler import logger
from src.submodules.common_utils.file_utils import file_exists
from src.util.loaders import load_search_word_cache_handler
from src.lib.history_parsing.search_word_cache_filter import SearchWordCacheFilter
from src.tools.word_search.jisho_word_search import JishoWordSearch
from src.conf.paths import PathConf

word_matches_save_path = f"{PathConf.word_matches_save_dir}/test.pkl"
search_word_cache_handler = load_search_word_cache_handler(PathConf.jisho_history_word_list_save_path)
word_filter = SearchWordCacheFilter(
    cache_list=search_word_cache_handler.cache_list,
)
word_filter.apply_tags()
words = word_filter.get_nongarbage_results()

results = None
if not file_exists(word_matches_save_path):
    results = {}
else:
    results = pickle.load(open(word_matches_save_path, 'rb'))

word_search = JishoWordSearch()

for i, word in zip(range(len(words)), words):
    search_word = word.search_word
    url = word.url
    if i < len(results) and search_word in results:
        logger.cyan(f"===Index: {i} - Found in cache. Skipping.===")
        continue
    else:
        logger.cyan(f"============Index: {i}======================")

    logger.cyan(f"Search Word: {search_word}")
    logger.cyan(f"URL: {url}")
    matching_results = word_search.scrape_word_matches(
        search_word=search_word,
        page_limit=1
    )
    results[search_word] = matching_results

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
    