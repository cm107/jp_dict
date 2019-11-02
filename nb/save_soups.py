import pickle
import requests
from bs4 import BeautifulSoup
from logger import logger
from common_utils.file_utils import file_exists
from common_utils.check_utils import check_file_exists
from common_utils.adv_file_utils import get_next_dump_path
from src.lib.history_parsing.cache import SoupCacheHandler
from src.lib.history_parsing.history_parser import HistoryParser

class SaveItem:
    def __init__(self, save_path: str):
        self.save_path = save_path

    def save_exists(self) -> bool:
        return file_exists(self.save_path)

    def load(self) -> object:
        check_file_exists(self.save_path)
        return pickle.load(open(self.save_path, 'rb'))

    def save(self, item: object, overwrite: bool=True):
        if not overwrite and file_exists(self.save_path):
            logger.error(f"overwrite is False and file already exists at: {self.save_path}")
            raise Exception
        pickle.dump(item, open(self.save_path, 'wb'))

class ProgressSave(SaveItem):
    def __init__(self, save_path: str):
        super().__init__(save_path=save_path)

    def load(self) -> dict:
        return super().load()

    def save(self, progress_dict: dict, overwrite: bool=True):
        super().save(item=progress_dict, overwrite=overwrite)

class ProgressTracker:
    def __init__(self, history_json_path_list: list, save_path: str):
        self.history_json_path_list = history_json_path_list
        self.progress_save = ProgressSave(save_path=save_path)
        self.progress_dict = self.load_progress()

    def load_progress(self) -> dict:
        if self.progress_save.save_exists():
            return self.progress_save.load()
        else:
            return {
                'history_json_pathlist': self.history_json_path_list,
                'finished': [],
                'unfinished': self.history_json_path_list[1:],
                'current': self.history_json_path_list[0],
                'current_index': 0
            }

    def update_progress(self, current_json_path: str, index: int, finished: bool=False):
        history_json_pathlist = self.progress_dict['history_json_pathlist']
        finished = self.progress_dict['finished']
        unfinished = self.progress_dict['unfinished']
        current = self.progress_dict['current']
        current_index = self.progress_dict['current_index']
        if finished:
            if current_json_path in history_json_pathlist:
                if current_json_path not in finished:
                    if current_json_path not in unfinished:
                        logger.error(f"Couldn't find {} in unfinished dict.")
                        logger.error(f"unfinished: {unfinished}")
                        raise Exception
                    finished.append(current_json_path)
                    del unfinished[unfinished.index(current_json_path)]
                else:
                    logger.error(f"Encountered finished flag, but {current_Json_path} is already in finished dict.")
                    logger.error(f"finished: {finished}")
                    raise Exception
            else:
                logger.error(f"{current_json_path} not found in history_json_pathlist")
                logger.error(f"history_json_pathlist: {history_json_pathlist}")
                raise Exception
        current = current_json_path
        current_index = index
        new_progress_dict = {
                'history_json_pathlist': history_json_pathlist,
                'finished': finished,
                'unfinished': unfinished,
                'current': current,
                'current_index': current_index
        }
        self.progress_save.save(progress_dict=new_progress_dict, overwrite=True)

class SoupSaveItem(SaveItem):
    def __init__(self, url: str, save_path: str):
        self.url = url
        super().__init__(save_path=save_path)

    def load(self) -> BeautifulSoup:
        return super().load()

    def get_soup(self) -> (int, BeautifulSoup):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser') if response.status_code == 200 else None
        return response.status_code, soup

    def save(self, soup: BeautifulSoup, overwrite: bool=True):
        super().save(item=soup, overwrite=overwrite)

class SoupSaver:
    def __init__(self, history_json_path_list: list, soup_dir: str):
        self.cache_handler = SoupCacheHandler()
        self.history_json_path_list = history_json_path_list
        self.soup_dir = soup_dir

        # history_parser = HistoryParser(history_json_path=history_json_path)
        # history_parser.load()
        # self.relevant_times, self.relevant_urls = history_parser.get_urls_that_start_with('https://jisho.org/search')

        # TODO: Instantiate ProgressTracker

    def run(self):
        for history_json_path in self.history_Json_path_list:
            history_parser = HistoryParser(history_json_path=history_json_path)
            history_parser.load()
            relevant_times, relevant_urls = history_parser.get_urls_that_start_with('https://jisho.org/search')
            for i, relevant_time, relevant_url in zip(len(relevant_times), relevant_times, relevant_urls):
                self.process(url=relevant_url, time_usec=relevant_time, verbose=True, verbose_index=i)

    def process(self, url: str, time_usec: int, verbose: bool=True, verbose_index: int=None):
        """
        verbose: Whether or not you would like to see progress messages.
        verbose_index: url counter (only usable in verbose)
        """
        index_str = f'{str(verbose_index)}: ' if verbose_index is not None else ''
        found, duplicate = self.cache_handler.check_url(url=url, time_usec=time_usec)
        if not found:
            save_path = get_next_dump_path(dump_dir=self.soup_dir, file_extension='pth', label_length=6)
            soup_save_item = SoupSaveItem(url=url, save_path=save_path)
            status_code, soup = soup_save_item.get_soup()
            if status_code == 200:
                soup_save_item.save(soup=soup, overwrite=False)
                if verbose:
                    logger.blue(f"{index_str}{url}")
            else:
                if verbose:
                    logger.warning(f"{index_str}Encountered status_code: {status_code}")
                    logger.warning(f"{index_str}Skipping {url}")
            
            url_item_pair = {'url': url, 'soup_save_item': soup_save_item}
            self.cache_handler.add_new(item=url_item_pair, time_usec=time_usec)
        else:
            if verbose and not duplicate:
                logger.yellow(f"{index_str}URL already in cache (hit) - {url}")
            else:
                logger.yellow(f"{index_str}Duplicate found in cache (no hit) - {url}")

# import sys
# import requests, pickle
# from bs4 import BeautifulSoup
# from logger import logger
# from common_utils.file_utils import file_exists
# from src.lib.history_parsing.cache import Cache, SoupCacheHandler
# from src.lib.history_parsing.history_parser import HistoryParser
# from qtpy.QtCore import Signal

# class SoupSaver:
#     def __init__(self, soup_save_file_path: str, history_json_path: str):
#         sys.setrecursionlimit(1000000)
#         self.soup_save_file_path = soup_save_file_path
#         history_parser = HistoryParser(history_json_path=history_json_path)
#         history_parser.load()
#         self.relevant_times, self.relevant_urls = history_parser.get_urls_that_start_with('https://jisho.org/search')

#         self.soup_cache_handler = None
#         if not file_exists(soup_save_file_path):
#             self.soup_cache_handler = SoupCacheHandler()
#         else:
#             cache_dict = pickle.load(open(soup_save_file_path, 'rb'))
#             self.soup_cache_handler = cache_dict['soup_cache_handler']

#         self.current_index = None

#     def is_done(self) -> bool:
#         return self.current_index == len(self.relevant_urls) - 1

#     def step(self, message_sig: Signal=None) -> bool:
#         if self.current_index is None:
#             if len(self.relevant_urls) == 0:
#                 if message_sig is None:
#                     logger.warning(f"No relevant urls found.")
#                 else:
#                     message_sig.emit(f"\nNo relevant urls found.")
#                 return True
#             self.current_index = 0
#         else:
#             self.current_index += 1

#         time_usec, url = self.relevant_times[self.current_index], self.relevant_urls[self.current_index]

#         found, duplicate = self.soup_cache_handler.check_url(url=url, time_usec=time_usec)
#         if not found:
#             response = requests.get(url)
#             if response.status_code != 200:
#                 if message_sig is None:
#                     logger.warning(f"Encountered status_code: {response.status_code}")
#                     logger.warning(f"Skipping {url}")
#                 else:
#                     message_sig.emit(f"\nEncountered status_code: {response.status_code}")
#                     message_sig.emit(f"\nSkipping {url}")
#                 return self.is_done()
#             soup = BeautifulSoup(response.text, 'html.parser')
#             # search_word = soup.title.text.split('-')[0][:-1]
#             if message_sig is None:
#                 logger.blue(f"{self.current_index}: {url}")
#             else:
#                 message_sig.emit(f"\n{self.current_index}: {url}")
#             url_soup_pair = {'url': url, 'soup': soup}
#             self.soup_cache_handler.process(item=url_soup_pair, time_usec=time_usec, item_key='url')
#         else:
#             if not duplicate:
#                 if message_sig is None:
#                     logger.yellow(f"{self.current_index}: URL already in cache (hit) - {url}")
#                 else:
#                     message_sig.emit(f"\n{self.current_index}: URL already in cache (hit) - {url}")
#             else:
#                 if message_sig is None:
#                     logger.yellow(f"{self.current_index}: Duplicate found in cache (no hit) - {url}")
#                 else:
#                     message_sig.emit(f"\n{self.current_index}: Duplicate found in cache (no hit) - {url}")
#         cache_dict = {}
#         cache_dict['soup_cache_handler'] = self.soup_cache_handler
#         pickle.dump(cache_dict, open(self.soup_save_file_path, 'wb'))
#         return self.is_done()

#     def run(self, app=None):
#         done = False
#         while not done:
#             done = self.step()

#             if app is not None:
#                 app.processEvents()

# SoupSaver(
#     soup_save_file_path='soup_save.pth',
#     history_json_path='data/browser_history/new/20191009/Chrome/BrowserHistory.json'
# ).run()