import requests, pickle
from bs4 import BeautifulSoup
from ..submodules.logger.logger_handler import logger
from ..submodules.common_utils.file_utils import file_exists
from ..lib.history_parsing.cache import Cache, CacheHandler
from ..lib.history_parsing.history_parser import HistoryParser

class PrintTest:
    def __init__(self):
        pass

    def test(self):
        print("=======================This is a test.===============================")

class WordListUpdater:
    def __init__(self, history_json_path: str, save_file_path: str):
        self.save_file_path = save_file_path
        history_parser = HistoryParser(history_json_path=history_json_path)
        history_parser.load()
        self.relevant_times, self.relevant_urls = history_parser.get_urls_that_start_with('https://jisho.org/search')

        self.search_word_cache_handler = None
        if not file_exists(save_file_path):
            self.search_word_cache_handler = CacheHandler()
        else:
            cache_dict = pickle.load(open(save_file_path, 'rb'))
            self.search_word_cache_handler = cache_dict['search_word_cache_handler']

    def run(self):
        for i, time_usec, url in zip(range(len(self.relevant_urls)), self.relevant_times, self.relevant_urls):
            found, duplicate = self.search_word_cache_handler.check_url(url=url, time_usec=time_usec)
            if not found:
                response = requests.get(url)
                if response.status_code != 200:
                    logger.warning(f"Encountered status_code: {response.status_code}")
                    logger.warning(f"Skipping {url}")
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')
                search_word = soup.title.text.split('-')[0][:-1]
                logger.blue(f"{i}: {search_word}")
                url_word_pair = {'url': url, 'search_word': search_word}
                self.search_word_cache_handler.process(item=url_word_pair, time_usec=time_usec, item_key='url')
            else:
                if not duplicate:
                    logger.yellow(f"{i}: URL already in cache (hit) - {url}")
                else:
                    logger.yellow(f"{i}: Duplicate found in cache (no hit) - {url}")
            cache_dict = {}
            cache_dict['search_word_cache_handler'] = self.search_word_cache_handler
            pickle.dump(cache_dict, open(self.save_file_path, 'wb'))