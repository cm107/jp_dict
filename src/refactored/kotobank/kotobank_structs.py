from __future__ import annotations
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Dict
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler
from common_utils.path_utils import get_all_files_of_extension
from common_utils.file_utils import dir_exists
from typing import Any
from collections import OrderedDict

from .digital_daijisen import parse as parse_digital_daijisen, ParsedItemListHandler as DigitalDaijisenDataHandler
from .seisenpan import parse as parse_seisenpan, ParsedArticleList as SeisenpanDataHandler

class DictionaryContent(BasicLoadableObject['DictionaryContent']):
    def __init__(self, dictionary_name: str, content: Any=None):
        assert hasattr(content, 'to_dict') or hasattr(content, 'to_dict_list') or content is None
        assert hasattr(content, 'from_dict') or hasattr(content, 'from_dict_list') or content is None
        self.dictionary_name = dictionary_name
        self.content = content
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> DictionaryContent:
        dictionary_name = item_dict['dictionary_name']
        if item_dict['content'] is not None:
            if dictionary_name == 'デジタル大辞泉の解説':
                content = DigitalDaijisenDataHandler.from_dict_list(item_dict['content'])
            elif dictionary_name == '精選版 日本国語大辞典の解説':
                content = SeisenpanDataHandler.from_dict_list(item_dict['content'])
            else:
                raise Exception(f"Found non-None content for {dictionary_name}, but DictionaryContent.from_dict doesn't account for {dictionary_name}.")
        else:
            content = None
        return DictionaryContent(
            dictionary_name=dictionary_name,
            content=content
        )

class DictionaryContentList(
    BasicLoadableHandler['DictionaryContentList', 'DictionaryContent'],
    BasicHandler['DictionaryContentList', 'DictionaryContent']
):
    def __init__(self, content_list: List[DictionaryContent]=None):
        super().__init__(obj_type=DictionaryContent, obj_list=content_list)
        self.content_list = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> DictionaryContentList:
        return DictionaryContentList([DictionaryContent.from_dict(item_dict) for item_dict in dict_list])
    
    @property
    def dictionary_names(self) -> List[str]:
        names = []
        for content in self:
            if content.dictionary_name not in names:
                names.append(content.dictionary_name)
        return names

class MainTitle(BasicLoadableObject['MainTitle']):
    def __init__(self, writing: str, reading: str=None):
        super().__init__()
        assert writing is not None, 'MainTitle writing cannot be None.'
        self.writing = writing
        self.reading = reading
    
    def __str__(self) -> str:
        if self.reading is not None:
            return f'{self.writing} ({self.reading})'
        else:
            return f'{self.writing}'

class MainAliasName(BasicLoadableObject['MainAliasName']):
    def __init__(self, text_list: List[str]):
        super().__init__()
        self.text_list = text_list

class MainArea(BasicLoadableObject['MainArea']):
    def __init__(self, articles: DictionaryContentList=None):
        self.articles = articles if articles is not None else DictionaryContentList()
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> MainArea:
        return MainArea(articles=DictionaryContentList.from_dict_list(item_dict['articles']))

class KotobankResult(BasicLoadableObject['KotobankResult']):
    def __init__(self, search_word: str, main_title: MainTitle=None, main_alias_name: MainAliasName=None, main_area: MainArea=None):
        super().__init__()
        self.search_word = search_word
        self.main_title = main_title
        self.main_alias_name = main_alias_name
        self.main_area = main_area
    
    def to_dict(self) -> dict:
        result = {'search_word': self.search_word}
        if self.main_title is not None:
            result['main_title'] = self.main_title.to_dict()
        if self.main_alias_name is not None:
            result['main_alias_name'] = self.main_alias_name.to_dict()
        if self.main_area is not None:
            result['main_area'] = self.main_area.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> KotobankResult:
        return KotobankResult(
            search_word=item_dict['search_word'],
            main_title=MainTitle(item_dict['main_title']) if 'main_title' in item_dict else None,
            main_alias_name=MainAliasName.from_dict(item_dict['main_alias_name']) if 'main_alias_name' in item_dict else None,
            main_area=MainArea.from_dict(item_dict['main_area']) if 'main_area' in item_dict else None
        )
    
    @property
    def dictionary_names(self) -> List[str]:
        if self.main_area is not None:
            return self.main_area.articles.dictionary_names
        else:
            return []

class KotobankResultList(
    BasicLoadableHandler['KotobankResultList', 'KotobankResult'],
    BasicHandler['KotobankResultList', 'KotobankResult']
):
    def __init__(self, results: List[KotobankResult]=None):
        super().__init__(obj_type=KotobankResult, obj_list=results)
        self.results = self.obj_list

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> KotobankResultList:
        return KotobankResultList([KotobankResult.from_dict(item_dict) for item_dict in dict_list])

    @classmethod
    def load_from_dir(cls, dir_path: str) -> KotobankResultList:
        assert dir_exists(dir_path), f'Directory not found: {dir_path}'
        json_paths = get_all_files_of_extension(dir_path, extension='json')
        results = KotobankResultList()
        for json_path in json_paths:
            result = KotobankResult.load_from_path(json_path)
            results.append(result)
        return results

    def get_dictionary_count(self, exclude_results_containing: List[str]=None) -> OrderedDict:
        count_dict = {}
        for result in self:
            dictionary_names = result.dictionary_names
            skip = False
            if exclude_results_containing is not None:
                for excluded_name in exclude_results_containing:
                    if excluded_name in dictionary_names:
                        skip = True
                        break
            if skip:
                continue

            for dictionary_name in dictionary_names:
                if dictionary_name in count_dict:
                    count_dict[dictionary_name] = count_dict[dictionary_name] + 1
                else:
                    count_dict[dictionary_name] = 1
        ordered_count_dict = OrderedDict(sorted(count_dict.items(), key=lambda x: x[1], reverse=True))
        return ordered_count_dict

    def get_dictionary_results(self, exclude_results_containing: List[str]=None) -> OrderedDict:
        count_dict = {}
        for result in self:
            dictionary_names = result.dictionary_names
            skip = False
            if exclude_results_containing is not None:
                for excluded_name in exclude_results_containing:
                    if excluded_name in dictionary_names:
                        skip = True
                        break
            if skip or result.main_area is None:
                continue

            # for dictionary_name in dictionary_names:
            #     if dictionary_name in count_dict:
            #         count_dict[dictionary_name] = count_dict[dictionary_name] + 1
            #     else:
            #         count_dict[dictionary_name] = 1
            for article in result.main_area.articles:
                if article.dictionary_name in count_dict:
                    count_dict[article.dictionary_name].append(result.search_word)
                else:
                    count_dict[article.dictionary_name] = [result.search_word]
        ordered_count_dict = OrderedDict(sorted(count_dict.items(), key=lambda x: len(x[1]), reverse=True))
        return ordered_count_dict

    def get_dictionary_priority_dict(self) -> OrderedDict:
        priority_dict = OrderedDict()
        excluded_dict_list = []
        orig_dictionary_results = self.get_dictionary_results()
        working_dictionary_results = orig_dictionary_results.copy()
        while True:
            top_priority_name, top_priority_words = working_dictionary_results.popitem(last=False)
            priority_dict[top_priority_name] = {
                'added_words': top_priority_words,
                'num_added_words': len(top_priority_words),
                'orig_num_dict_words': len(orig_dictionary_results[top_priority_name]),
                'total_proportion': round(len(orig_dictionary_results[top_priority_name]) / len(self), 4)
            }
            excluded_dict_list.append(top_priority_name)
            working_dictionary_results = self.get_dictionary_results(exclude_results_containing=excluded_dict_list)
            if len(working_dictionary_results) == 0:
                break
        return priority_dict

class KotobankWordHtmlParser:
    def __init__(self, url: str):
        assert url.startswith('https://kotobank.jp/word/')
        self._url = url
        self._http = urllib3.PoolManager()
        page = self._http.request(method='GET', url=url)
        self._soup = BeautifulSoup(page.data, 'html.parser')

    @property
    def url(self) -> str:
        return self._url
    
    @property
    def title(self) -> str:
        return self._soup.title.text.strip()

    @property
    def search_word(self) -> str:
        import urllib
        encoded_search_word = self.url.replace('https://kotobank.jp/word/', '')
        decoded_search_word = urllib.parse.unquote(encoded_search_word)
        return decoded_search_word

    @classmethod
    def from_search_word(cls, search_word: str) -> KotobankWordHtmlParser:
        search_url = f'https://kotobank.jp/word/{search_word}'
        return KotobankWordHtmlParser(url=search_url)

    def parse(self) -> KotobankResult:
        content_area_html = self._soup.find(name='div', attrs={'id': 'contentArea'})
        has_content_area_html = content_area_html is not None
        assert has_content_area_html, 'No content_area_html found.'
        no_page_found_html = content_area_html.find(name='h3', attrs={'class': 'lead'})
        if no_page_found_html is not None:
            return KotobankResult(search_word=self.search_word)

        main_title = self.parse_main_title(content_area_html)
        main_alias_name = self.parse_main_alias_name(content_area_html)
        main_area = self.parse_main_area(content_area_html)

        return KotobankResult(
            search_word=self.search_word,
            main_title=main_title,
            main_alias_name=main_alias_name,
            main_area=main_area
        )

    def parse_main_title(self, content_area_html: Tag) -> MainTitle:
        main_title_html = content_area_html.find(name='div', attrs={'id': 'mainTitle'})
        main_title_text = main_title_html.text.strip()
        main_title_reading_html = main_title_html.find(name='span')
        has_main_title_reading = main_title_reading_html is not None
        if has_main_title_reading:
            main_title_reading_text = main_title_reading_html.text.strip()
            main_title_writing_text = main_title_text.replace(main_title_reading_text, '')
            main_title_reading_text = main_title_reading_text.replace('（読み）', '')
        else:
            main_title_reading_text = None
            main_title_writing_text = main_title_text
        main_title = MainTitle(
            writing=main_title_writing_text,
            reading=main_title_reading_text
        )
        return main_title
    
    def parse_main_alias_name(self, content_area_html: Tag) -> MainAliasName:
        main_alias_name_html = content_area_html.find(name='div', attrs={'id': 'mainAliasName'})
        has_main_alias_name = main_alias_name_html is not None
        if has_main_alias_name:
            main_alias_item_html_list = main_alias_name_html.find_all(name='li')
            text_list = []
            for main_alias_item_html in main_alias_item_html_list:
                main_alias_item_text = main_alias_item_html.text.strip()
                text_list.append(main_alias_item_text)
            main_alias_name = MainAliasName(text_list=text_list)
            return main_alias_name
        else:
            return None

    def parse_main_area(self, content_area_html: Tag) -> MainArea:
        main_area_html = content_area_html.find(name='div', attrs={'id': 'mainArea'})
        has_main_area = main_area_html is not None
        assert has_main_area
        article_html_list = main_area_html.find_all(name='article')
        assert len(article_html_list) > 0
        dictionary_content_list = DictionaryContentList()
        for article_html in article_html_list:
            dictionary_title_html = article_html.find(name='h2')
            dictionary_title_text = dictionary_title_html.text.strip()
            ex_cf_html_list = article_html.find_all(name='div', attrs={'class': 'ex cf'})
            dictionary_content = self.parse_dictionary(
                dictionary_title_text=dictionary_title_text,
                ex_cf_html_list=ex_cf_html_list,
                strict=False
            )
            dictionary_content_list.append(dictionary_content)
        main_area = MainArea(articles=dictionary_content_list)
        return main_area

    def parse_dictionary(self, dictionary_title_text: str, ex_cf_html_list: List[Tag], strict: bool=True) -> DictionaryContent:
        if dictionary_title_text == 'デジタル大辞泉の解説':
            digital_daijisen_data_handler = parse_digital_daijisen(ex_cf_html_list)
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=digital_daijisen_data_handler
            )
        elif dictionary_title_text == '大辞林 第三版の解説': # TODO 2
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '精選版 日本国語大辞典の解説': # TODO 1
            seisenpan_data_handler = parse_seisenpan(ex_cf_html_list)
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=seisenpan_data_handler
            )
        elif dictionary_title_text == 'ブリタニカ国際大百科事典 小項目事典の解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '日本大百科全書(ニッポニカ)の解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '百科事典マイペディアの解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典 第２版の解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == 'デジタル大辞泉プラスの解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == 'ナビゲート ビジネス基本用語集の解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の夢遊病の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の賃金の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '動植物名よみかた辞典　普及版の解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == 'デジタル版 日本人名大辞典+Plusの解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '朝日日本歴史人物事典の解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の微妙の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の投網の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の異端審問の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の寝室の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '防府市歴史用語集の解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の経典の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の相方の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の声帯模写の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の消火の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内のpassageの言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == 'リフォーム用語集の解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内のお盆の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '栄養・生化学辞典の解説':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の授乳の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        elif dictionary_title_text == '世界大百科事典内の共謀の言及':
            if strict:
                raise NotImplementedError
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )
        else:
            if strict:
                raise Exception(f'Unknown dictionary_title_text: {dictionary_title_text}')
            return DictionaryContent(
                dictionary_name=dictionary_title_text,
                content=None
            )