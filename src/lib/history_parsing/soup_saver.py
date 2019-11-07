import sys
import pickle
import requests
from bs4 import BeautifulSoup
from logger import logger
from common_utils.file_utils import file_exists, dir_exists, make_dir
from common_utils.check_utils import check_file_exists
from common_utils.adv_file_utils import get_next_dump_path
from .cache import SoupCacheHandler
from .history_parser import HistoryParser

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
        self.history_json_pathlist = history_json_path_list
        self.progress_save = ProgressSave(save_path=save_path)
        self.cache_handler = SoupCacheHandler()
        self.progress_dict = self.load_progress()

    def load_progress(self) -> dict:
        if self.progress_save.save_exists():
            self.progress_dict = self.progress_save.load()
            self.cache_handler = self.progress_dict['cache_handler']
            return self.progress_dict
        else:
            self.progress_dict = {
                'history_json_pathlist': self.history_json_pathlist.copy(),
                'finished_paths': [],
                'unfinished_paths': self.history_json_pathlist.copy(),
                'current_path': self.history_json_pathlist[0],
                'current_index': -1,
                'cache_handler': self.cache_handler
            }
            return self.progress_dict

    def update_progress(self, current_json_path: str, index: int, finished: bool=False):
        history_json_pathlist = self.progress_dict['history_json_pathlist']
        finished_paths = self.progress_dict['finished_paths']
        unfinished_paths = self.progress_dict['unfinished_paths']
        current_path = self.progress_dict['current_path']
        current_index = self.progress_dict['current_index']
        if finished:
            if current_json_path in history_json_pathlist:
                if current_json_path not in finished_paths:
                    if current_json_path not in unfinished_paths:
                        logger.error(f"Couldn't find {unfinished_paths} in unfinished_paths list.")
                        logger.error(f"unfinished_paths: {unfinished_paths}")
                        raise Exception
                    finished_paths.append(current_json_path)
                    del unfinished_paths[unfinished_paths.index(current_json_path)]
                else:
                    logger.error(f"Encountered finished flag, but {current_json_path} is already in finished_paths list.")
                    logger.error(f"finished_paths: {finished_paths}")
                    raise Exception
            else:
                logger.error(f"{current_json_path} not found in history_json_pathlist")
                logger.error(f"history_json_pathlist: {history_json_pathlist}")
                raise Exception
        current_path = current_json_path
        current_index = index if not finished else -1
        new_progress_dict = {
                'history_json_pathlist': history_json_pathlist.copy(),
                'finished_paths': finished_paths.copy(),
                'unfinished_paths': unfinished_paths.copy(),
                'current_path': current_path,
                'current_index': current_index,
                'cache_handler': self.cache_handler
        }
        self.progress_save.save(progress_dict=new_progress_dict, overwrite=True)
        self.progress_dict = new_progress_dict

class SoupSaveItem(SaveItem):
    def __init__(self, url: str, save_path: str):
        super().__init__(save_path=save_path)
        self.url = url

    def load(self) -> BeautifulSoup:
        return super().load()

    def get_soup(self) -> (int, BeautifulSoup):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser') if response.status_code == 200 else None
        return response.status_code, soup

    def save(self, soup: BeautifulSoup, overwrite: bool=True):
        super().save(item=soup, overwrite=overwrite)

class SoupSaver:
    def __init__(self, history_json_path_list: list, soup_root_dir: str):
        sys.setrecursionlimit(1000000)
        self.history_json_pathlist = history_json_path_list.copy()
        self.soup_root_dir = soup_root_dir
        self.soups_dir = f"{self.soup_root_dir}/soups"

        self.progress_tracker = ProgressTracker(
            history_json_path_list=history_json_path_list.copy(),
            save_path=f"{soup_root_dir}/progress.pth"
        )

    def run(self):
        if not dir_exists(self.soups_dir):
            make_dir(self.soups_dir)
        progress_dict = self.progress_tracker.load_progress()
        history_json_pathlist = progress_dict['history_json_pathlist']
        finished_paths = progress_dict['finished_paths']
        unfinished_paths = progress_dict['unfinished_paths']

        if self.history_json_pathlist != history_json_pathlist:
            for history_json_path in self.history_json_pathlist:
                if history_json_path not in history_json_pathlist:
                    logger.info(f"New path found in history_json_path_list.")
                    logger.info(f"Would you like to add this path to the queue?")
                    while True:
                        answer = input(f"yes/no: ")
                        if answer.lower() in ['yes', 'y']:
                            history_json_pathlist.append(history_json_path)
                            unfinished_paths.append(history_json_path)
                            break
                        elif answer.lower() in ['no', 'n']:
                            logger.warning(f"Ignoring {history_json_path}")
                            del self.history_json_pathlist[self.history_json_pathlist.index(history_json_path)]
                            break
                        else:
                            logger.warning(f"Invalid answer.")

        for i, history_json_path in enumerate(self.history_json_pathlist):
            logger.green(f"({i+1}/{len(self.history_json_pathlist)}) Processing {history_json_path}")
            if history_json_path in finished_paths:
                continue
            if history_json_path not in unfinished_paths:
                logger.error(f"Encountered history_json_path not in unfinished_paths list.")
                raise Exception
            history_parser = HistoryParser(history_json_path=history_json_path)
            history_parser.load()
            relevant_times, relevant_urls = history_parser.get_urls_that_start_with('https://jisho.org/search')
            for i, relevant_time, relevant_url in zip(range(len(relevant_times)), relevant_times, relevant_urls):
                if i <= self.progress_tracker.progress_dict['current_index']:
                    continue
                self.process(url=relevant_url, time_usec=relevant_time, verbose=True, verbose_index=i)
                if i != len(relevant_times) - 1:
                    self.progress_tracker.update_progress(current_json_path=history_json_path, index=i, finished=False)
                else:
                    self.progress_tracker.update_progress(current_json_path=history_json_path, index=i, finished=True)

    def process(self, url: str, time_usec: int, verbose: bool=True, verbose_index: int=None):
        """
        verbose: Whether or not you would like to see progress messages.
        verbose_index: url counter (only usable in verbose)
        """
        index_str = f'{str(verbose_index)}: ' if verbose_index is not None else ''
        found, duplicate = self.progress_tracker.cache_handler.check_url(url=url, time_usec=time_usec)
        if not found:
            save_path = get_next_dump_path(dump_dir=self.soups_dir, file_extension='pth', label_length=6)
            soup_save_item = SoupSaveItem(url=url, save_path=save_path)
            status_code, soup = soup_save_item.get_soup()
            if status_code == 200:
                soup_save_item.save(soup=soup, overwrite=False)
                if verbose:
                    search_word = soup.title.text.split('-')[0][:-1]
                    logger.blue(f"{index_str}{search_word}")
            else:
                if verbose:
                    logger.warning(f"{index_str}Encountered status_code: {status_code}")
                    logger.warning(f"{index_str}Skipping {url}")
            
            url_item_pair = {'url': url, 'soup_save_item': soup_save_item}
            self.progress_tracker.cache_handler.add_new(item=url_item_pair, time_usec=time_usec)
        else:
            if verbose and not duplicate:
                logger.yellow(f"{index_str}URL already in cache (hit) - {url}")
            else:
                logger.yellow(f"{index_str}Duplicate found in cache (no hit) - {url}")