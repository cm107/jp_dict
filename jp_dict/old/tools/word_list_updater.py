import requests, pickle
from bs4 import BeautifulSoup
from logger import logger
from common_utils.file_utils import file_exists
from ..lib.history_parsing.cache import Cache, SearchWordCacheHandler
from ..lib.history_parsing.history_parser import HistoryParser
from qtpy.QtCore import Signal

class WordListUpdater:
    def __init__(self, history_json_path: str, save_file_path: str):
        self.save_file_path = save_file_path
        history_parser = HistoryParser(history_json_path=history_json_path)
        history_parser.load()
        self.relevant_times, self.relevant_urls = history_parser.get_urls_that_start_with('https://jisho.org/search')

        self.search_word_cache_handler = None
        if not file_exists(save_file_path):
            self.search_word_cache_handler = SearchWordCacheHandler()
        else:
            cache_dict = pickle.load(open(save_file_path, 'rb'))
            self.search_word_cache_handler = cache_dict['search_word_cache_handler']

        self.current_index = None

    def is_done(self) -> bool:
        return self.current_index == len(self.relevant_urls) - 1

    def step(self, message_sig: Signal=None) -> bool:
        if self.current_index is None:
            if len(self.relevant_urls) == 0:
                if message_sig is None:
                    logger.warning(f"No relevant urls found.")
                else:
                    message_sig.emit(f"\nNo relevant urls found.")
                return True
            self.current_index = 0
        else:
            self.current_index += 1

        time_usec, url = self.relevant_times[self.current_index], self.relevant_urls[self.current_index]

        found, duplicate = self.search_word_cache_handler.check_url(url=url, time_usec=time_usec)
        if not found:
            response = requests.get(url)
            if response.status_code != 200:
                if message_sig is None:
                    logger.warning(f"Encountered status_code: {response.status_code}")
                    logger.warning(f"Skipping {url}")
                else:
                    message_sig.emit(f"\nEncountered status_code: {response.status_code}")
                    message_sig.emit(f"\nSkipping {url}")
                return self.is_done()
            soup = BeautifulSoup(response.text, 'html.parser')
            search_word = soup.title.text.split('-')[0][:-1]
            if message_sig is None:
                logger.blue(f"{self.current_index}: {search_word}")
            else:
                message_sig.emit(f"\n{self.current_index}: {search_word}")
            url_word_pair = {'url': url, 'search_word': search_word}
            self.search_word_cache_handler.process(item=url_word_pair, time_usec=time_usec, item_key='url')
        else:
            if not duplicate:
                if message_sig is None:
                    logger.yellow(f"{self.current_index}: URL already in cache (hit) - {url}")
                else:
                    message_sig.emit(f"\n{self.current_index}: URL already in cache (hit) - {url}")
            else:
                if message_sig is None:
                    logger.yellow(f"{self.current_index}: Duplicate found in cache (no hit) - {url}")
                else:
                    message_sig.emit(f"\n{self.current_index}: Duplicate found in cache (no hit) - {url}")
        cache_dict = {}
        cache_dict['search_word_cache_handler'] = self.search_word_cache_handler
        pickle.dump(cache_dict, open(self.save_file_path, 'wb'))
        return self.is_done()

    def run(self, app=None):
        done = False
        while not done:
            done = self.step()

            if app is not None:
                app.processEvents()