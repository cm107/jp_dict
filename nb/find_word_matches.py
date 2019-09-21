#%%
from src.tools.word_search.jisho_word_search_core import JishoWordSearchCore
from src.submodules.logger.logger_handler import logger

search_word = '日'

word_search = JishoWordSearchCore()
word_search.search(
    search_word=search_word,
    page_limit=10,
    silent=True
)
#%%
word_search.word_result_handler.find_matches(
    search_word=search_word,
    verbose=False
)
matching_results = word_search.word_result_handler.matching_results
#%%
for i, word in zip(range(len(matching_results)), matching_results):
    logger.yellow(f"==========Matching Result {i+1}==========")
    logger.green(word)
#%%