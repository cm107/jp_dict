from __future__ import annotations
from typing import List
from tqdm import tqdm
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler

class BrowserHistoryItem(BasicLoadableObject['BrowserHistoryItem']):
    def __init__(
        self, page_transition: str, title: str, url: str, client_id: str, time_usec: int,
        favicon_url: str=None
    ):
        super().__init__()
        self.page_transition = page_transition
        self.title = title
        self.url = url
        self.client_id = client_id
        self.time_usec = time_usec
        self.favicon_url = favicon_url

    def to_dict(self) -> dict:
        result = {
            'title': self.title,
            'url': self.url,
            'client_id': self.client_id,
            'time_usec': self.time_usec,
        }
        if self.favicon_url is not None:
            result['favicon_url'] = self.favicon_url
        return result
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> BrowserHistoryItem:
        return BrowserHistoryItem(
            page_transition=item_dict['page_transition'],
            title=item_dict['title'],
            url=item_dict['url'],
            client_id=item_dict['client_id'],
            time_usec=item_dict['time_usec'],
            favicon_url=item_dict['favicon_url'] if 'favicon_url' in item_dict else None
        )

class BrowserHistoryItemList(
    BasicLoadableHandler['BrowserHistoryItemList', 'BrowserHistoryItem'],
    BasicHandler['BrowserHistoryItemList', 'BrowserHistoryItem']
):
    def __init__(self, history_items: List[BrowserHistoryItem]=None):
        super().__init__(obj_type=BrowserHistoryItem, obj_list=history_items)
        self.history_items = self.obj_list

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> BrowserHistoryItemList:
        return BrowserHistoryItemList([BrowserHistoryItem.from_dict(item_dict) for item_dict in dict_list])

class BrowserHistory(BasicLoadableObject['BrowserHistory']):
    def __init__(self, browser_history_item_list: BrowserHistoryItemList=None):
        super().__init__()
        self.browser_history_item_list = browser_history_item_list if browser_history_item_list is not None else BrowserHistoryItemList()

    def to_dict(self) -> dict:
        return {
            'Browser History': self.browser_history_item_list.to_dict_list()
        }
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> BrowserHistory:
        return BrowserHistory(
            browser_history_item_list=BrowserHistoryItemList.from_dict_list(item_dict['Browser History'])
        )

    @classmethod
    def combine(cls, browser_history_list: List[BrowserHistory]) -> BrowserHistory:
        result = BrowserHistory()
        time_usec_list = []
        combine_pbar = tqdm(total=len(browser_history_list), unit='histories')
        combine_pbar.set_description('Combining Histories')
        for browser_history in browser_history_list:
            for item in browser_history.browser_history_item_list:
                if item.time_usec not in time_usec_list:
                    time_usec_list.append(item.time_usec)
                    result.browser_history_item_list.append(item)
            combine_pbar.update()
        return result

class BrowserHistoryHandler(
    BasicLoadableHandler['BrowserHistoryHandler', 'BrowserHistory'],
    BasicHandler['BrowserHistoryHandler', 'BrowserHistory']
):
    def __init__(self, browser_history_list: List[BrowserHistory]=None):
        super().__init__(obj_type=BrowserHistory, obj_list=browser_history_list)
        self.browser_history_list = self.obj_list

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> BrowserHistoryHandler:
        return BrowserHistoryHandler([BrowserHistory.from_dict(item_dict) for item_dict in dict_list])

    @classmethod
    def load_from_path_list(cls, path_list: List[str]) -> BrowserHistoryHandler:
        return BrowserHistoryHandler([BrowserHistory.load_from_path(path) for path in path_list])