from __future__ import annotations
from typing import List, Any
from bs4.element import Tag, NavigableString
from logger import logger
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler

class PlainText(BasicLoadableObject['PlainText']):
    """
    Note: Used for the text of NavigableString
    """
    def __init__(self, text: str):
        super().__init__()
        self.text = text

class BoldText(BasicLoadableObject['BoldText']):
    """
    Note: Used to make plain text look bold.
    """
    def __init__(self, text: str):
        super().__init__()
        self.text = text

class SmallText(BasicLoadableObject['SmallText']):
    """
    Note: Not really sure what this is supposed to mean.
    It seems like it's being used for text that is contained in parentheses.
    """
    def __init__(self, text: str):
        super().__init__()
        self.text = text

class LineBreak(BasicLoadableObject['LineBreak']):
    """
    Note: Used for putting a line break in the middle of a paragraph.
    Indentation needs to be considered when incorporating this class
    into a string.
    I'm not sure if it will always be like this, but in the example
    that I've seen so far, strippable text that comes immediately after
    the line break is included in the same html child.
    """
    def __init__(self, text: str=None):
        super().__init__()
        self.text = text
    
    def to_dict(self) -> dict:
        result = {}
        if self.text is not None:
            result['text'] = self.text
        return result
    
    @classmethod
    def from_dict(self, item_dict: dict) -> LineBreak:
        return LineBreak(
            text=item_dict['text'] if 'text' in item_dict else None
        )

class SubText(BasicLoadableObject['SubText']):
    """
    Note: SubText for subscript text
    """
    def __init__(self, text: str):
        super().__init__()
        self.text = text

class SupText(BasicLoadableObject['SupText']):
    """
    Note: SupText for superscript text
    """
    def __init__(self, text: str):
        super().__init__()
        self.text = text

class A_Link(BasicLoadableObject['A_Link']):
    """
    Note: a href Link
    """
    def __init__(self, text: str, url: str):
        super().__init__()
        self.text = text
        self.url = url
    
    @property
    def plain_str(self) -> str:
        return f'[{self.text}]({self.url})'

class StyledText(BasicLoadableObject['StyledText']):
    """
    So far, I have seen this be used to draw a box around
    some text with a given border width (e.g. 1px), a solid
    colodr (e.g. #000) and a given margin.
    """
    def __init__(self, text: str, style: str):
        super().__init__()
        self.text = text
        self.style = style

class ParseFailed(BasicLoadableObject['ParseFailed']):
    """
    This indicates that the parsing failed due to some
    reason. So far I have seen one example where a strange
    tag was causing the html text to be unstrippable.
    """
    def __init__(self):
        super().__init__()
    
    @property
    def plain_str(self) -> str:
        return "[Text Parsing Failed]"

class KanjiImage(BasicLoadableObject['KanjiImage']):
    """
    Note: So far, I have seen this being used to paste the image of
    an unusual kanji into a sentence. It looks unnatural even in the
    browser.
    """
    def __init__(self, url: str, text: str, height: int):
        self.url = url
        self.text = text
        self.height = height

class CaptionedImage(BasicLoadableObject['CaptionedImage']):
    """
    Note: So far I have seen this being used to show an illustration
    between the meaning and example html, enclosed inside of a div.
    Unlike the KanjiImage, this one doesn't have any text that can be
    stripped. It's just an image with an enclosed caption.
    """
    def __init__(self, url: str, caption: str):
        self.url = url
        self.caption = caption

class ParsedItem(BasicLoadableObject['ParsedItem']):
    def __init__(self, obj: Any):
        super().__init__()
        self.obj = obj

    def preview_str(self) -> str:
        if type(self.obj) in [PlainText, BoldText, SmallText, StyledText]:
            return self.obj.text
        elif type(self.obj) is SubText:
            return f'_{self.obj.text}'
        elif type(self.obj) is SupText:
            return f'^{self.obj.text}'
        elif type(self.obj) in [A_Link, ParseFailed]:
            return self.obj.plain_str
        elif type(self.obj) == LineBreak:
            return f'\n{self.obj.text}' if self.obj.text is not None else '\n'
        else:
            return f'TODO ({self.obj.__class__.__name__})'

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
        elif class_name == 'BoldText':
            obj = PlainText.from_dict(item_dict['obj'])
        elif class_name == 'SmallText':
            obj = SmallText.from_dict(item_dict['obj'])
        elif class_name == 'LineBreak':
            obj = LineBreak.from_dict(item_dict['obj'])
        elif class_name == 'SubText':
            obj = SubText.from_dict(item_dict['obj'])
        elif class_name == 'SupText':
            obj = SupText.from_dict(item_dict['obj'])
        elif class_name == 'A_Link':
            obj = A_Link.from_dict(item_dict['obj'])
        elif class_name == 'StyledText':
            obj = StyledText.from_dict(item_dict['obj'])
        elif class_name == 'ParseFailed':
            obj = StyledText.from_dict(item_dict['obj'])
        elif class_name == 'KanjiImage':
            obj = KanjiImage.from_dict(item_dict['obj'])
        elif class_name == 'CaptionedImage':
            obj = CaptionedImage.from_dict(item_dict['obj'])
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
    
    def preview_str(self) -> str:
        print_str = ''
        for item in self:
            print_str += item.preview_str()
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

class ParsedContainer(BasicLoadableObject['ParsedContainer']):
    def __init__(self, container_type: str, parsed_items: ParsedItemList=None):
        super().__init__()
        self.container_type = container_type
        self.parsed_items = parsed_items if parsed_items is not None else ParsedItemList

    def to_dict(self) -> dict:
        return {
            'container_type': self.container_type,
            'parsed_items': self.parsed_items.to_dict_list() if self.parsed_items is not None else None
        }

    @classmethod
    def from_dict(cls, item_dict: dict) -> ParsedContainer:
        return ParsedContainer(
            container_type=item_dict['container_type'],
            parsed_items=ParsedItemList.from_dict_list(item_dict['parsed_items']) if item_dict['parsed_items'] is not None else None
        )
    
    @property
    def is_meaning(self) -> bool:
        return self.container_type == 'Meaning'
    
    @property
    def is_example(self) -> bool:
        return self.container_type == 'Example'
    
    @property
    def is_subhead_word(self) -> bool:
        return self.container_type == 'SubheadWord'
    
    @property
    def is_irregular_div(self) -> bool:
        return self.container_type == 'IrregularDiv'

class ParsedContainerList(
    BasicLoadableHandler['ParsedContainerList', 'ParsedContainer'],
    BasicHandler['ParsedContainerList', 'ParsedContainer']
):
    def __init__(self, container_list: List[ParsedContainer]=None):
        super().__init__(obj_type=ParsedContainer, obj_list=container_list)
        self.container_list = self.obj_list

    def preview_str(self) -> str:
        print_str = ''
        for i, container in enumerate(self):
            if i == 0:
                print_str += container.parsed_items.preview_str()
            else:
                print_str += f'\n{container.parsed_items.preview_str()}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> ParsedContainerList:
        return ParsedContainerList([ParsedContainer.from_dict(item_dict) for item_dict in dict_list])

    @property
    def container_types(self) -> List[str]:
        return [container.container_type for container in self]

class ParsedArticleList(
    BasicLoadableHandler['ParsedArticleList', 'ParsedContainerList'],
    BasicHandler['ParsedArticleList', 'ParsedContainerList']
):
    def __init__(self, article_list: List[ParsedContainerList]=None):
        super().__init__(obj_type=ParsedContainerList, obj_list=article_list)
        self.article_list = self.obj_list

    def preview_str(self) -> str:
        print_str = ''
        for i, article in enumerate(self):
            if i == 0:
                print_str += article.preview_str()
            else:
                print_str += f'\n{article.preview_str()}'
        return print_str

    def to_dict_list(self) -> list:
        return [article.to_dict_list() for article in self]

    @classmethod
    def from_dict_list(cls, dict_list: list) -> ParsedArticleList:
        return ParsedArticleList([ParsedContainerList.from_dict_list(item_dict) for item_dict in dict_list])

    @property
    def container_types_list(self) -> List[List[str]]:
        return [article.container_types for article in self]

def get_parsed_items(tag: Tag) -> ParsedItemList:
    parsed_items = ParsedItemList()
    for child in tag.children:
        if type(child) is NavigableString:
            parsed_items.append(PlainText(text=str(child)), is_obj=True)
        elif type(child) is Tag:
            if child.name == 'small':
                parsed_items.append(SmallText(text=child.text.strip()), is_obj=True)
            elif child.name == 'sub':
                parsed_items.append(SubText(text=child.text.strip()), is_obj=True)
            elif child.name == 'sup':
                parsed_items.append(SupText(text=child.text.strip()), is_obj=True)
            elif child.name == 'a' and 'href' in child.attrs:
                link_text = child.text.strip()
                link_url = f"kotobank.jp{child.attrs['href']}"
                a_link = A_Link(text=link_text, url=link_url)
                parsed_items.append(a_link, is_obj=True)
            elif child.name == 'b' and len(child.attrs) == 0:
                parsed_items.append(BoldText(text=child.text.strip()), is_obj=True)
            elif child.name == 'br' and len(child.attrs) == 0:
                text = child.text.strip()
                text = text if len(text) > 0 else None
                parsed_items.append(LineBreak(text=text), is_obj=True)
            elif child.name == 'span' and 'style' in child.attrs:
                text = child.text.strip()
                style = child.attrs['style']
                styled_text = StyledText(text=text, style=style)
                parsed_items.append(styled_text, is_obj=True)
            elif child.name == 'img' and 'src' in child.attrs and 'height' in child.attrs:
                url = f"kotobank.jp{child.attrs['src']}"
                height = int(child.attrs['height'])
                text = child.text.strip()
                img_source = KanjiImage(url=url, text=text, height=height)
                parsed_items.append(img_source, is_obj=True)
            elif child.name == 'img' and 'src' in child.attrs and 'caption' in child.attrs:
                url = f"kotobank.jp{child.attrs['src']}"
                caption = child.attrs['caption']
                captioned_img = CaptionedImage(url=url, caption=caption)
                parsed_items.append(captioned_img, is_obj=True)
            elif child.name == 'sma<a':
                # Wierd tag. Probably a typo. Refer to 軌跡
                parsed_items.append(ParseFailed(), is_obj=True)
            else:
                logger.red(f'TODO')
                logger.red(f'child.name: {child.name}')
                logger.red(f'child.attrs: {child.attrs}')
                logger.red(f'child.text.strip(): {child.text.strip()}')
                import sys
                sys.exit()
        else:
            raise TypeError
    return parsed_items

def parse(ex_cf_html_list: List[Tag]):
    article_list = ParsedArticleList()
    for ex_cf_html in ex_cf_html_list:
        description_html = ex_cf_html.find(name='section', attrs={'class': 'description'})
        has_description = description_html is not None
        assert has_description, 'No description found.'
        container_list = ParsedContainerList()
        for child in description_html.children:
            if type(child) is NavigableString:
                logger.cyan(f'Plain Text')
                text = str(child).replace(' ', '').replace('\n', '')
                logger.purple(f'text: {text}')
                assert len(text) == 0, f'len(text): {len(text)}'
            elif type(child) is Tag:
                if 'data-orgtag' in child.attrs and child.attrs['data-orgtag'] == 'meaning':
                    logger.cyan('Meaning')
                    meaning_text = child.text.strip()
                    logger.purple(f'\tmeaning_text: {meaning_text}')
                    parsed_items = get_parsed_items(tag=child)
                    logger.white(f'parsed_items.preview_str():\n{parsed_items.preview_str()}')
                    logger.blue(f'parsed_items.class_name_list: {parsed_items.class_name_list}')
                    container = ParsedContainer(container_type='Meaning', parsed_items=parsed_items)
                    container_list.append(container)
                elif 'data-orgtag' in child.attrs and child.attrs['data-orgtag'] == 'example':
                    logger.cyan('Example')
                    example_text = child.text.strip()
                    logger.purple(f'\texample_text: {example_text}')
                    parsed_items = get_parsed_items(tag=child)
                    logger.white(f'parsed_items.preview_str():\n{parsed_items.preview_str()}')
                    logger.blue(f'parsed_items.class_name_list: {parsed_items.class_name_list}')
                    container = ParsedContainer(container_type='Example', parsed_items=parsed_items)
                    container_list.append(container)
                elif 'data-orgtag' in child.attrs and child.attrs['data-orgtag'] == 'subheadword':
                    # This is for showing the alternative of a given word. E.g. ふてぶてしい -> ふてぶてしさ
                    # So far I have only encountered the subheadword + meaning pattern.
                    parsed_items = get_parsed_items(tag=child)
                    logger.white(f'parsed_items.preview_str():\n{parsed_items.preview_str()}')
                    logger.blue(f'parsed_items.class_name_list: {parsed_items.class_name_list}')
                    container = ParsedContainer(container_type='SubheadWord', parsed_items=parsed_items)
                    container_list.append(container)
                elif child.name == 'div' and len(child.attrs) == 0:
                    logger.cyan('Irregular Div')
                    parsed_items = get_parsed_items(tag=child)
                    container = ParsedContainer(container_type='IrregularDiv', parsed_items=parsed_items)
                    container_list.append(container)
                else:
                    logger.red(f'Unknown')
                    logger.red(f'child.name: {child.name}')
                    logger.red(f'child.attrs: {child.attrs}')
                    logger.red(f'child.text.strip(): {child.text.strip()}')
                    import sys
                    sys.exit()
        article_list.append(container_list)
    print(f'article_list.container_types_list: {article_list.container_types_list}')
    logger.green(article_list.preview_str())