from src.submodules.logger.logger_handler import logger
from src.util.loaders import load_search_word_cache_handler
from src.lib.history_parsing.search_word_cache_filter import SearchWordCacheFilter
from src.tools.word_search.jisho_word_search import JishoWordSearch
from src.conf.paths import PathConf

search_word_cache_handler = load_search_word_cache_handler(PathConf.jisho_history_word_list_save_path)
word_filter = SearchWordCacheFilter(
    cache_list=search_word_cache_handler.cache_list,
)
word_filter.apply_tags()
words = word_filter.get_nongarbage_results()

results = {}
word_search = JishoWordSearch()
for word in words:
    search_word = word.search_word
    url = word.url
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