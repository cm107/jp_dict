from __future__ import annotations
from typing import List
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler

class Link(BasicLoadableObject['Link']):
    def __init__(self, url: str, text: str=None):
        super().__init__()
        self.url = url
        self.text = text

class LinkList(
    BasicLoadableHandler['LinkList', 'Link'],
    BasicHandler['LinkList', 'Link']
):
    def __init__(self, links: List[Link]=None):
        super().__init__(obj_type=Link, obj_list=links)
        self.links = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> LinkList:
        return LinkList([Link.from_dict(item_dict) for item_dict in dict_list])