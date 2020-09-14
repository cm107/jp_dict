from __future__ import annotations
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler
from ..common import Link
from typing import List, Any
import pandas as pd
from logger import logger

# Simple Text
class PlainText(BasicLoadableObject['PlainText']):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
    
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

class RelatedWordLink(Link):
    def __init__(self, url: str, text: str):
        super().__init__(url=url, text=text)

    @property
    def plain_str(self) -> str:
        return f'[{self.text}]'

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
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> TableList:
        return TableList([Table.from_dict(item_dict) for item_dict in dict_list])

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

class ParsedItem(BasicLoadableObject['ParsedItem']):
    def __init__(self, obj: Any):
        super().__init__()

        assert hasattr(obj, 'to_dict') or hasattr(obj, 'to_dict_list')
        assert hasattr(obj, 'from_dict') or hasattr(obj, 'from_dict_list')
        self.obj = obj
    
    def preview_str(self) -> str:
        from typing import cast
        if type(self.obj) in [PlainText, Hinshi, KigoWord, MotoTsudzuri, RekishiText]:
            obj = cast(PlainText, self.obj)
            return obj.text
        elif type(self.obj) is BoldText:
            obj = cast(BoldText, self.obj)
            return SpecialString(obj.text).bold.end.text
        elif type(self.obj) is OriginWord:
            obj = cast(OriginWord, self.obj)
            return SpecialString(obj.text).underline.end.text
        elif type(self.obj) is SuperscriptText:
            obj = cast(SuperscriptText, self.obj)
            return f'^{obj.text}'
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
            return SpecialString(obj.text).bold.underline.end.text
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
        else:
            return f'TODO ({self.obj.__class__.__name__})'

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
        elif class_name == 'KigoWord':
            obj = KigoWord.from_dict(item_dict['obj'])
        elif class_name == 'OriginWord':
            obj = OriginWord.from_dict(item_dict['obj'])
        elif class_name == 'MotoTsudzuri':
            obj = MotoTsudzuri.from_dict(item_dict['obj'])
        elif class_name == 'SuperscriptText':
            obj = SuperscriptText.from_dict(item_dict['obj'])
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
                    # print(f'Ignoring: {self[i].class_name}')
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
            # tab = '\t'*indent_val
            # logger.cyan(f"{tab}{indent_label} {[item.class_name for item in group]}")
            # logger.purple(f"{tab}{''.join([item.obj.plain_str for item in group])}")

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
        # logger.blue(item_group_list.plain_str)
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

class ParsedItemListHandler(
    BasicLoadableHandler['ParsedItemListHandler', 'ParsedItemList'],
    BasicHandler['ParsedItemListHandler', 'ParsedItemList']
):
    def __init__(self, item_list_list: List[ParsedItemList]=None):
        super().__init__(obj_type=ParsedItemList, obj_list=item_list_list)
        self.item_list_list = self.obj_list
    
    def preview_str(self) -> str:
        print_str = ''
        for i, item_list in enumerate(self):
            if i == 0:
                print_str += item_list.preview_str()
            else:
                print_str += f'\n{item_list.preview_str()}'
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