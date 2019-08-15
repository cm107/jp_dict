import json
from .browser_history import BrowserHistory, BrowserHistoryItem
from .favicon import FaviconExtractor
from ...submodules.logger.logger_handler import logger
from ...submodules.common_utils.file_utils import init_dir
from ...submodules.common_utils.counter_utils import count_list_items

class HistoryParser:
    def __init__(self, history_json_path: str):
        self.history_json_path = history_json_path
        self.browser_history = None

    def load(self):
        data = json.load(open(self.history_json_path, 'r'))
        history_data = data['Browser History']
        self.browser_history = BrowserHistory()
        for history_data_item in history_data:
            favicon_url = history_data_item['favicon_url'].strip() if 'favicon_url' in history_data_item else None
            page_transition = history_data_item['page_transition']
            title = history_data_item['title']
            url = history_data_item['url']
            client_id = history_data_item['client_id']
            time_usec = history_data_item['time_usec']

            history_item = BrowserHistoryItem(
                favicon_url=favicon_url,
                page_transition=page_transition,
                title=title,
                url=url,
                client_id=client_id,
                time_usec=time_usec
            )
            self.browser_history.add(history_item)

    def download_all_favicon(self, icon_dump_dir: str):
        favicon_url_list = self.browser_history.get_favicon_url_list()
        favicon_extractor = FaviconExtractor(
            favicon_url_list=favicon_url_list,
            icon_dump_dir=icon_dump_dir
        )
        init_dir(dir_path=icon_dump_dir, ask_permission=False)
        favicon_extractor.download_icons()
        favicon_extractor.convert_ico2png()
        favicon_extractor.delete_duplicates()

    def print_page_transition_frequencies(self):
        logger.cyan(f"Page Transition Frequencies")
        page_transitions = [
            history_item.page_transition \
                for history_item in self.browser_history.history_items
        ]
        ordered_items = count_list_items(item_list=page_transitions)
        for item in ordered_items:
            logger.purple(f"{item[0]}: {item[1]}")

    def print_title_frequencies(self):
        logger.cyan(f"Title Frequencies")
        titles = [
            history_item.title \
                for history_item in self.browser_history.history_items
        ]
        ordered_items = count_list_items(item_list=titles)
        for item in ordered_items:
            logger.purple(f"{item[0]}: {item[1]}")

    def print_url_frequencies(self):
        logger.cyan(f"URL Frequencies")
        urls = [
            history_item.url \
                for history_item in self.browser_history.history_items
        ]
        ordered_items = count_list_items(item_list=urls)
        for item in ordered_items:
            logger.purple(f"{item[0]}: {item[1]}")

    def print_client_id_frequencies(self):
        logger.cyan(f"Client ID Frequencies")
        client_ids = [
            history_item.client_id \
                for history_item in self.browser_history.history_items
        ]
        ordered_items = count_list_items(item_list=client_ids)
        for item in ordered_items:
            logger.purple(f"{item[0]}: {item[1]}")

    def get_urls_that_start_with(self, substring: str) -> (list, list):
        all_urls = [history_item.url for history_item in self.browser_history.history_items]
        all_times = [history_item.time_usec for history_item in self.browser_history.history_items]
        relevant_urls = []
        relevant_times = []
        for time_usec, url in zip(all_times, all_urls):
            if url.startswith(substring):
                relevant_urls.append(url)
                relevant_times.append(time_usec)
        return relevant_times, relevant_urls