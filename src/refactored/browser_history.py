from __future__ import annotations
from typing import List, Any, Dict, cast
from tqdm import tqdm
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler

class BrowserHistoryItem(BasicLoadableObject['BrowserHistoryItem']):
    def __init__(
        self, title: str, url: str, client_id: str, time_usec: int,
        page_transition: str=None, favicon_url: str=None
    ):
        super().__init__()
        self.title = title
        self.url = url
        self.client_id = client_id
        self.time_usec = time_usec
        self.page_transition = page_transition
        self.favicon_url = favicon_url

    def to_dict(self) -> dict:
        result = {
            'title': self.title,
            'url': self.url,
            'client_id': self.client_id,
            'time_usec': self.time_usec,
        }
        if self.page_transition is not None:
            result['page_transition'] = self.page_transition
        if self.favicon_url is not None:
            result['favicon_url'] = self.favicon_url
        return result
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> BrowserHistoryItem:
        return BrowserHistoryItem(
            title=item_dict['title'],
            url=item_dict['url'],
            client_id=item_dict['client_id'],
            time_usec=item_dict['time_usec'],
            page_transition=item_dict['page_transition'] if 'page_transition' in item_dict else None,
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

    def search(self, search_str: str, target: str='title') -> BrowserHistoryItemList:
        relevant_items = []
        if target == 'title':
            for item in self:
                if search_str in item.title:
                    relevant_items.append(item)
        elif target == 'url':
            for item in self:
                if search_str in item.url:
                    relevant_items.append(item)
        else:
            raise Exception(f'Invalid target: {target}')
        return BrowserHistoryItemList(relevant_items)
    
    def search_by_url_base(self, url_base: str) -> BrowserHistoryItemList:
        relevant_items = []
        for item in self:
            if item.url.startswith(url_base):
                relevant_items.append(item)
        return BrowserHistoryItemList(relevant_items)
    
    def search_by_url_base_and_group_by_url(self, url_base: str) -> CommonBrowserHistoryItemGroupList:
        relevant_items = self.search_by_url_base(url_base)
        common_url_dict = cast(Dict[str, List[BrowserHistoryItem]], {})
        for item in relevant_items:
            if item.url not in common_url_dict:
                common_url_dict[item.url] = [item]
            else:
                common_url_dict[item.url].append(item)
        return CommonBrowserHistoryItemGroupList([CommonBrowserHistoryItemGroup.from_list(item_list) for title, item_list in common_url_dict.items()])

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
    def combine(cls, browser_history_list: List[BrowserHistory], show_pbar: bool=True) -> BrowserHistory:
        result = BrowserHistory()
        time_usec_list = []
        combine_pbar = tqdm(total=len(browser_history_list), unit='histories') if show_pbar else None
        if combine_pbar is not None:
            combine_pbar.set_description('Combining Histories')
        for browser_history in browser_history_list:
            for item in browser_history.browser_history_item_list:
                if item.time_usec not in time_usec_list:
                    time_usec_list.append(item.time_usec)
                    result.browser_history_item_list.append(item)
            if combine_pbar is not None:
                combine_pbar.update()
        if combine_pbar is not None:
            combine_pbar.close()
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

class CommonBrowserHistoryItemGroup(BasicLoadableObject['CommonBrowserHistoryItemGroup']):
    def __init__(
        self, title: str, url: str,
        client_id: str, time_usec: List[int],
        page_transition: str=None, favicon_url: str=None
    ):
        self.title = title
        self.url = url
        self.client_id = client_id
        self.time_usec = time_usec
        self.page_transition = page_transition
        self.favicon_url = favicon_url
    
    def to_list(self) -> List[BrowserHistoryItem]:
        return [
            BrowserHistoryItem(
                title=self.title[i] if type(self.title) is list else self.title,
                url=self.url,
                client_id=self.client_id[i] if type(self.client_id) is list else self.client_id,
                time_usec=self.time_usec[i],
                page_transition=self.page_transition[i] if type(self.page_transition) is list else self.page_transition,
                favicon_url=self.favicon_url[i] if type(self.favicon_url) is list else self.favicon_url
            ) for i in range(len(self.time_usec))
        ]

    @classmethod
    def from_list(cls, item_list: List[BrowserHistoryItem]) -> CommonBrowserHistoryItemGroup:
        title = []
        url = []
        client_id = []
        time_usec = []
        page_transition = []
        favicon_url = []
        for item in item_list:
            title.append(item.title)
            url.append(item.url)
            client_id.append(item.client_id)
            time_usec.append(item.time_usec)
            page_transition.append(item.page_transition)
            favicon_url.append(item.favicon_url)
        if len(list(set(title))) == 1:
            title = title[0]
        assert len(list(set(url))) == 1
        url = url[0]
        if len(list(set(client_id))) == 1:
            client_id = client_id[0]
        assert len(list(set(time_usec))) == len(time_usec)
        if len(list(set(page_transition))) == 1:
            page_transition = page_transition[0]
        if len(list(set(favicon_url))) == 1:
            favicon_url = favicon_url[0]
        return CommonBrowserHistoryItemGroup(
            title=title,
            url=url,
            client_id=client_id,
            time_usec=time_usec,
            page_transition=page_transition,
            favicon_url=favicon_url
        )
    
    def to_browser_history_item_list(self) -> BrowserHistoryItemList:
        return BrowserHistoryItemList(self.to_list())

    @classmethod
    def from_browser_history_item_list(cls, browser_history_item_list: BrowserHistoryItemList) -> CommonBrowserHistoryItemGroup:
        return cls.from_list(browser_history_item_list.history_items)
    
    @classmethod
    def convert_from(cls, obj: Any) -> CommonBrowserHistoryItemGroup:
        if isinstance(obj, list):
            if len(list(set([type(part) for part in obj]))) == 1:
                if isinstance(obj[0], BrowserHistoryItem):
                    return cls.from_list(obj)
                else:
                    raise TypeError(f'Cannot convert List[{type(obj[0]).__name__}] to {cls.__name__}')
            else:
                raise TypeError(f'Cannot convert multi-type list to {cls.__name__}')
        elif isinstance(obj, BrowserHistoryItemList):
            return cls.from_browser_history_item_list(obj)
        else:
            raise TypeError(f'Cannot convert {type(obj).__name__} to {cls.__name__}')
    
    @property
    def item_count(self) -> int:
        return len(self.time_usec)

class CommonBrowserHistoryItemGroupList(
    BasicLoadableHandler['CommonBrowserHistoryItemGroupList', 'CommonBrowserHistoryItemGroup'],
    BasicHandler['CommonBrowserHistoryItemGroupList', 'CommonBrowserHistoryItemGroup']
):
    def __init__(self, group_list: List[CommonBrowserHistoryItemGroup]=None):
        super().__init__(obj_type=CommonBrowserHistoryItemGroup, obj_list=group_list)
        self.group_list = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> CommonBrowserHistoryItemGroupList:
        return CommonBrowserHistoryItemGroupList([CommonBrowserHistoryItemGroup.from_dict(item_dict) for item_dict in dict_list])