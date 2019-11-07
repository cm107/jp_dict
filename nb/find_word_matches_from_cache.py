#%%
from src.tools.word_search.jisho_word_search import JishoSoupWordSearch
from logger import logger
from src.conf.paths import PathConf

search_words = ['がっしり', '秀でる', '窘める', 'やたら', '一概に', '火照る']
results = {}

word_search = JishoSoupWordSearch()
for search_word in search_words:
    matching_results = word_search.scrape_word_matches(
        search_word=search_word,
        soup_dir=PathConf.jisho_soup_root_dir
    )
    results[search_word] = matching_results
#%%
for search_word, matching_words in results.items():
    logger.yellow('================================')
    logger.purple(search_word)
    logger.yellow('================================')
    if len(matching_words) > 0:
        for i, matching_word in zip(range(len(matching_words)), matching_words):
            if i > 0:
                logger.yellow('--------------------------------')
            logger.green(matching_word)
    else:
        logger.red("No matching results found.")
    
#%%