from __future__ import annotations
from typing import List, Any, Type, cast, Union, TypeVar
from jp_dict.parsing.kotobank.seisenpan import LineBreak
import pandas as pd
from bs4.element import Tag, NavigableString

from logger import logger
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler
from common_utils.path_utils import get_rootname_from_path

from ..common import Link

T = TypeVar('T')
H = TypeVar('H')

# Simple Text
class PlainText(BasicLoadableObject['PlainText']):
    def __init__(self, text: str):
        super().__init__()
        text = text.replace('　', 'X')
        text = text.replace('  ', '')
        text = text.replace('\n', '').replace('\t', '')
        self.text = text
    
    @property
    def is_empty(self) -> bool:
        return len(self.text) == 0

    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        return f'{tab}{self.text}'
    
    @property
    def plain_str(self) -> str:
        return self.text.replace(' ', '')

class Hinshi(PlainText):
    def __init__(self, text: str):
        super().__init__(text=text)

    @property
    def plain_str(self) -> str:
        return self.text

class BoldText(PlainText):
    def __init__(self, text: str):
        super().__init__(text=text)

    @property
    def plain_str(self) -> str:
        return self.text

class HeaderText(BoldText):
    def __init__(self, text: str):
        super().__init__(text=text)
    
    @property
    def plain_str(self) -> str:
        return self.text
    
    @property
    def html(self) -> str:
        return f'<b>{self.text}</b>'

class KigoWord(PlainText):
    def __init__(self, text: str):
        super().__init__(text=text)

    @property
    def plain_str(self) -> str:
        return self.text

class OriginWord(PlainText):
    def __init__(self, text: str):
        super().__init__(text=text)

    @property
    def plain_str(self) -> str:
        return self.text

class MotoTsudzuri(PlainText):
    def __init__(self, text: str):
        super().__init__(text=text)

    @property
    def plain_str(self) -> str:
        return self.text

class SuperscriptText(PlainText):
    def __init__(self, text: str):
        super().__init__(text=text)

    @property
    def plain_str(self) -> str:
        return f'^{self.text}'

    @property
    def html(self) -> str:
        return f'<sup>{self.text}</sup>'

class SubscriptText(PlainText):
    def __init__(self, text: str):
        super().__init__(text=text)

    @property
    def plain_str(self) -> str:
        return f'_{self.text}'

    @property
    def html(self) -> str:
        return f'<sub>{self.text}</sub>'

class RekishiText(PlainText):
    def __init__(self, text: str):
        super().__init__(text=text)

    @property
    def plain_str(self) -> str:
        return self.text

class ItalicText(PlainText):
    def __init__(self, text: str):
        super().__init__(text=text)

    @property
    def plain_str(self) -> str:
        return self.text
    
    @property
    def html(self) -> str:
        return f'<i>{self.text}</i>'

# Other
class Gaiji(BasicLoadableObject['Gaiji']):
    def __init__(self, url: str, int_equivalent: int, str_equivalent: str):
        super().__init__()
        self.url = url
        self.int_equivalent = int_equivalent
        self.str_equivalent = str_equivalent
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        return f'{tab}{self.str_equivalent}'

    @property
    def plain_str(self) -> str:
        return f'{self.str_equivalent}. '

class DefinitionNumber(BasicLoadableObject['DefinitionNumber']):
    def __init__(self, num: int):
        super().__init__()
        self.num = num
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        return f'{tab}{self.num}'

    @property
    def plain_str(self) -> str:
        return f'{self.num}. '

class RelatedWordLink(BasicLoadableObject['RelatedWordLink']):
    def __init__(self, url: str, text: Union[str, RubyFuriganaWord]):
        super().__init__()
        self.url = url
        self.text = text

    def to_dict(self) -> dict:
        if type(self.text) is str:
            text_value = self.text
        elif type(self.text) is RubyFuriganaWord:
            text_value = self.text.to_dict()
        else:
            raise TypeError
        return {
            'url': self.url,
            'text': text_value,
            'text_type': type(self.text).__name__
        }
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> RelatedWordLink:
        if 'text_type' not in item_dict:
            raise KeyError
        if item_dict['text_type'] == 'str':
            text_value = item_dict['text']
        elif item_dict['text_type'] == 'RubyFuriganaWord':
            text_value = RubyFuriganaWord.from_dict(item_dict['text'])
        else:
            raise ValueError
        return RelatedWordLink(
            url=item_dict['url'],
            text=text_value
        )

    @property
    def plain_str(self) -> str:
        if type(self.text) is str:
            return f'[{self.text}]'
        elif type(self.text) is RubyFuriganaWord:
            return f'[{self.text.plain_str}]'
        else:
            raise TypeError
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        return f'{tab}{self.plain_str}'
    
    @property
    def markdown(self) -> str:
        if type(self.text) is str:
            return f'[{self.text}]({self.url})'
        elif type(self.text) is RubyFuriganaWord:
            return f'[{self.text.writing}]({self.url})' # I don't think I can do the furigana in markdown.
        else:
            raise ValueError
    
    @property
    def html(self) -> str:
        if type(self.text) is str:
            return f'<a href="{self.url}">{self.text}</a>'
        elif type(self.text) is RubyFuriganaWord:
            return f'<a href="{self.url}">{self.text.html}</a>'
        else:
            raise TypeError

class RelatedWordLinkList(
    BasicLoadableHandler['RelatedWordLinkList', 'RelatedWordLink'],
    BasicHandler['RelatedWordLinkList', 'RelatedWordLink']
):
    def __init__(self, link_list: List[RelatedWordLink]=None):
        super().__init__(obj_type=RelatedWordLink, obj_list=link_list)
        self.link_list = self.obj_list
    
    def custom_str(self, indent: int=0) -> str:
        print_str = ''
        for i, link in enumerate(self):
            if i == 0:
                print_str += link.custom_str(indent=indent)
            else:
                print_str += f'\n{link.custom_str(indent=indent)}'
        return print_str

    @property
    def plain_str(self) -> str:
        return self.custom_str(indent=0)

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> RelatedWordLinkList:
        return RelatedWordLinkList([RelatedWordLink.from_dict(item_dict) for item_dict in dict_list])

class Media(BasicLoadableObject['Media']):
    def __init__(self, fullsize_img_link: Link, smallsize_img_link: Link):
        super().__init__()
        self.fullsize_img_link = fullsize_img_link
        self.smallsize_img_link = smallsize_img_link
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}Media:'
        print_str += f'\n{self.fullsize_img_link.custom_str(indent=indent+1)}'
        print_str += f'\n{self.smallsize_img_link.custom_str(indent=indent+1)}'
        return print_str

    @property
    def plain_str(self) -> str:
        return self.custom_str(indent=0)

    def to_dict(self) -> dict:
        return {
            'fullsize_img_link': self.fullsize_img_link.to_dict(),
            'smallsize_img_link': self.smallsize_img_link.to_dict()
        }
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> Media:
        return Media(
            fullsize_img_link=Link.from_dict(item_dict['fullsize_img_link']),
            smallsize_img_link=Link.from_dict(item_dict['smallsize_img_link'])
        )

class Table(BasicLoadableObject['Table']):
    def __init__(self, table_dict: dict):
        super().__init__()
        self.table_dict = table_dict
    
    @property
    def plain_str(self) -> str:
        return self.to_df().to_string()

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.table_dict)
    
    @classmethod
    def from_df(cls, table_df: pd.DataFrame) -> Table:
        return Table(table_dict=table_df.to_dict())

class TableList(
    BasicLoadableHandler['TableList', 'Table'],
    BasicHandler['TableList', 'Table']
):
    def __init__(self, table_list: List[Table]=None):
        super().__init__(obj_type=Table, obj_list=table_list)
        self.table_list = self.obj_list
    
    @property
    def plain_str(self) -> str:
        return self.to_df().to_string()

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> TableList:
        return TableList([Table.from_dict(item_dict) for item_dict in dict_list])

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_records(self.to_dict_list())

    @classmethod
    def from_df(cls, df: pd.DataFrame) -> TableList:
        return TableList.from_dict_list(df.to_records())

class SpecialString:
    end_str = '\033[0m'
    bold_str = '\033[1m'
    italic_str = "\033[3m"
    underline_str = "\033[4m"
    gaiji_str = "\33[101m"
    def_num_str = "\33[44m"

    def __init__(self, text: str):
        self.text = text
    
    @property
    def end(self) -> SpecialString:
        return SpecialString(f'{self.text}{self.end_str}')

    @property
    def bold(self) -> SpecialString:
        return SpecialString(f'{self.bold_str}{self.text}')
    
    @property
    def italic(self) -> SpecialString:
        return SpecialString(f'{self.italic_str}{self.text}')

    @property
    def underline(self) -> SpecialString:
        return SpecialString(f'{self.underline_str}{self.text}')
    
    @property
    def gaiji(self) -> SpecialString:
        return SpecialString(f'{self.gaiji_str}{self.text}')
    
    @property
    def def_num(self) -> SpecialString:
        return SpecialString(f'{self.def_num_str}{self.text}')

class RubyFuriganaWord(BasicLoadableObject['RubyFuriganaWord']):
    def __init__(self, writing: str, reading: str):
        self.writing = writing
        self.reading = reading
    
    @property
    def plain_str(self) -> str:
        return f'{self.writing}({self.reading})'
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}{self.plain_str}'
        return print_str
    
    @property
    def html(self) -> str:
        return f'<ruby><rb>{self.writing}</rb><rt>{self.reading}</rt></ruby>'

class RuigigoList(
    BasicLoadableHandler['RuigigoList', 'RelatedWordLink'],
    BasicHandler['RuigigoList', 'RelatedWordLink']
):
    def __init__(self, ruigigo_list: List[RelatedWordLink]=None):
        raise Exception("This class is obsolete now.")
        super().__init__(obj_type=RelatedWordLink, obj_list=ruigigo_list)
        self.ruigigo_list = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> RuigigoList:
        return RuigigoList([RelatedWordLink.from_dict(item_dict) for item_dict in dict_list])

    @property
    def plain_str(self) -> str:
        return '[類義語]\n' + '・'.join([link.plain_str for link in self])
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        return tab + '[類義語]\n' + tab + '・'.join([link.plain_str for link in self])

    @property
    def html(self) -> str:
        hidden = '・'.join([link.html for link in self])
        return f'<details><summary>[類義語]</summary>{hidden}</details>'

class ParsedItem(BasicLoadableObject['ParsedItem']):
    def __init__(self, obj: Any):
        super().__init__()

        assert hasattr(obj, 'to_dict') or hasattr(obj, 'to_dict_list')
        assert hasattr(obj, 'from_dict') or hasattr(obj, 'from_dict_list')
        self.obj = obj
    
    @property
    def preview_str(self) -> str:
        if type(self.obj) in [PlainText, Hinshi, KigoWord, MotoTsudzuri, RekishiText]:
            obj = cast(PlainText, self.obj)
            return obj.text
        elif type(self.obj) in [BoldText, HeaderText]:
            obj = cast(BoldText, self.obj)
            return SpecialString(obj.text).bold.end.text
        elif type(self.obj) is OriginWord:
            obj = cast(OriginWord, self.obj)
            return SpecialString(obj.text).underline.end.text
        elif type(self.obj) is SuperscriptText:
            obj = cast(SuperscriptText, self.obj)
            return f'^{obj.text}'
        elif type(self.obj) is SubscriptText:
            obj = cast(SubscriptText, self.obj)
            return f'_{obj.text}'
        elif type(self.obj) is ItalicText:
            obj = cast(ItalicText, self.obj)
            return SpecialString(obj.text).italic.end.text
        elif type(self.obj) is Gaiji:
            obj = cast(Gaiji, self.obj)
            return '\n' + SpecialString(obj.str_equivalent).gaiji.end.text
        elif type(self.obj) is DefinitionNumber:
            obj = cast(DefinitionNumber, self.obj)
            return '\n' + SpecialString(f'{obj.num}').def_num.end.text
        elif type(self.obj) is RelatedWordLink:
            obj = cast(RelatedWordLink, self.obj)
            return SpecialString(obj.plain_str).bold.underline.end.text
        elif type(self.obj) is RelatedWordLinkList:
            obj = cast(RelatedWordLinkList, self.obj)
            print_str = ''
            for link in obj:
                print_str += f'\n{SpecialString(link.text).bold.underline.end.text}'
            return print_str
        elif type(self.obj) is Media:
            obj = cast(Media, self.obj)
            return '[Media Links]'
        elif type(self.obj) is Table:
            obj = cast(Table, self.obj)
            return '\n' + obj.to_df().__str__()
        elif type(self.obj) is TableList:
            obj = cast(Table, self.obj)
            print_str = ''
            for table in obj:
                print_str += '\n' + table.to_df().__str__()
            return print_str
        elif type(self.obj) is RubyFuriganaWord:
            obj = cast(RubyFuriganaWord, self.obj)
            return obj.plain_str
        elif type(self.obj) is RuigigoList:
            obj = cast(RuigigoList, self.obj)
            return obj.plain_str
        elif type(self.obj) is RuigigoParsedItemGroup:
            obj = cast(RuigigoParsedItemGroup, self.obj)
            return obj.plain_str
        elif type(self.obj) is HeaderParsedItemGroup:
            obj = cast(HeaderParsedItemGroup, self.obj)
            return obj.plain_str
        else:
            return f'TODO ({self.obj.__class__.__name__})'

    @property
    def plain_str(self) -> str:
        if type(self.obj) in [PlainText, Hinshi, KigoWord, MotoTsudzuri, RekishiText]:
            obj = cast(PlainText, self.obj)
            return obj.text
        elif type(self.obj) in [BoldText, HeaderText]:
            obj = cast(BoldText, self.obj)
            return obj.text
        elif type(self.obj) is OriginWord:
            obj = cast(OriginWord, self.obj)
            return obj.text
        elif type(self.obj) is SuperscriptText:
            obj = cast(SuperscriptText, self.obj)
            return f'^{obj.text}'
        elif type(self.obj) is SubscriptText:
            obj = cast(SubscriptText, self.obj)
            return f'_{obj.text}'
        elif type(self.obj) is ItalicText:
            obj = cast(ItalicText, self.obj)
            return obj.text
        elif type(self.obj) is Gaiji:
            obj = cast(Gaiji, self.obj)
            return '\n' + obj.str_equivalent
        elif type(self.obj) is DefinitionNumber:
            obj = cast(DefinitionNumber, self.obj)
            return f'\n{obj.num}'
        elif type(self.obj) is RelatedWordLink:
            obj = cast(RelatedWordLink, self.obj)
            return obj.plain_str
        elif type(self.obj) is RelatedWordLinkList:
            obj = cast(RelatedWordLinkList, self.obj)
            print_str = ''
            for link in obj:
                print_str += f'\n{link.plain_str}'
            return print_str
        elif type(self.obj) is Media:
            obj = cast(Media, self.obj)
            return '[Media Links]'
        elif type(self.obj) is Table:
            obj = cast(Table, self.obj)
            return '\n' + obj.to_df().__str__()
        elif type(self.obj) is TableList:
            obj = cast(Table, self.obj)
            print_str = ''
            for table in obj:
                print_str += '\n' + table.to_df().__str__()
            return print_str
        elif type(self.obj) is RubyFuriganaWord:
            obj = cast(RubyFuriganaWord, self.obj)
            return obj.plain_str
        elif type(self.obj) is RuigigoList:
            obj = cast(RuigigoList, self.obj)
            return obj.plain_str
        elif type(self.obj) is RuigigoParsedItemGroup:
            obj = cast(RuigigoParsedItemGroup, self.obj)
            return obj.plain_str
        elif type(self.obj) is HeaderParsedItemGroup:
            obj = cast(HeaderParsedItemGroup, self.obj)
            return obj.plain_str
        else:
            return f'TODO ({self.obj.__class__.__name__})'

    def custom_str(
        self, indent: int=0, first: bool=False,
        link2html: bool=False, media2html: bool=False,
        furigana2html: bool=False,
        all_html: bool=True
    ) -> str:
        tab = '\t' * indent
        use_tab, use_linebreak = False, False
        if type(self.obj) in [PlainText, Hinshi, KigoWord, MotoTsudzuri, RekishiText]:
            obj = cast(PlainText, self.obj)
            print_str = obj.text
        elif type(self.obj) in [BoldText, HeaderText]:
            obj = cast(BoldText, self.obj)
            if not all_html:
                print_str = obj.text
            else:
                print_str = f'<b>{obj.text}</b>'
        elif type(self.obj) is OriginWord:
            obj = cast(OriginWord, self.obj)
            if not all_html:
                print_str = obj.text
            else:
                print_str = f'<strong>{obj.text}</strong>'
        elif type(self.obj) is SuperscriptText:
            obj = cast(SuperscriptText, self.obj)
            if not all_html:
                print_str = obj.plain_str
            else:
                print_str = obj.html
        elif type(self.obj) is SubscriptText:
            obj = cast(SubscriptText, self.obj)
            if not all_html:
                print_str = obj.plain_str
            else:
                print_str = obj.html
        elif type(self.obj) is ItalicText:
            obj = cast(ItalicText, self.obj)
            if not all_html:
                print_str = obj.plain_str
            else:
                print_str = obj.html
        elif type(self.obj) is Gaiji:
            obj = cast(Gaiji, self.obj)
            use_tab, use_linebreak = True, not first
            print_str = obj.str_equivalent
        elif type(self.obj) is DefinitionNumber:
            obj = cast(DefinitionNumber, self.obj)
            use_tab, use_linebreak = True, not first
            print_str = f'{obj.num}.'
        elif type(self.obj) is RelatedWordLink:
            obj = cast(RelatedWordLink, self.obj)
            if not (link2html or all_html):
                print_str = obj.plain_str
            else:
                if type(obj.text) is str:
                    print_str = f'<a href="{obj.url}">{obj.text}</a>'
                elif type(obj.text) is RubyFuriganaWord:
                    print_str = f'<a href="{obj.url}">{obj.text.html}</a>'
                else:
                    raise TypeError
        elif type(self.obj) is RelatedWordLinkList:
            obj = cast(RelatedWordLinkList, self.obj)
            print_str = ''
            for link in obj:
                if not (link2html or all_html):
                    print_str += f'\n{tab}{link.plain_str}'
                else:
                    if type(link.text) is str:
                        print_str += f'\n<a href="{link.url}">{link.text}</a>'
                    elif type(link.text) is RubyFuriganaWord:
                        print_str += f'\n<a href="{link.url}">{link.text.html}</a>'
                    else:
                        raise TypeError
        elif type(self.obj) is Media:
            obj = cast(Media, self.obj)
            use_tab, use_linebreak = True, True
            if not (media2html or all_html):
                print_str = '[Media Links]'
            else:
                print_str = f'<a href="{obj.fullsize_img_link.url}"><img src="{obj.fullsize_img_link.url}" alt="Failed to load image."></a>'
        elif type(self.obj) is Table:
            obj = cast(Table, self.obj)
            use_tab, use_linebreak = True, True
            print_str = obj.to_df().__str__()
        elif type(self.obj) is TableList:
            obj = cast(Table, self.obj)
            print_str = ''
            for table in obj:
                print_str += f'\n{tab}' + table.to_df().__str__()
        elif type(self.obj) is LineBreak:
            obj = cast(LineBreak, self.obj)
            use_tab, use_linebreak = True, True
            print_str = ''
        elif type(self.obj) is RubyFuriganaWord:
            obj = cast(RubyFuriganaWord, self.obj)
            if furigana2html or all_html:
                print_str = obj.html
            else:
                print_str = obj.plain_str
        elif type(self.obj) is RuigigoList:
            obj = cast(RuigigoList, self.obj)
            if link2html or all_html:
                print_str = obj.html
            else:
                print_str = obj.plain_str
        elif type(self.obj) is RuigigoParsedItemGroup:
            obj = cast(RuigigoParsedItemGroup, self.obj)
            print_str = obj.custom_str(
                indent=indent, link2html=link2html,
                media2html=media2html, furigana2html=furigana2html,
                all_html=all_html
            )
        elif type(self.obj) is HeaderParsedItemGroup:
            obj = cast(HeaderParsedItemGroup, self.obj)
            return obj.custom_str(
                indent=indent,
                as_html=furigana2html or all_html
            )
        else:
            print_str = f'TODO ({self.obj.__class__.__name__})'
        if first:
            use_tab = True
        # if True:
        #     print_str = f'[{type(self.obj).__name__}]{print_str}'
        if use_tab:
            print_str = f'{tab}{print_str}'
        if use_linebreak:
            print_str = f'\n{print_str}'
        return print_str

    @property
    def class_name(self) -> str:
        return self.obj.__class__.__name__

    def to(self, target: str) -> Any:
        if hasattr(self.obj, f'to_{target}'):
            return getattr(self.obj, f'to_{target}')()
        else:
            raise Exception(f"{self.class_name} does not have a to_{target} method.")
    
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
        elif class_name == 'Hinshi':
            obj = Hinshi.from_dict(item_dict['obj'])
        elif class_name == 'BoldText':
            obj = BoldText.from_dict(item_dict['obj'])
        elif class_name == 'HeaderText':
            obj = HeaderText.from_dict(item_dict['obj'])
        elif class_name == 'KigoWord':
            obj = KigoWord.from_dict(item_dict['obj'])
        elif class_name == 'OriginWord':
            obj = OriginWord.from_dict(item_dict['obj'])
        elif class_name == 'MotoTsudzuri':
            obj = MotoTsudzuri.from_dict(item_dict['obj'])
        elif class_name == 'SuperscriptText':
            obj = SuperscriptText.from_dict(item_dict['obj'])
        elif class_name == 'SubscriptText':
            obj = SubscriptText.from_dict(item_dict['obj'])
        elif class_name == 'RekishiText':
            obj = RekishiText.from_dict(item_dict['obj'])
        elif class_name == 'ItalicText':
            obj = ItalicText.from_dict(item_dict['obj'])
        elif class_name == 'Gaiji':
            obj = Gaiji.from_dict(item_dict['obj'])
        elif class_name == 'DefinitionNumber':
            obj = DefinitionNumber.from_dict(item_dict['obj'])
        elif class_name == 'RelatedWordLink':
            obj = RelatedWordLink.from_dict(item_dict['obj'])
        elif class_name == 'RelatedWordLinkList':
            obj = RelatedWordLinkList.from_dict_list(item_dict['obj'])
        elif class_name == 'Media':
            obj = Media.from_dict(item_dict['obj'])
        elif class_name == 'Table':
            obj = Table.from_dict(item_dict['obj'])
        elif class_name == 'TableList':
            obj = TableList.from_dict_list(item_dict['obj'])
        elif class_name == 'LineBreak':
            obj = LineBreak.from_dict(item_dict['obj'])
        elif class_name == 'RubyFuriganaWord':
            obj = RubyFuriganaWord.from_dict(item_dict['obj'])
        elif class_name == 'RuigigoList':
            obj = RuigigoList.from_dict_list(item_dict['obj'])
        elif class_name == 'RuigigoParsedItemGroup':
            obj = RuigigoParsedItemGroup.from_dict_list(item_dict['obj'])
        elif class_name == 'HeaderParsedItemGroup':
            obj = HeaderParsedItemGroup.from_dict_list(item_dict['obj'])
        else:
            raise Exception(f'Cannot create ParsedItem from {class_name}.')
        return ParsedItem(obj=obj)

class BaseParsedItemList(
    BasicLoadableHandler[H, 'ParsedItem'],
    BasicHandler[H, 'ParsedItem']
):
    def __init__(self, item_list: List[ParsedItem]=None):
        super().__init__(obj_type=ParsedItem, obj_list=item_list)
        self.item_list = self.obj_list
    
    @property
    def preview_str(self) -> str:
        print_str = ''
        for item in self:
            print_str += item.preview_str
        return print_str

    @property
    def plain_str(self) -> str:
        print_str = ''
        for item in self:
            print_str += item.plain_str
        return print_str

    def custom_str(self, indent: int=0) -> str:
        print_str = ''
        first = True
        for item in self:
            if isinstance(item.obj, PlainText) and item.obj.is_empty:
                continue
            print_str += item.custom_str(indent=indent, first=first)
            if first:
                first = False
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> H:
        return cls([ParsedItem.from_dict(item_dict) for item_dict in dict_list])
    
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

class RuigigoParsedItemGroup(BaseParsedItemList['RuigigoParsedItemGroup']):
    def __init__(self, item_list: List[ParsedItem]=None):
        super().__init__(item_list=item_list)

    @property
    def plain_str(self) -> str:
        return '[類義語]\n' + super().plain_str
    
    def custom_str(
        self, indent: int=0,
        link2html: bool=False, media2html: bool=False,
        furigana2html: bool=False,
        all_html: bool=True
    ) -> str:
        tab = '\t' * indent
        print_str = ''
        if all_html:
            hidden_str = ''
            for item in self:
                if isinstance(item.obj, PlainText) and item.obj.is_empty:
                    continue
                hidden_str += item.custom_str(
                    indent=indent, first=True,
                    link2html=link2html,
                    media2html=media2html,
                    furigana2html=furigana2html,
                    all_html=all_html
                )
            print_str += tab + f'<details><summary>[類義語]</summary>{hidden_str}</details>'
        else:
            print_str += tab + '[類義語]\n'
            for item in self:
                if isinstance(item.obj, PlainText) and item.obj.is_empty:
                    continue
                print_str += item.custom_str(
                    indent=indent, first=True,
                    link2html=link2html,
                    media2html=media2html,
                    furigana2html=furigana2html,
                    all_html=all_html
                )
        return print_str

class HeaderParsedItemGroup(BaseParsedItemList['HeaderParsedItemGroup']):
    def __init__(self, item_list: List[ParsedItem]=None):
        super().__init__(item_list=item_list)
    
    def check_validity(self):
        invalid_class_names = []
        for class_name in self.class_name_list:
            if class_name not in ['PlainText', 'RubyFuriganaWord'] and class_name not in invalid_class_names:
                invalid_class_names.append(class_name)
        if len(invalid_class_names) > 0:
            list_str = ', '.join(invalid_class_names)
            raise TypeError(f"Invalid class names in HeaderParsedItemGroup: {list_str}")

    @property
    def plain_str(self) -> str:
        self.check_validity()
        return ''.join([obj.plain_str for obj in self])

    def custom_str(
        self, indent: int=0,
        as_html: bool=True
    ) -> str:
        tab = '\t' * indent
        print_str = tab
        if as_html:
            inner_str = ''
            for item in self:
                if isinstance(item.obj, PlainText):
                    obj = cast(PlainText, item.obj)
                    if obj.is_empty:
                        continue
                    else:
                        inner_str += obj.text
                elif isinstance(item.obj, RubyFuriganaWord):
                    obj = cast(RubyFuriganaWord, item.obj)
                    inner_str += obj.html
                else:
                    raise TypeError
            print_str += HeaderText(inner_str).html
        else:
            print_str += self.plain_str
        return print_str

class ParsedItemList(BaseParsedItemList['ParsedItemList']):
    def __init__(self, item_list: List[ParsedItem]=None):
        super().__init__(item_list=item_list)

    # def process_ruigigo_lists(self) -> ParsedItemList:
    #     ruigigo_list = cast(RuigigoList, None)
    #     is_ruigigo_list = False
    #     skip_count = 0

    #     result = ParsedItemList()

    #     for i in range(len(self)):
    #         if skip_count > 0:
    #             skip_count -= 1
    #             continue
    #         if self[i].class_name == 'PlainText' and cast(PlainText, self[i].obj).text.startswith('[類語]'):
    #             # remaining_text = cast(PlainText, self[i].obj).text.replace('[類語]', '')
    #             # if remaining_text != '':
    #             #     result.append(PlainText(remaining_text), is_obj=True)
    #             is_ruigigo_list = True
    #             ruigigo_list = RuigigoList()
    #             continue
    #         elif i < len(self) - 2 and self[i].class_name == 'PlainText' and self[i+2].class_name == 'PlainText' and self[i+1].class_name in ['PlainText', 'RelatedWordLink']:
    #             plain_text0 = cast(PlainText, self[i].obj)
    #             plain_text1 = cast(PlainText, self[i+2].obj)
    #             if plain_text0.text == '[' and plain_text1.text == ']':
    #                 if type(self[i+1].obj) is PlainText:
    #                     plain_text_middle = cast(PlainText, self[i+1].obj)
    #                     if plain_text_middle.text == '類語':
    #                         is_ruigigo_list = True
    #                         skip_count = 2
    #                 elif type(self[i+1].obj) is RelatedWordLink:
    #                     link = cast(RelatedWordLink, self[i+1].obj)
    #                     if type(link.text) is str:
    #                         if link.text == '類語':
    #                             is_ruigigo_list = True
    #                             skip_count = 2
    #                     elif type(link.text) is RubyFuriganaWord:
    #                         link_text = cast(RubyFuriganaWord, link.text)
    #                         if link_text.writing == '類語':
    #                             is_ruigigo_list = True
    #                             skip_count = 2
    #                     else:
    #                         raise TypeError
    #                 else:
    #                     raise Exception
    #             if is_ruigigo_list and ruigigo_list is None: # here
    #                 ruigigo_list = RuigigoList()
    #                 continue
    #         if not is_ruigigo_list:
    #             result.append(self[i])
    #         else:
    #             if self[i].class_name == 'RelatedWordLink':
    #                 ruigigo_list.append(cast(RelatedWordLink, self[i].obj))
    #             elif self[i].class_name == 'PlainText' and cast(PlainText, self[i].obj).text == '・':
    #                 continue # Do nothing
    #             elif self[i].class_name == 'DefinitionNumber':
    #                 # result.append(PlainText(str(cast(DefinitionNumber, self[i].obj).num)), is_obj=True)
    #                 continue
    #             elif self[i].class_name == 'PlainText' and cast(PlainText, self[i].obj).text in ['）', '／', '(', ')', '／（', '（']:
    #                 # result.append(self[i]) # Ignore these for now.
    #                 continue
    #             else:
    #                 is_ruigigo_list = False
    #                 if ruigigo_list is not None and len(ruigigo_list) > 0:
    #                     result.append(ruigigo_list, is_obj=True)
    #                     ruigigo_list = None
    #                 result.append(self[i])
    #     if ruigigo_list is not None and len(ruigigo_list) > 0:
    #         result.append(ruigigo_list, is_obj=True)
    #         ruigigo_list = None
    #     return result

    def process_ruigigo_group(self) -> ParsedItemList:
        # New approach.
        # Section Start at [類語] keyword
        # ruigigo section always continues until end of parsed item list

        ruigigo_group = cast(RuigigoParsedItemGroup, None)
        is_ruigigo_group = False
        skip_count = 0

        result = ParsedItemList()

        for i in range(len(self)):
            if skip_count > 0:
                skip_count -= 1
                continue
            if self[i].class_name == 'PlainText' and cast(PlainText, self[i].obj).text.startswith('[類語]'):
                is_ruigigo_group = True
                ruigigo_group = RuigigoParsedItemGroup()
                continue
            elif self[i].class_name == 'RelatedWordLink' \
                and '類語' in self[i].plain_str and i > 0 \
                and self[i-1].plain_str.endswith('[') \
                and i < len(self) - 1 \
                and self[i+1].plain_str.startswith(']'):
                is_ruigigo_group = True
                ruigigo_group = RuigigoParsedItemGroup()
                del result[-1]
                skip_count = 1
                continue
            elif i < len(self) - 2 and self[i].class_name == 'PlainText' and self[i+2].class_name == 'PlainText' and self[i+1].class_name in ['PlainText', 'RelatedWordLink']:
                # Not sure if this condition is needed anymore.
                plain_text0 = cast(PlainText, self[i].obj)
                plain_text1 = cast(PlainText, self[i+2].obj)
                if plain_text0.text == '[' and plain_text1.text == ']':
                    if type(self[i+1].obj) is PlainText:
                        plain_text_middle = cast(PlainText, self[i+1].obj)
                        if plain_text_middle.text == '類語':
                            is_ruigigo_group = True
                            skip_count = 2
                    elif type(self[i+1].obj) is RelatedWordLink:
                        link = cast(RelatedWordLink, self[i+1].obj)
                        if type(link.text) is str:
                            if link.text == '類語':
                                is_ruigigo_group = True
                                skip_count = 2
                        elif type(link.text) is RubyFuriganaWord:
                            link_text = cast(RubyFuriganaWord, link.text)
                            if link_text.writing == '類語':
                                is_ruigigo_group = True
                                skip_count = 2
                        else:
                            raise TypeError
                    else:
                        raise Exception
                if is_ruigigo_group and ruigigo_group is None:
                    ruigigo_group = RuigigoParsedItemGroup()
                    continue
            if not is_ruigigo_group:
                result.append(self[i])
            else:
                ruigigo_group.append(self[i])
        if ruigigo_group is not None and len(ruigigo_group) > 0:
            result.append(ruigigo_group, is_obj=True)
            ruigigo_group = None
        return result

    def group_items(self) -> ParsedItemGroupList:
        groups = []
        group_labels = []

        current_group = []
        current_group_label = None
        for i in range(len(self)):
            if self[i].class_name in ['Gaiji', 'DefinitionNumber']:
                if current_group_label is not None:
                    groups.append(current_group)
                    group_labels.append(current_group_label)
                    current_group = []
                    current_group_label = None
                if self[i].class_name == 'Gaiji':
                    current_group_label = 'gaiji_group'
                    current_group.append(self[i])
                elif self[i].class_name == 'DefinitionNumber':
                    current_group_label = 'definition_group'
                    current_group.append(self[i])
                else:
                    raise Exception
            else:
                if current_group_label is not None:
                    current_group.append(self[i])
                else:
                    current_group_label = 'misc'
                    current_group.append(self[i])
        if len(current_group) > 0:
            groups.append(current_group)
            group_labels.append(current_group_label)
            current_group = []
            current_group_label = None
        
        indent_label_buffer = []
        indent_val_buffer = []
        label_queue = []
        current_indent = 0
        for group, group_label in zip(groups, group_labels):
            if len(indent_label_buffer) == 0:
                indent_label_buffer.append(group_label)
                indent_val_buffer.append(current_indent)
                label_queue.append(group_label)
                if group_label in ['gaiji_group', 'definition_group']:
                    current_indent += 1
            elif len(indent_label_buffer) >= 1:
                if group_label in ['gaiji_group', 'definition_group']:
                    if indent_label_buffer[-1] == group_label:
                        current_indent -= 1
                        indent_label_buffer.append(group_label)
                        indent_val_buffer.append(current_indent)
                        current_indent += 1
                    elif group_label in label_queue:
                        while label_queue[-1] != group_label:
                            del label_queue[-1]
                            current_indent -= 1
                        current_indent -= 1
                        indent_label_buffer.append(group_label)
                        indent_val_buffer.append(current_indent)
                        current_indent += 1
                    elif group_label not in label_queue:
                        indent_label_buffer.append(group_label)
                        indent_val_buffer.append(current_indent)
                        label_queue.append(group_label)
                        current_indent += 1
                    else:
                        raise Exception
                else:
                    indent_label_buffer.append(group_label)
                    indent_val_buffer.append(current_indent)
        
        item_group_list = ParsedItemGroupList()
        for indent_label, indent_val, group in zip(indent_label_buffer, indent_val_buffer, groups):
            item_group = ParsedItemGroup(group_type=indent_label, item_list=ParsedItemList(group), indent=indent_val)
            if len(item_group_list) == 0:
                item_group_list.append(item_group)
            else:
                if item_group.indent > item_group_list[-1].indent:
                    relevant_item_group = item_group_list[-1]
                    while item_group.indent != relevant_item_group.indent + 1:
                        relevant_item_group = relevant_item_group.contained_groups[-1]
                    relevant_item_group.contained_groups.append(item_group)
                else:
                    item_group_list.append(item_group)
        return item_group_list

class ParsedItemGroup(BasicLoadableObject['ParsedItemGroup']):
    def __init__(self, group_type: str, item_list: ParsedItemList=None, indent: int=0, contained_groups: ParsedItemGroupList=None):
        super().__init__()
        self.group_type = group_type
        self.item_list = item_list if item_list is not None else ParsedItemList()
        self.indent = indent
        self.contained_groups = contained_groups if contained_groups is not None else ParsedItemGroupList()

    @property
    def plain_str(self) -> str:
        tab = '\t' * self.indent
        print_str = f"{tab}{''.join([item.obj.plain_str for item in self.item_list])}"
        for contained_group in self.contained_groups:
            print_str += '\n' + contained_group.plain_str
        return print_str

    def to_dict(self) -> dict:
        return {
            'group_type': self.group_type,
            'item_list': self.item_list.to_dict_list(),
            'indent': self.indent,
            'contained_groups': self.contained_groups.to_dict_list()
        }
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> ParsedItemGroup:
        return ParsedItemGroup(
            group_type=item_dict['group_type'],
            item_list=ParsedItemList.from_dict_list(item_dict['item_list']),
            indent=item_dict['indent'],
            contained_groups=ParsedItemGroupList.from_dict_list(item_dict['contained_groups'])
        )
    
    @property
    def has_contained(self) -> bool:
        return len(self.contained_groups) > 0
    
    def get_bounded_text(self, bound_start: str='「', bound_end: str='」') -> List[str]:
        text = self.plain_str
        left_split_list = text.split(bound_start)[1:]
        result = [part.split(bound_end)[0] for part in left_split_list]
        return [f'{bound_start}{part}{bound_end}' for part in result]

    @property
    def quotations(self) -> List[str]:
        return self.get_bounded_text(bound_start='「', bound_end='」')

class ParsedItemGroupList(
    BasicLoadableHandler['ParsedItemGroupList', 'ParsedItemGroup'],
    BasicHandler['ParsedItemGroupList', 'ParsedItemGroup']
):
    def __init__(self, group_list: List[ParsedItemGroup]=None):
        super().__init__(obj_type=ParsedItemGroup, obj_list=group_list)
        self.group_list = self.obj_list
    
    @property
    def plain_str(self) -> str:
        print_str = ''
        for i, item_group in enumerate(self):
            if i == 0:
                print_str += item_group.plain_str
            else:
                print_str += '\n' + item_group.plain_str
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> ParsedItemGroupList:
        return ParsedItemGroupList([ParsedItemGroup.from_dict(item_dict) for item_dict in dict_list])

    @property
    def quotations(self) -> List[str]:
        result = []
        for item_group in self:
            result.extend(item_group.quotations)
        return result

class ParsedItemListHandler(
    BasicLoadableHandler['ParsedItemListHandler', 'ParsedItemList'],
    BasicHandler['ParsedItemListHandler', 'ParsedItemList']
):
    def __init__(self, item_list_list: List[ParsedItemList]=None):
        super().__init__(obj_type=ParsedItemList, obj_list=item_list_list)
        self.item_list_list = self.obj_list
    
    @property
    def preview_str(self) -> str:
        print_str = ''
        for i, item_list in enumerate(self):
            if i == 0:
                print_str += item_list.preview_str
            else:
                print_str += f'\n{item_list.preview_str}'
        return print_str

    def custom_str(self, indent: int=0) -> str:
        print_str = ''
        for i, item_list in enumerate(self):
            if i == 0:
                print_str += item_list.custom_str(indent=indent)
            else:
                print_str += f'\n{item_list.custom_str(indent=indent)}'
        return print_str

    def to_dict_list(self) -> List[List[dict]]:
        return [item_list.to_dict_list() for item_list in self]
    
    @classmethod
    def from_dict_list(cls, dict_list: List[List[dict]]) -> ParsedItemListHandler:
        return ParsedItemListHandler([ParsedItemList.from_dict_list(item_dict) for item_dict in dict_list])
    
    @property
    def class_name_list_list(self) -> List[List[str]]:
        return [item_list.class_name_list for item_list in self]
    
    def contains_class_names(self, class_names: List[str], operator: str='and') -> bool:
        return any([item_list.contains_class_names(class_names, operator=operator) for item_list in self])

def parse_ruby_html(ruby_html: Tag) -> RubyFuriganaWord:
    rb_html = ruby_html.find(name='rb')
    assert rb_html is not None
    rb_text = rb_html.text.strip()
    rt_html = ruby_html.find(name='rt')
    assert rt_html is not None
    rt_text = rt_html.text.strip()
    ruby_furigana_word = RubyFuriganaWord(writing=rb_text, reading=rt_text)
    return ruby_furigana_word

def parse_heading_html(heading_html: Tag) -> HeaderParsedItemGroup:
    group = HeaderParsedItemGroup()
    for child in heading_html.children:
        if type(child) is NavigableString:
            group.append(PlainText(str(child)), is_obj=True)
        elif type(child) is Tag:
            parse_tag(item_list=group, child=child)
        else:
            raise TypeError
    return group

gaiji_map = {
    1: '一',
    2: '二',
    3: '三',
    4: '四',
    5: '五',
    6: '六',
    7: '七',
    8: '八',
    9: '九',
    10: '十'
}

def parse_tag(item_list: ParsedItemList, child: Tag):
    if 'class' in child.attrs and child.attrs['class'] == ['gaiji']:
        gaiji_url = child.attrs['src']
        gaiji_root_int = int(get_rootname_from_path(gaiji_url))
        if gaiji_root_int >= 2539 and gaiji_root_int <= 2546:
            gaiji_type = 'black_gaiji_number'
            gaiji_int_equivalent = gaiji_root_int - 2538
        elif gaiji_root_int >= 2531 and gaiji_root_int <= 2538:
            gaiji_type = 'white_gaiji_number'
            gaiji_int_equivalent = gaiji_root_int - 2530
        else:
            raise Exception(
                f"""
                gaiji_root_int={gaiji_root_int} is not in an acceptable range.
                """
            )
        assert gaiji_int_equivalent in gaiji_map, f'{gaiji_int_equivalent} not in gaiji_map.\nurl: {self.url}\ntitle: {self.title}'
        gaiji_str_equivalent = gaiji_map[gaiji_int_equivalent]
        gaiji = Gaiji(
            url=gaiji_url,
            int_equivalent=gaiji_int_equivalent,
            str_equivalent=gaiji_str_equivalent
        )
        item_list.append(gaiji, is_obj=True)
    elif 'class' in child.attrs and child.attrs['class'] == ['hinshi']:
        hinshi_text = child.text.strip()
        hinshi = Hinshi(text=hinshi_text)
        item_list.append(hinshi, is_obj=True)
    elif len(child.attrs) == 0 and child.text.strip() == '':
        pass # Ignore. Usually just a <br> or <br/>
        # item_list.append(LineBreak(), is_obj=True)
    elif len(child.attrs) == 0 and str.isdigit(child.text.strip()):
        definition_number_int = int(child.text.strip())
        definition_number = DefinitionNumber(num=definition_number_int)
        item_list.append(definition_number, is_obj=True)
    elif 'org' in child.attrs and child.attrs['org'] == '―':
        origin_word_text = child.text.strip()
        origin_word = OriginWord(origin_word_text)
        item_list.append(origin_word, is_obj=True)
    elif child.name == 'spellout' and 'org' in child.attrs and child.attrs['org'] == '—':
        text = child.text.strip()
        bold_text = BoldText(text) # Too lazy to create a new class for this.
        item_list.append(bold_text, is_obj=True)
    elif child.name == 'ruby':
        ruby_furigana_word = parse_ruby_html(child)
        item_list.append(ruby_furigana_word, is_obj=True)
    elif 'href' in child.attrs and child.name == 'a':
        related_word_url = f"https://kotobank.jp{child['href']}"
        ruby_html = child.find(name='ruby')
        if ruby_html is None:
            related_word_text = child.text.strip()
        else:
            related_word_text = parse_ruby_html(child)
        related_word_link = RelatedWordLink(url=related_word_url, text=related_word_text)
        item_list.append(related_word_link, is_obj=True)
    elif len(child.attrs) == 0 and child.name == 'b' and len(child.text.strip()) > 0:
        bold_text_str = child.text.strip()
        bold_text = BoldText(bold_text_str)
        item_list.append(bold_text, is_obj=True)
    elif child.name == 'span' and 'class' in child.attrs and child['class'] == ['kigo']:
        kigo_text = child.text.strip()
        kigo_word = KigoWord(kigo_text)
        item_list.append(kigo_word, is_obj=True)
    elif 'class' in child.attrs and child['class'] == ['media'] and child.name == 'div':
        fullsize_link_html = child.find(name='a', href=True)
        assert fullsize_link_html is not None
        fullsize_img_url = f"https://kotobank.jp{fullsize_link_html['href']}"
        fullsize_img_link = Link(url=fullsize_img_url)
        smallsize_img_html = (
            fullsize_link_html
            .find(name='p', attrs={'class': 'image'})
            .find(name='img')
        )
        smallsize_img_url = f"https://kotobank.jp{smallsize_img_html['src']}"
        smallsize_img_link = Link(url=smallsize_img_url)
        media = Media(
            fullsize_img_link=fullsize_img_link,
            smallsize_img_link=smallsize_img_link
        )
        item_list.append(media, is_obj=True)
    elif child.name == 'br' and 'clear' in child.attrs and child.attrs['clear'] == 'all':
        pass # Ignore. Appears to come after a media tag.
    elif child.name == 'span' and 'type' in child.attrs and child.attrs['type'] == '原綴':
        mototsudzuri_text = child.text.strip()
        mototsudzuri = MotoTsudzuri(mototsudzuri_text)
        item_list.append(mototsudzuri, is_obj=True)
    elif child.name == 'br' and len(child.attrs) == 0 and len(child.text.strip()) > 0 and len(child.find_all(name='a', href=True)) > 0:
        related_word_html_list = child.find_all(name='a', href=True)
        related_word_link_list = RelatedWordLinkList()
        for related_word_html in related_word_html_list:
            related_word_url = f"https://kotobank.jp{related_word_html['href']}"
            related_word_text = related_word_html.text.strip()
            related_word_link = RelatedWordLink(url=related_word_url, text=related_word_text)
            related_word_link_list.append(related_word_link)
        item_list.append(related_word_link_list, is_obj=True)
    elif child.name == 'sup' and len(child.attrs) == 0 and len(child.text.strip()) > 0:
        superscript_text_str = child.text.strip()
        superscript_text = SuperscriptText(superscript_text_str)
        item_list.append(superscript_text, is_obj=True)
    elif child.name == 'sub' and len(child.attrs) == 0 and len(child.text.strip()) > 0:
        subscript_text_str = child.text.strip()
        subscript_text = SubscriptText(subscript_text_str)
        item_list.append(subscript_text, is_obj=True)
    elif child.name == 'br' and len(child.attrs) == 0 and child.find(name='table') is not None:
        table_html = child.find(name='table')
        table_dfs = pd.read_html(str(child))
        table_dicts = [table_df.to_dict() for table_df in table_dfs]
        table_list = TableList([Table(item_dict) for item_dict in table_dicts])
        item_list.append(table_list, is_obj=True)
    elif child.name == 'span' and 'type' in child.attrs and child.attrs['type'] == '歴史':
        rekishi_text_str = child.text.strip()
        rekishi_text = RekishiText(rekishi_text_str)
        item_list.append(rekishi_text, is_obj=True)
    elif child.name == 'i' and len(child.attrs) == 0 and len(child.text.strip()) > 0:
        italic_text_str = child.text.strip()
        italic_text = ItalicText(italic_text_str)
        item_list.append(italic_text, is_obj=True)
    elif child.name == 'br' and len(child.find_all(name='br')) > 1:
        # Nested br block
        # TODO: Might need to fix this later on.
        item_list.append(PlainText(child.text.strip()), is_obj=True)
    else:
        logger.red(f'TODO')
        logger.red(f'\tchild.text.strip(): {child.text.strip()}')
        logger.red(f'\tchild.name: {child.name}')
        logger.red(f'\tchild.attrs: {child.attrs}')
        logger.red(child)
        raise Exception

def parse(ex_cf_html_list: List[Tag]):
    item_list_handler = ParsedItemListHandler()
    for i, ex_cf_html in enumerate(ex_cf_html_list):
        item_list = ParsedItemList()
        if i > 0:
            item_list.append(LineBreak(), is_obj=True)
        heading_html = ex_cf_html.find(name='h3')
        if heading_html is not None:
            heading_group = parse_heading_html(heading_html)
            item_list.append(heading_group, is_obj=True)
            # heading_text = heading_html.text.strip()
            # item_list.append(HeaderText(heading_text), is_obj=True)
            item_list.append(LineBreak(), is_obj=True)
        description_html = ex_cf_html.find(name='section', attrs={'class': 'description'})
        has_description = description_html is not None
        assert has_description, 'No description found.'
        for child in description_html.children:
            if type(child) is NavigableString:
                text = str(child)
                plain_text = PlainText(text)
                item_list.append(plain_text, is_obj=True)
            elif type(child) is Tag:
                parse_tag(item_list=item_list, child=child)
        item_list = item_list.process_ruigigo_group()
        item_list_handler.append(item_list)
    return item_list_handler