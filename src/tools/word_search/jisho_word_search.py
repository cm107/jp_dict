from .jisho_word_search_core import JishoWordSearchCore

class JishoWordSearch(JishoWordSearchCore):
    def __init__(self):
        super().__init__()

    def scrape_word_matches(self, search_word: str, page_limit: int=1) -> list:
        self.reset()
        self.search(
            search_word=search_word,
            page_limit=page_limit,
            silent=True
        )
        self.word_result_handler.find_matches(
            search_word=search_word,
            verbose=False
        )
        return self.word_result_handler.matching_results