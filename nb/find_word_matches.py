#%%
from src.tools.word_search import WordSearch
from src.util.word_search_utils import find_matches
from src.submodules.logger.logger_handler import logger

search_word = '日'

word_search = WordSearch()
word_search.search(
    search_word=search_word,
    page_limit=10
)
#%%
matching_results = word_search.word_result_handler.find_matches(
    search_word=search_word,
    verbose=False
)
#%%
for i, word in zip(range(len(matching_results)), matching_results):
    logger.yellow(f"==========Matching Result {i+1}==========")
    logger.green(word)
#%%