from __future__ import annotations
from typing import List, Any
from bs4.element import Tag, NavigableString
from bs4 import BeautifulSoup
from logger import logger
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler
from ..common import Link, LinkList

class PlainText(BasicLoadableObject['PlainText']):
    """
    Note: Used for the text of NavigableString
    """
    def __init__(self, text: str):
        super().__init__()
        self.text = text
    
    @property
    def plain_str(self) -> str:
        return self.text

class DescriptionLinkListObject(BasicLoadableObject['DescriptionLinkListObject']):
    def __init__(self, explanation: str, linklist: LinkList=None):
        super().__init__()
        self.explanation = explanation
        self.linklist = linklist if linklist is not None else LinkList()

    def to_dict(self) -> dict:
        return {
            'explanation': self.explanation,
            'linklist': self.linklist.to_dict_list()
        }
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> DescriptionLinkListObject:
        return DescriptionLinkListObject(
            explanation=item_dict['explanation'],
            linklist=LinkList.from_dict_list(item_dict['linklist'])
        )
    
    @property
    def plain_str(self) -> str:
        return f"{self.explanation}: {' | '.join([link.text for link in self.linklist])}"

class PassagePart(BasicLoadableObject['PassagePart']):
    def __init__(self, header: str, paragraphs: List[str]=None):
        super().__init__()
        self.header = header
        self.paragraphs = paragraphs if paragraphs is not None else []

    @property
    def plain_str(self) -> str:
        print_str = self.header
        for paragraph in self.paragraphs:
            print_str += f'\n{paragraph}'
        return print_str
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = ''
        for i, paragraph in enumerate(self.paragraphs):
            if i == 0:
                print_str += f'{tab}{paragraph}'
            else:
                print_str += f'\n{tab}{paragraph}'
        return print_str

class PassageParts(
    BasicLoadableHandler['PassageParts', 'PassagePart'],
    BasicHandler['PassageParts', 'PassagePart']
):
    def __init__(self, parts: List[PassagePart]=None):
        super().__init__(obj_type=PassagePart, obj_list=parts)
        self.parts = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> PassageParts:
        return PassageParts([PassagePart.from_dict(item_dict) for item_dict in dict_list])

    @property
    def plain_str(self) -> str:
        print_str = ''
        for i, part in enumerate(self):
            if i == 0:
                print_str += part.plain_str
            else:
                print_str += f'\n{part.plain_str}'
        return print_str

    def custom_str(self, indent: int=0) -> str:
        print_str = ''
        for i, part in enumerate(self):
            if i == 0:
                print_str += part.custom_str(indent=indent)
            else:
                print_str += f'\n{part.custom_str(indent=indent)}'
        return print_str

class Passage(BasicLoadableObject['Passage']):
    def __init__(self, header: str, passage_parts: PassageParts=None):
        super().__init__()
        self.header = header
        self.passage_parts = passage_parts if passage_parts is not None else PassageParts()

    @classmethod
    def from_dict(cls, item_dict: dict) -> Passage:
        return Passage(
            header=item_dict['header'],
            passage_parts=PassageParts.from_dict_list(item_dict['passage_parts'])
        )
    
    @property
    def plain_str(self) -> str:
        return f'{self.header}\n{self.passage_parts.plain_str}'
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}{self.header}'
        print_str += f'\n{self.passage_parts.custom_str(indent=indent+1)}'
        return print_str

class MediaItem(BasicLoadableObject['MediaItem']):
    def __init__(self, url: str, caption: str, description: str=None):
        super().__init__()
        self.url = url
        self.caption = caption
        self.description = description
    
    @property
    def plain_str(self) -> str:
        return '[MediaItem]'

class Media(
    BasicLoadableHandler['Media', 'MediaItem'],
    BasicHandler['Media', 'MediaItem']
):
    def __init__(self, item_list: List[MediaItem]=None):
        super().__init__(obj_type=MediaItem, obj_list=item_list)
        self.item_list = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> Media:
        return Media([MediaItem.from_dict(item_dict) for item_dict in dict_list])

    @property
    def plain_str(self) -> str:
        return '[Media]'

class ParsedItem(BasicLoadableObject['ParsedItem']):
    def __init__(self, obj: Any):
        super().__init__()
        assert hasattr(obj, 'plain_str')
        self.obj = obj

    @property
    def plain_str(self) -> str:
        return self.obj.plain_str

    def custom_str(self, indent: int=0) -> str:
        if isinstance(self.obj, Passage):
            return self.obj.custom_str(indent=indent)
        else:
            tab = '\t' * indent
            return f'{tab}{self.plain_str}'

    @property
    def class_name(self) -> str:
        return self.obj.__class__.__name__

    def to_dict(self) -> dict:
        item_dict = {'class_name': self.class_name}
        if hasattr(self.obj, 'to_dict'):
            item_dict['obj'] = self.obj.to_dict()
        elif hasattr(self.obj, 'to_dict_list'):
            item_dict['obj'] = self.obj.to_dict_list()
        else:
            raise Exception
        return item_dict
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> ParsedItem:
        assert 'class_name' in item_dict
        class_name = item_dict['class_name']
        if class_name == 'PlainText':
            obj = PlainText.from_dict(item_dict['obj'])
        elif class_name == 'DescriptionLinkListObject':
            obj = DescriptionLinkListObject.from_dict(item_dict['obj'])
        elif class_name == 'PassagePart':
            obj = PassagePart.from_dict(item_dict['obj'])
        elif class_name == 'PassageParts':
            obj = PassageParts.from_dict_list(item_dict['obj'])
        elif class_name == 'Passage':
            obj = Passage.from_dict(item_dict['obj'])
        elif class_name == 'MediaItem':
            obj = MediaItem.from_dict(item_dict['obj'])
        elif class_name == 'Media':
            obj = Media.from_dict_list(item_dict['obj'])
        else:
            raise Exception(f'Cannot create ParsedItem from {class_name}.')
        return ParsedItem(obj=obj)

class ParsedItemList(
    BasicLoadableHandler['ParsedItemList', 'ParsedItem'],
    BasicHandler['ParsedItemList', 'ParsedItem']
):
    def __init__(self, item_list: List[ParsedItem]=None):
        super().__init__(obj_type=ParsedItem, obj_list=item_list)
        self.item_list = self.obj_list
    
    @property
    def plain_str(self) -> str:
        print_str = ''
        for i, item in enumerate(self):
            if i == 0:
                print_str += item.plain_str
            else:
                print_str += f'\n{item.plain_str}'
        return print_str

    def custom_str(self, indent: int=0) -> str:
        print_str = ''
        for i, item in enumerate(self):
            if i == 0:
                print_str += item.custom_str(indent=indent)
            else:
                print_str += f'\n{item.custom_str(indent=indent)}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> ParsedItemList:
        return ParsedItemList([ParsedItem.from_dict(item_dict) for item_dict in dict_list])
    
    @property
    def class_name_list(self) -> List[str]:
        return [item.class_name for item in self]
    
    def contains_class_names(self, class_names: List[str], operator: str='and') -> bool:
        contained_class_names = self.class_name_list
        if isinstance(class_names, (list, tuple)):
            if operator == 'and':
                return all([name in contained_class_names for name in class_names])
            elif operator == 'or':
                return any([name in contained_class_names for name in class_names])
            else:
                raise Exception
        elif isinstance(class_names, str):
            return class_names in contained_class_names
        else:
            raise Exception

    def append(self, item, is_obj: bool=False):
        if not is_obj:
            super().append(item)
        else:
            super().append(ParsedItem(item))

def parse_description_linklist(description_linklist_html: Tag) -> DescriptionLinkListObject:
    explanation_text = description_linklist_html.find(name='b').text.strip()
    linkbutton_html_list = description_linklist_html.find_all(name='span', class_='linkbutton')
    linklist = LinkList()
    for linkbutton_html in linkbutton_html_list:
        linkbutton_text = linkbutton_html.text.strip()
        link_html = linkbutton_html.find(name='a', href=True)
        linkbutton_url = f"https://kotobank.jp{link_html.attrs['href']}"
        linkbutton_link = Link(url=linkbutton_url, text=linkbutton_text)
        linklist.append(linkbutton_link)
    description_linklist_obj = DescriptionLinkListObject(
        explanation=explanation_text,
        linklist=linklist
    )
    return description_linklist_obj

def parse_passage2(passage2_html: Tag) -> PassagePart:
    header_menu_html = passage2_html.find(name='h5', class_='header_menu')
    header_menu_text = header_menu_html.text.strip()
    passage_paragraph_html_list = passage2_html.find_all(name='p')
    passage_part = PassagePart(header=header_menu_text)
    for passage_paragraph_html in passage_paragraph_html_list:
        passage_paragraph_text = passage_paragraph_html.text.strip()
        passage_part.paragraphs.append(passage_paragraph_text)
    return passage_part

def parse_passage(passage_html: Tag) -> Passage:
    header_menu_html = passage_html.find(name='h4', class_='header_menu')
    header_menu_text = header_menu_html.text.strip()
    passage = Passage(header=header_menu_text)
    passage2_html_list = passage_html.find_all(name='div', type='本文2')
    for passage2_html in passage2_html_list:
        passage_part = parse_passage2(passage2_html)
        passage.passage_parts.append(passage_part)
    return passage

def parse_media(media_html: Tag) -> Media:
    figure_html_list = media_html.find_all(name='figure')
    media = Media()
    for figure_html in figure_html_list:
        figure0_html = figure_html.find(name='a')
        figure_url = f"https://kotobank.jp{figure0_html.attrs['href']}"
        figure_data_lightbox = figure0_html.attrs['data-lightbox']
        figure_data_title = figure0_html.attrs['data-title']
        figure_data_title_html = BeautifulSoup(figure_data_title, 'lxml')
        caption_html = figure_data_title_html.find(name='span', class_='lbdata_caption')
        caption_text = caption_html.text.strip()
        description_html = figure_data_title_html.find(name='span', class_='lbdata_desc')
        description_text = description_html.text.strip() if description_html is not None else None
        media_item = MediaItem(
            url=figure_url,
            caption=caption_text,
            description=description_text
        )
        media.append(media_item)
    return media

def parse(ex_cf_html_list: List[Tag]) -> ParsedItemList:
    parsed_items = ParsedItemList()
    for ex_cf_html in ex_cf_html_list:
        description_html = ex_cf_html.find(name='section', attrs={'class': 'description'})
        has_description = description_html is not None
        assert has_description, 'No description found.'
        for child in description_html.children:
            if type(child) is NavigableString:
                text = str(child).replace(' ', '').replace('\n', '')
                assert len(text) == 0, f'len(text): {len(text)}'
            elif type(child) is Tag:
                if child.name == 'p' and len(child.attrs) == 0:
                    paragraph_text = child.text.strip()
                    parsed_items.append(PlainText(paragraph_text), is_obj=True)
                elif child.name == 'div' and 'type' in child.attrs and child.attrs['type'] == '本文1':
                    passage = parse_passage(child)
                    parsed_items.append(passage, is_obj=True)
                elif child.name == 'div' and 'class' in child.attrs and child.attrs['class'] == ['description_linklist']:
                    description_linklist_obj = parse_description_linklist(child)
                    parsed_items.append(description_linklist_obj, is_obj=True)
                elif child.name == 'div' and 'class' in child.attrs and child.attrs['class'] == ['media']:
                    media = parse_media(child)
                    parsed_items.append(media, is_obj=True)
                elif child.name == 'br' and 'clear' in child.attrs and child.attrs['clear'] == 'all':
                    # Comes after media
                    pass
                else:
                    logger.red(f'Unknown')
                    logger.red(f'child.name: {child.name}')
                    logger.red(f'child.attrs: {child.attrs}')
                    logger.red(f'child.text.strip(): {child.text.strip()}')
                    raise Exception('Unimplemented description child (Tag).')
    return parsed_items