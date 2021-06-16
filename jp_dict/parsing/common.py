from __future__ import annotations
from typing import List
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler

class Link(BasicLoadableObject['Link']):
    def __init__(self, url: str, text: str=None):
        super().__init__()
        self.url = url
        self.text = text
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        return f'{tab}[{self.text}]'
    
    @property
    def markdown(self) -> str:
        return f'[{self.text}]({self.url})'
    
    @property
    def html(self) -> str:
        return f'<a href="{self.url}">{self.text}</a>'

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
    
    @property
    def markdown(self) -> str:
        print_str = ''
        for i, link in enumerate(self):
            if i == 0:
                print_str += link.markdown
            else:
                print_str += f'\n{link.markdown}'
    
    @property
    def html(self) -> str:
        print_str = ''
        for i, link in enumerate(self):
            if i == 0:
                print_str += link.html
            else:
                print_str += f'<br>{link.html}'