#%%
from src.tools.word_search.jisho_word_search import JishoWordSearch
from logger import logger

search_words = ['日', '取り扱い', '未亡人', '修羅場']
results = {}

word_search = JishoWordSearch()
for search_word in search_words:
    matching_results = word_search.scrape_word_matches(
        search_word=search_word,
        page_limit=1
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