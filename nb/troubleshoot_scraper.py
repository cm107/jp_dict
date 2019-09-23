from src.submodules.logger.logger_handler import logger
from src.tools.word_search.jisho_word_search import JishoWordSearch

problematic_word = 'ブルう'
problematic_url = 'https://jisho.org/search/%E3%83%96%E3%83%AB%E3%81%86'

word_search = JishoWordSearch()
matching_results = word_search.scrape_word_matches(
    search_word=problematic_word,
    page_limit=1
)

logger.green(matching_results)