from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import List
import bs4
from bs4 import BeautifulSoup

from logger import logger
from common_utils.check_utils import check_list_length, check_type, check_type_from_list
from ...util.char_lists import circle_number_char2int

class KotobankExample:
    def __init__(self, text: str):
        self.text = text

    def __str__(self) -> str:
        return f'Example: {self.text}'
    
    def __repr__(self) -> str:
        return self.__str__()

    def custom_str(self, ex_num: int=None, indent: int=0):
        indent_str = '\t' * indent
        ex_num_str = f'{ex_num}: ' if ex_num is not None else ''
        return f'{indent_str}{ex_num_str}{self.text}'

class KotobankExampleHandler:
    def __init__(self, examples: List[KotobankExample]=None):
        self.examples = examples if examples is not None else []

    def __str__(self) -> str:
        print_str = 'Examples:'
        ex_num = 0
        for example in self.examples:
            ex_num += 1
            print_str += f'\n{example.custom_str(ex_num=ex_num, indent=1)}'
        return print_str

    def __repr__(self) -> str:
        return self.__str__()

    def custom_str(self, show_ex_num: bool=False, indent: int=0) -> str:
        print_str = ''
        ex_num = 0
        for example in self.examples:
            ex_num += 1
            if ex_num == 1:
                print_str += f'{example.custom_str(ex_num=ex_num if show_ex_num else None, indent=indent)}'
            else:
                print_str += f'\n{example.custom_str(ex_num=ex_num if show_ex_num else None, indent=indent)}'
        return print_str

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> KotobankExample:
        if len(self.examples) == 0:
            logger.error(f"KotobankExampleHandler is empty.")
            raise IndexError
        elif idx < 0 or idx >= len(self.examples):
            logger.error(f"Index out of range: {idx}")
            raise IndexError
        else:
            return self.examples[idx]

    def __setitem__(self, idx: int, value: KotobankExample):
        check_type(value, valid_type_list=[KotobankExample])
        self.examples[idx] = value

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self) -> KotobankExample:
        if self.n < len(self.examples):
            result = self.examples[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def append(self, example: KotobankExample):
        check_type(example, valid_type_list=[KotobankExample])
        self.examples.append(example)

class KotobankDefinition:
    def __init__(self, definition_text: str, example_handler: KotobankExampleHandler=None):
        self.definition_text = definition_text
        self.example_handler = example_handler if example_handler is not None else KotobankExampleHandler()

    def __str__(self) -> str:
        print_str = f'Definition: {self.definition_text}'
        if len(self.example_handler) > 0:
            print_str += '\n\tExamples:'
            print_str += f'\n{self.example_handler.custom_str(show_ex_num=True, indent=2)}'
        return print_str

    def __repr__(self) -> str:
        return self.__str__()

    def custom_str(self, def_num: int=None, show_examples: bool=True, show_ex_num: bool=True, indent: int=0):
        if def_num is not None:
            print_str = '\t' * indent + f'{def_num}: {self.definition_text}'
        else:
            print_str = '\t' * indent + f'{self.definition_text}'
        if show_examples and len(self.example_handler) > 0:
            print_str += '\n' + '\t' * (indent + 1) + 'Examples:'
            print_str += '\n' + self.example_handler.custom_str(show_ex_num=show_ex_num, indent=indent+2)
        return print_str

class KotobankDefinitionHandler:
    def __init__(self, definitions: List[KotobankDefinition]=None):
        self.definitions = definitions if definitions is not None else []

    def __str__(self) -> str:
        print_str = 'Definitions:'
        if len(self.definitions) > 0:
            def_num = 0
            for definition in self.definitions:
                def_num += 1
                print_str += '\n' + definition.custom_str(
                    def_num=def_num,
                    show_examples=True, show_ex_num=True,
                    indent=1
                )
        return print_str

    def __repr__(self) -> str:
        return self.__str__()

    def custom_str(self, show_def_num: bool=True, show_examples: bool=True, show_ex_num: bool=True, indent: int=0) -> str:
        print_str = ''
        def_num = 0
        for definition in self.definitions:
            def_num += 1
            def_str = definition.custom_str(
                def_num=def_num if show_def_num else None,
                show_examples=show_examples,
                show_ex_num=show_ex_num,
                indent=indent
            )
            if def_num == 1:
                print_str += def_str
            else:
                print_str += f'\n{def_str}'
        return print_str

    def __len__(self) -> int:
        return len(self.definitions)

    def __getitem__(self, idx: int) -> KotobankDefinition:
        if len(self.definitions) == 0:
            logger.error(f"KotobankDefinitionHandler is empty.")
            raise IndexError
        elif idx < 0 or idx >= len(self.definitions):
            logger.error(f"Index out of range: {idx}")
            raise IndexError
        else:
            return self.definitions[idx]

    def __setitem__(self, idx: int, value: KotobankDefinition):
        check_type(value, valid_type_list=[KotobankDefinition])
        self.definitions[idx] = value

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self) -> KotobankDefinition:
        if self.n < len(self.definitions):
            result = self.definitions[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def append(self, definition: KotobankDefinition):
        check_type(definition, valid_type_list=[KotobankDefinition])
        self.definitions.append(definition)

class KotobankUsage:
    def __init__(self, usage_text: str=None, definition_handler: KotobankDefinitionHandler=None):
        self.usage_text = usage_text
        self.definition_handler = definition_handler if definition_handler is not None else KotobankDefinitionHandler()

    def __str__(self) -> str:
        print_str = ''
        if self.usage_text is not None:
            print_str += self.usage_text
            if len(self.definition_handler) > 0:
                print_str += '\n'
        print_str += self.definition_handler.custom_str(
            show_def_num=True,
            show_examples=True,
            show_ex_num=True,
            indent=0
        )
        return print_str

    def __repr__(self) -> str:
        return self.__str__()

    def custom_str(
        self,
        show_usage: bool=True, show_definitions: bool=True,
        show_def_num: bool=True, show_examples: bool=True,
        show_ex_num: bool=True, indent: int=0
    ) -> str:
        print_str = ''
        if self.usage_text is not None and show_usage:
            print_str += self.usage_text
            if len(self.definition_handler) > 0 and show_definitions:
                print_str += '\n'
        if show_definitions:
            print_str += self.definition_handler.custom_str(
                show_def_num=show_def_num,
                show_examples=show_examples,
                show_ex_num=show_ex_num,
                indent=indent
            )
        return print_str

class KotobankUsageHandler:
    def __init__(self, usages: List[KotobankUsage]=None):
        self.usages = usages if usages is not None else []

    def __str__(self) -> str:
        print_str = ''
        usage_num = 0
        for usage in self.usages:
            usage_num += 1
            usage_str = usage.custom_str(
                show_usage=True,
                show_definitions=True,
                show_def_num=True,
                show_examples=True,
                show_ex_num=True,
                indent=0
            )
            if usage_num > 1:
                print_str += '\n'
            print_str += usage_str
        return print_str

    def __repr__(self) -> str:
        return self.__str__()

    def custom_str(
        self,
        show_usage: bool=True, show_definitions: bool=True,
        show_def_num: bool=True, show_examples: bool=True,
        show_ex_num: bool=True, indent: int=0
    ) -> str:
        print_str = ''
        usage_num = 0
        for usage in self.usages:
            usage_num += 1
            usage_str = usage.custom_str(
                show_usage=show_usage,
                show_definitions=show_definitions,
                show_def_num=show_def_num,
                show_examples=show_examples,
                show_ex_num=show_ex_num,
                indent=indent
            )
            if usage_num > 1:
                print_str += '\n'
            print_str += usage_str
        return print_str

    def __len__(self) -> int:
        return len(self.usages)

    def __getitem__(self, idx: int) -> KotobankUsage:
        if len(self.usages) == 0:
            logger.error(f"KotobankUsageHandler is empty.")
            raise IndexError
        elif idx < 0 or idx >= len(self.usages):
            logger.error(f"Index out of range: {idx}")
            raise IndexError
        else:
            return self.usages[idx]

    def __setitem__(self, idx: int, value: KotobankUsage):
        check_type(value, valid_type_list=[KotobankUsage])
        self.usages[idx] = value

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self) -> KotobankUsage:
        if self.n < len(self.usages):
            result = self.usages[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def append(self, usage: KotobankUsage):
        check_type(usage, valid_type_list=[KotobankUsage])
        self.usages.append(usage)

class KotobankDictionary(metaclass=ABCMeta):
    def __init__(self, specific_writing: str, specific_reading: str, usage_handler: KotobankUsageHandler=None):
        """
        TODO: Model after the following structure:
        {
            usage_number: {
                'usage_text': usage_text,
                'definitions': {
                    definition_number: {
                        'definition_text': definition_text,
                        'examples': [example0, example1, ...]
                    }
                }
            }
        }
        """
        self.specific_writing = specific_writing
        self.specific_reading = specific_reading
        self.usage_handler = usage_handler if usage_handler is not None else KotobankUsageHandler()

    def __str__(self) -> str:
        print_str = 'Kotobank Dictionary'
        if self.specific_writing is not None and self.specific_reading is not None:
            print_str += f'\n\t{self.specific_writing} ({self.specific_reading})'
        elif self.specific_writing is not None and self.specific_reading is None:
            print_str += f'\n\t{self.specific_writing}'
        elif self.specific_writing is None and self.specific_reading is not None:
            print_str += f'\n\t{self.specific_reading}'
        else:
            pass
        print_str += '\n'
        if len(self.usage_handler) > 0:
            print_str += self.usage_handler.custom_str(
                show_usage=True,
                show_definitions=True,
                show_def_num=True,
                show_examples=True,
                show_ex_num=True,
                indent=1
            )
        return print_str

    def __repr__(self) -> str:
        return self.__str__()

    def custom_str(
        self,
        show_specific_writing: bool=True, show_specific_reading: bool=True,
        show_usage: bool=True, show_definitions: bool=True, show_def_num: bool=True,
        show_examples: bool=True, show_ex_num: bool=True, indent: int=0
    ) -> str:
        print_str = ''
        show_writing = self.specific_writing is not None and show_specific_writing
        show_reading = self.specific_reading is not None and show_specific_writing
        if show_writing and show_reading:
            print_str += '\t' * indent + f'{self.specific_writing} ({self.specific_reading})'
        elif show_writing and not show_reading:
            print_str += '\t' * indent + f'{self.specific_writing}'
        elif not show_writing and show_reading:
            print_str += '\t' * indent + f'{self.specific_reading}'
        else:
            pass
        if show_writing or show_reading and len(self.usage_handler) > 0:
            print_str += '\n'
        if len(self.usage_handler) > 0:
            print_str += self.usage_handler.custom_str(
                show_usage=show_usage,
                show_definitions=show_definitions,
                show_def_num=show_def_num,
                show_examples=show_examples,
                show_ex_num=show_ex_num,
                indent=indent
            )
        return print_str

    @classmethod
    @abstractmethod
    def from_description(cls, specific_writing: str, specific_reading: str, description_html: bs4.element.Tag) -> KotobankDictionary:
        raise NotImplementedError

    @staticmethod
    def _remove_html_from_str(html_str: str) -> str:
        return (
            BeautifulSoup(html_str, 'html.parser').text
            .replace(' ', '')
            .replace('\n', '')
        )

class DigitalDaijisenDictionary(KotobankDictionary):
    def __init__(self, specific_writing: str, specific_reading: str, usage_handler: KotobankUsageHandler=None):
        super().__init__(
            specific_writing=specific_writing,
            specific_reading=specific_reading,
            usage_handler=usage_handler
        )

    def __str__(self) -> str:
        print_str = 'デジタル大辞泉の解説'
        print_str += '\n'
        print_str += super().custom_str(
            show_specific_writing=True, show_specific_reading=True,
            show_usage=True, show_definitions=True,
            show_def_num=True, show_examples=True,
            show_ex_num=True, indent=1
        )
        return print_str

    def __repr__(self) -> str:
        return self.__str__()

    def custom_str(
        self,
        show_specific_writing: bool=True, show_specific_reading: bool=True,
        show_usage: bool=True, show_definitions: bool=True, show_def_num: bool=True,
        show_examples: bool=True, show_ex_num: bool=True, indent: int=0
    ) -> str:
        print_str = 'デジタル大辞泉の解説'
        print_str += '\n'
        print_str += super().custom_str(
            show_specific_writing=show_specific_writing,
            show_specific_reading=show_specific_reading,
            show_usage=show_usage,
            show_definitions=show_definitions,
            show_def_num=show_def_num,
            show_examples=show_examples,
            show_ex_num=show_ex_num,
            indent=indent
        )
        return print_str

    @classmethod
    def from_description(cls, specific_writing: str, specific_reading: str, description_html: bs4.element.Tag) -> DigitalDaijisenDictionary:
        kotobank_dict = DigitalDaijisenDictionary(specific_writing=specific_writing, specific_reading=specific_reading)
        def_numbers = [int(number.text) for number in description_html.find_all(name='b')]
        usage_text_list = [
            hinshi_html.text \
                for hinshi_html in description_html.find_all(name='span', class_='hinshi')
        ]
        logger.yellow(f'def_numbers: {def_numbers}')
        logger.yellow(f'usage_text_list: {usage_text_list}')
        for j, child in enumerate(list(description_html.children)):
            logger.white(f'{j}: {child}')
        usage_dict = {}
        current_usage_number = 0
        definition_dict = {}
        if len(def_numbers) > 0:
            children = list(description_html.children)
            current_def_number = None
            for j, child in enumerate(children):
                if '<b>' in str(child) and '</b>' in str(child):
                    next_def_number = int(child.text)
                    if current_def_number is None or next_def_number > current_def_number:
                        current_def_number = next_def_number
                    else:
                        current_usage_number += 1
                        logger.blue(f'current_usage_number: {current_usage_number}')
                        usage_dict[current_usage_number] = {
                            'usage_text': usage_text_list[current_usage_number - 1] if current_usage_number <= len(usage_text_list) else None,
                            'definitions': definition_dict
                        }
                        definition_dict = {}
                    definition_dict[current_def_number] = ''
                else:
                    if current_def_number is not None:
                        definition_dict[current_def_number] += cls._remove_html_from_str(str(child))
        else:
            description_text = description_html.text.replace(' ', '').replace('\n', '')
            definition_dict[1] = description_text

        # logger.cyan(definition_dict)
        logger.cyan(usage_dict)

        def_handler = KotobankDefinitionHandler()
        for def_num, def_text in definition_dict.items():
            def_handler.append(
                definition=KotobankDefinition(definition_text=def_text)
            )
        usage = KotobankUsage(definition_handler=def_handler)
        kotobank_dict.usage_handler.append(usage)
        logger.purple(f'kotobank_dict:\n{kotobank_dict}')

        return kotobank_dict

class DaijirinDaisenpanDictionary(KotobankDictionary):
    def __init__(self, specific_writing: str, specific_reading: str, usage_handler: KotobankUsageHandler=None):
        super().__init__(
            specific_writing=specific_writing,
            specific_reading=specific_reading,
            usage_handler=usage_handler
        )

    def __str__(self) -> str:
        print_str = '大辞林 第三版の解説'
        print_str += '\n'
        print_str += super().custom_str(
            show_specific_writing=True, show_specific_reading=True,
            show_usage=True, show_definitions=True,
            show_def_num=True, show_examples=True,
            show_ex_num=True, indent=1
        )
        return print_str

    def __repr__(self) -> str:
        return self.__str__()

    def custom_str(
        self,
        show_specific_writing: bool=True, show_specific_reading: bool=True,
        show_usage: bool=True, show_definitions: bool=True, show_def_num: bool=True,
        show_examples: bool=True, show_ex_num: bool=True, indent: int=0
    ) -> str:
        print_str = '大辞林 第三版の解説'
        print_str += '\n'
        print_str += super().custom_str(
            show_specific_writing=show_specific_writing,
            show_specific_reading=show_specific_reading,
            show_usage=show_usage,
            show_definitions=show_definitions,
            show_def_num=show_def_num,
            show_examples=show_examples,
            show_ex_num=show_ex_num,
            indent=indent
        )
        return print_str

    @classmethod
    def from_description(cls, specific_writing: str, specific_reading: str, description_html: bs4.element.Tag) -> DaijirinDaisenpanDictionary:
        raise NotImplementedError


class SeisenpanNihonkokugoDaijishoDictionary(KotobankDictionary):
    def __init__(self, specific_writing: str, specific_reading: str, usage_handler: KotobankUsageHandler=None):
        super().__init__(
            specific_writing=specific_writing,
            specific_reading=specific_reading,
            usage_handler=usage_handler
        )

    def __str__(self) -> str:
        print_str = '精選版 日本国語大辞典の解説'
        print_str += '\n'
        print_str += super().custom_str(
            show_specific_writing=True, show_specific_reading=True,
            show_usage=True, show_definitions=True,
            show_def_num=True, show_examples=True,
            show_ex_num=True, indent=1
        )
        return print_str

    def __repr__(self) -> str:
        return self.__str__()

    def custom_str(
        self,
        show_specific_writing: bool=True, show_specific_reading: bool=True,
        show_usage: bool=True, show_definitions: bool=True, show_def_num: bool=True,
        show_examples: bool=True, show_ex_num: bool=True, indent: int=0
    ) -> str:
        print_str = '精選版 日本国語大辞典の解説'
        print_str += '\n'
        print_str += super().custom_str(
            show_specific_writing=show_specific_writing,
            show_specific_reading=show_specific_reading,
            show_usage=show_usage,
            show_definitions=show_definitions,
            show_def_num=show_def_num,
            show_examples=show_examples,
            show_ex_num=show_ex_num,
            indent=indent
        )
        return print_str

    @classmethod
    def from_description(cls, specific_writing: str, specific_reading: str, description_html: bs4.element.Tag) -> SeisenpanNihonkokugoDaijishoDictionary:
        raise NotImplementedError

class KotobankDictionaryHandler:
    def __init__(self, dictionary_list: List[KotobankDictionary]=None):
        if dictionary_list is not None:
            self._check_valid(dictionary_list)
            self.dictionary_list = dictionary_list
        else:
            self.dictionary_list = []

    @staticmethod
    def _check_valid(dictionary_list: List[KotobankDictionary]):
        valid_type_list = [
            DigitalDaijisenDictionary,
            DaijirinDaisenpanDictionary,
            SeisenpanNihonkokugoDaijishoDictionary
        ]
        check_type_from_list(item_list=dictionary_list, valid_type_list=valid_type_list)

    def add(self, dictionary: KotobankDictionary):
        self._check_valid([dictionary])
        self.dictionary_list.append(dictionary)

    def add_from_description(self, dict_name: str, specific_writing: str, specific_reading: str, description_html: bs4.element.Tag):
        if dict_name == 'デジタル大辞泉':
            kotobank_dictionary = DigitalDaijisenDictionary.from_description(
                specific_writing=specific_writing, specific_reading=specific_reading,
                description_html=description_html
            )
        elif dict_name == '大辞林 第三版':
            return # debug
            kotobank_dictionary = DaijirinDaisenpanDictionary.from_description(
                specific_writing=specific_writing, specific_reading=specific_reading,
                description_html=description_html
            )
        elif dict_name == '精選版 日本国語大辞典':
            return # debug
            kotobank_dictionary = SeisenpanNihonkokugoDaijishoDictionary.from_description(
                specific_writing=specific_writing, specific_reading=specific_reading,
                description_html=description_html
            )
        else:
            logger.error(f'The following dict_name is not yet supported: {dict_name}')
            # raise NotImplementedError
            return # debug
        self.add(kotobank_dictionary)

class KotobankContent:
    def __init__(self, main_writing: str, main_reading: str, dict_handler: KotobankDictionaryHandler=None):
        self.main_writing = main_writing
        self.main_reading = main_reading
        self.dict_handler = dict_handler if dict_handler is not None else KotobankDictionaryHandler()

    @staticmethod
    def _parse_content_html(soup: BeautifulSoup) -> bs4.element.Tag:
        content_area = (
            soup.find(name='body', class_='pageWord winpc')
            .find(name='div', class_='bodyWrap')
            .find(name='div', id='contentArea')
        )
        return content_area

    @staticmethod
    def _parse_main_writing_and_reading(content_html: bs4.element.Tag) -> (str, str):
        writing_reading_text = (
            content_html.find(name='header', id='hdWrap')
            .find(name='div', id='mainTitle')
            .find(name='h1', class_='grid02 grid1 left')
        ).text
        writing, reading = writing_reading_text.split('（読み）')
        return writing, reading

    @staticmethod
    def _parse_article_list(content_html: bs4.element.Tag) -> List[bs4.element.Tag]:
        article_list = (
            content_html.find(name='div', class_='grid022leftwrap')
            .find(name='div', id='mainArea')
            .find_all(name='article')
        )
        return article_list

    @staticmethod
    def _get_dictionary_name(article_html: bs4.element.Tag) -> str:
        dictionary_name = (
            article_html.find(name='h2')
        ).text.replace('の解説', '')
        return dictionary_name

    @staticmethod
    def _get_ex_cf_list(article_html: bs4.element.Tag) -> List[bs4.element.Tag]:
        ex_cf_list = article_html.find_all(name='div', class_='ex cf')
        return ex_cf_list

    @staticmethod
    def _get_specific_reading_and_writing_list(ex_cf_list: List[bs4.element.Tag]) -> List[(str, str)]:
        result = []
        specific_reading_and_writing_html_list = [ex_cf.find(name='h3') for ex_cf in ex_cf_list]
        specific_reading_and_writing_text_list = [
            html.text if html is not None else None \
                for html in specific_reading_and_writing_html_list
        ]
        for specific_reading_and_writing_text in specific_reading_and_writing_text_list:
            if specific_reading_and_writing_text is not None:
                specific_reading, specific_writing = (
                    specific_reading_and_writing_text
                    .replace('】', '').replace('‐', '')
                    .split('【')
                )
            else:
                specific_reading, specific_writing = None, None
            result.append((specific_reading, specific_writing))
        return result

    @staticmethod
    def _get_description_list(ex_cf_list: List[bs4.element.Tag]) -> List[bs4.element.Tag]:
        description_list = [ex_cf.find(name='section', class_='description') for ex_cf in ex_cf_list]
        return description_list

    @classmethod
    def from_soup(cls, soup: BeautifulSoup) -> KotobankContent:
        dict_handler = KotobankDictionaryHandler()
        content_html = cls._parse_content_html(soup=soup)
        main_writing, main_reading = cls._parse_main_writing_and_reading(content_html=content_html)
        article_list = cls._parse_article_list(content_html=content_html)
        for i, article in enumerate(article_list):
            dictionary_name = cls._get_dictionary_name(article_html=article)
            ex_cf_list = cls._get_ex_cf_list(article_html=article)
            specific_reading_and_writing_list = cls._get_specific_reading_and_writing_list(ex_cf_list=ex_cf_list)
            description_list = cls._get_description_list(ex_cf_list=ex_cf_list)
            for [specific_reading, specific_writing], description in zip(specific_reading_and_writing_list, description_list):
                logger.blue(f'specific_reading: {specific_reading}, specific_writing: {specific_writing}')
                dict_handler.add_from_description(
                    dict_name=dictionary_name,
                    specific_writing=specific_writing, specific_reading=specific_reading,
                    description_html=description
                )

                # TODO: KotobankContent only comes in when I start parsing the definition_dict.
                #       Need to move all of these static methods to a different class.

                # if dictionary_name == 'デジタル大辞泉':
                #     definition_dict = parse_digital_daijisen(description_html=description)
                #     for def_num, def_text in definition_dict.items():
                #         logger.blue(f'{def_num}: {def_text}')
                # elif dictionary_name == '大辞林 第三版':
                #     definition_dict = parse_daijirin_daisanpan(description_html=description)
                #     for def_num, def_text in definition_dict.items():
                #         logger.blue(f'{def_num}: {def_text}')
                # elif dictionary_name == '精選版 日本国語大辞典':
                #     root_definition_dict = parse_seisenpan_nihonkokugodaijisho(description_html=description)
                #     for usage_number, definition_dict in root_definition_dict.items():
                #         logger.blue(f"{usage_number}: {definition_dict['usage_text']}")
                #         for def_number, def_dict in definition_dict.items():
                #             logger.blue(f"\t{def_number}: ({def_dict['usage']}) {def_dict['definition_text']}")
                #             for example in def_dict['examples']:
                #                 logger.blue(f'\t\t{example}')
                # else:
                #     logger.error(f"Unidentified dictionary_name: {dictionary_name}")
                #     raise Exception
        return KotobankContent(
            dict_handler=dict_handler,
            main_writing=main_writing, main_reading=main_reading
        )

# def parse_content_area(soup: BeautifulSoup) -> bs4.element.Tag:
#     content_area = (
#         soup.find(name='body', class_='pageWord winpc')
#         .find(name='div', class_='bodyWrap')
#         .find(name='div', id='contentArea')
#     )
#     return content_area

# def parse_main_writing_and_reading(content_area: bs4.element.Tag) -> (str, str):
#     writing_reading_text = (
#         content_area.find(name='header', id='hdWrap')
#         .find(name='div', id='mainTitle')
#         .find(name='h1', class_='grid02 grid1 left')
#     ).text
#     writing, reading = writing_reading_text.split('（読み）')
#     return writing, reading

# def parse_article_list(content_area: bs4.element.Tag) -> List[bs4.element.Tag]:
#     article_list = (
#         content_area.find(name='div', class_='grid022leftwrap')
#         .find(name='div', id='mainArea')
#         .find_all(name='article')
#     )
#     return article_list

def parse_digital_daijisen(description_html: bs4.element.Tag) -> dict:
    def_numbers = [int(number.text) for number in description_html.find_all(name='b')]
    definition_dict = {}
    if len(def_numbers) > 0:
        children = list(description_html.children)
        current_def_number = None
        for j, child in enumerate(children):
            if '<b>' in str(child) and '</b>' in str(child):
                current_def_number = int(child.text)
                definition_dict[current_def_number] = ''
            else:
                if current_def_number is not None:
                    definition_dict[current_def_number] += str(child)
        for key in definition_dict:
            definition_dict[key] = (
                BeautifulSoup(definition_dict[key], 'html.parser').text
                .replace(' ', '')
                .replace('\n', '')
            )
    else:
        description_text = description_html.text.replace(' ', '').replace('\n', '')
        definition_dict[1] = description_text
    return definition_dict

def parse_daijirin_daisanpan(description_html: bs4.element.Tag) -> dict:
    definition_part_list = (
        description_html.find(name='div', class_='NetDicBody')
        .find_all(name='div', style='text-indent:0;')
    )
    definition_dict = {}
    if len(definition_part_list) > 0:
        for definition_part in definition_part_list:
            definition_part = definition_part.find(name='div', style='margin-left:1.2em;text-indent:-1.2em;')
            definition_number = definition_part.find(name='span', style='display:inline-block;width:1.2em;text-indent:0;').text.replace(' ', '')
            definition_number = circle_number_char2int[definition_number]
            definition_text = definition_part.find(name='span', style='text-indent:0;').text.replace(' ', '')
            definition_dict[definition_number] = definition_text
    else:
        description_text = description_html.text.replace(' ', '').replace('\n', '')
        definition_dict[1] = description_text
    return definition_dict


def split_at_brackets(text: str, left_bracket: str, right_bracket: str) -> (str, str, str):
    check_list_length(left_bracket, correct_length=1, ineq_type='eq')
    check_list_length(right_bracket, correct_length=1, ineq_type='eq')
    left_index = text.index(left_bracket)
    right_index = text.index(right_bracket)
    left_text = text[:left_index]
    right_text = text[right_index+1:]
    contents = text[left_index+1:right_index]
    return left_text, contents, right_text

def parse_seisenpan_nihonkokugodaijisho(description_html: bs4.element.Tag) -> dict:
    """
    {
        usage_number: {
            'usage_text': usage_text,
            'definitions': {
                definition_number: {
                    'definition_text': definition_text,
                    'examples': [example0, example1, ...]
                }
            }
        }
    }
    TODO: I think I might just have to turn this into a class.
          It's hard to keep track of what's going on otherwise.
    """
    children = [child for child in list(description_html.children) if type(child) is bs4.element.Tag]
    root_definition_dict = {}
    definition_dict = {}
    current_usage_number = None
    current_usage = None
    current_def_number = None
    for j, child in enumerate(children):
        if child.attrs['data-orgtag'] == 'meaning':
            if child.text[0] == '[':
                _, current_usage_number_str, remaining_text = split_at_brackets(
                    text=child.text, left_bracket='[', right_bracket=']'
                )
                previous_usage_number = current_usage_number
                current_usage_number = int(current_usage_number_str)
                if current_usage_number <= previous_usage_number:
                    root_definition_dict[previous_usage_number]['definitions'].append(definition_dict)
                    definition_dict = {}
                    current_def_number = None
                remaining_text = remaining_text.replace(' ', '')
                if remaining_text[0] == '〘':
                    _, current_usage, remaining_text = split_at_brackets(
                        text=remaining_text, left_bracket='〘', right_bracket='〙'
                    )
                    if remaining_text != '':
                        current_def_number = 1
                        definition_dict[current_def_number] = {
                            'definition_text': remaining_text,
                            'examples': []
                        }
                        root_definition_dict[current_usage_number] = {
                            'usage_text': current_usage,
                            'definitions': [definition_dict]
                        }
                else:
                    current_def_number = 1
                    definition_dict[current_def_number] = {
                        'definition_text': remaining_text,
                        'examples': []
                    }
                    root_definition_dict[current_usage_number] = {
                        'usage_text': current_usage,
                        'definitions': [definition_dict]
                    }
            elif child.text[0] in circle_number_char2int.keys():
                next_def_number = circle_number_char2int[child.text[0]]
                if current_def_number is not None and current_def_number + 1 != next_def_number:
                    logger.error(f'current_def_number + 1 == {current_def_number + 1} != {next_def_number} == next_def_number')
                    raise Exception
                current_def_number = next_def_number
                definition_dict[current_def_number] = {
                    'definition_text': child.text[1:],
                    'examples': []
                }
            elif child.text[0] == '〘':
                _, current_usage, remaining_text = split_at_brackets(
                    text=child.text, left_bracket='〘', right_bracket='〙'
                )
                if remaining_text != '':
                    current_def_number = 1
                    definition_dict[current_def_number] = {
                        'definition_text': remaining_text,
                        'examples': []
                    }
            else:
                logger.red(f"child.text: {child.text}")
                raise NotImplementedError
        elif child.attrs['data-orgtag'] == 'example':
            definition_dict[current_def_number]['examples'].append(child.text[1:])
        else:
            logger.error(f"Invalid child.attrs['data-orgtag']={child.attrs['data-orgtag']}")
            raise Exception
    if len(definition_dict) > 0:
        current_usage_number = current_usage_number + 1 if current_usage_number is not None else 1
        root_definition_dict[current_usage_number] = definition_dict

        # if child.attrs['data-orgtag'] == 'meaning':
        #     logger.purple(f'child.text[0]: {child.text[0]}')
        #     if child.text[0] not in circle_number_char2int.keys():
        #         if '〘' in child.text and '〙' in child.text:
        #             logger.purple(f'Found usage')
        #             current_usage = child.text[:child.text.index('〙')+1].replace(' ', '')
        #             # TODO: Need to parse usage number
        #             possible_definition = child.text[child.text.index('〙')+1:].replace(' ', '')
        #             if possible_definition != '':
        #                 logger.purple(f'Found non-empty definition -> new dictionary')
        #                 current_def_number = 1
        #                 definition_dict[current_def_number] = {
        #                     'usage': current_usage,
        #                     'definition_text': possible_definition,
        #                     'examples': []
        #                 }
        #         else:
        #             logger.purple(f'Found irregular -> new dictionary')
        #             current_usage = ''
        #             current_def_number = 1
        #             definition_dict[current_def_number] = {
        #                 'usage': current_usage,
        #                 'definition_text': child.text,
        #                 'examples': []
        #             }
        #     else:
        #         logger.purple(f"Round number - append to dictionary")
        #         current_def_number = circle_number_char2int[child.text[0]]
        #         definition_dict[current_def_number] = {
        #             'usage': current_usage,
        #             'definition_text': child.text[1:],
        #             'examples': []
        #         }
        # elif child.attrs['data-orgtag'] == 'example':
        #     definition_dict[current_def_number]['examples'].append(child.text[1:])
        # else:
        #     logger.error(f"Invalid child.attrs['data-orgtag']={child.attrs['data-orgtag']}")
        #     raise Exception
    return root_definition_dict