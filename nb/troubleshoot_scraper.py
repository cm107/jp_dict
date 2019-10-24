from logger import logger
from src.tools.word_search.jisho_word_search import JishoWordSearch

nominal_word = '日常'
no_results_word = 'おいやれる'
problematic_word = 'ブルう'
problematic_url = 'https://jisho.org/search/%E3%83%96%E3%83%AB%E3%81%86'

test_words = [nominal_word, problematic_word, no_results_word]

word_search = JishoWordSearch()
for word in test_words:
    logger.cyan(f"Word: {word}")
    matching_results = word_search.scrape_word_matches(
        search_word=word,
        page_limit=1
    )
    logger.green(matching_results)