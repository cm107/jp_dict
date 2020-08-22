from __future__ import annotations
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from typing import List
from logger import logger
from common_utils.base.basic import BasicLoadableObject

from src.refactored.common import Link, LinkList

dictionary_title_text_list = []

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

    @classmethod
    def from_search_word(cls, search_word: str) -> KotobankWordHtmlParser:
        search_url = f'https://kotobank.jp/word/{search_word}'
        return KotobankWordHtmlParser(url=search_url)

    def parse(self):
        content_area_html = self._soup.find(name='div', attrs={'id': 'contentArea'})
        has_content_area_html = content_area_html is not None
        assert has_content_area_html, 'No content_area_html found.'
        no_page_found_html = content_area_html.find(name='h3', attrs={'class': 'lead'})
        if no_page_found_html is not None:
            print('No Page Found')
            return

        main_title = self.parse_main_title(content_area_html)
        logger.purple(f'main_title: {main_title}')
        main_alias_name = self.parse_main_alias_name(content_area_html)
        self.parse_main_area(content_area_html)

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

    def parse_main_area(self, content_area_html: Tag):
        main_area_html = content_area_html.find(name='div', attrs={'id': 'mainArea'})
        has_main_area = main_area_html is not None
        assert has_main_area
        article_html_list = main_area_html.find_all(name='article')
        assert len(article_html_list) > 0
        for article_html in article_html_list:
            dictionary_title_html = article_html.find(name='h2')
            dictionary_title_text = dictionary_title_html.text.strip()
            logger.cyan(f'dictionary_title_text: {dictionary_title_text}')
            ex_cf_html_list = article_html.find_all(name='div', attrs={'class': 'ex cf'})
            logger.blue(len(ex_cf_html_list))
            self.parse_dictionary(
                dictionary_title_text=dictionary_title_text,
                ex_cf_html_list=ex_cf_html_list,
                strict=False
            )
    
    def parse_digital_daijisen(self, ex_cf_html_list: List[Tag]):
        from common_utils.path_utils import get_rootname_from_path
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
        # gaiji2numeral_dict = {
        #     '/image/dictionary/daijisen/gaiji/02539.gif': '一',
        #     '/image/dictionary/daijisen/gaiji/02540.gif': '二',
        #     '/image/dictionary/daijisen/gaiji/02541.gif': '三',
        #     '/image/dictionary/daijisen/gaiji/02542.gif': '四'
        # }

        for ex_cf_html in ex_cf_html_list:
            description_html = ex_cf_html.find(name='section', attrs={'class': 'description'})
            has_description = description_html is not None
            assert has_description, 'No description found.'
            for child in description_html.children:
                # logger.yellow(f'type(child): {type(child)}')
                # logger.white(f'child: {child}')
                if type(child) is NavigableString:
                    logger.green('Text')
                    text = str(child)
                    logger.blue(f'\ttext: {text}')
                elif type(child) is Tag:
                    # logger.white(f'child.text.strip(): {child.text.strip()}')
                    # logger.white(f'child.attrs: {child.attrs}')
                    if 'class' in child.attrs and child.attrs['class'] == ['gaiji']:
                        logger.green('Gaiji')
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
                                Please check the HTML source at:
                                    {self.url}
                                    {self.title}
                                """
                            )
                        assert gaiji_int_equivalent in gaiji_map, f'{gaiji_int_equivalent} not in gaiji_map.\nurl: {self.url}\ntitle: {self.title}'
                        gaiji_str_equivalent = gaiji_map[gaiji_int_equivalent]
                        logger.blue(f'\tgaiji_str_equivalent: {gaiji_str_equivalent}')
                        logger.blue(f'\tgaiji_type: {gaiji_type}')
                    elif 'class' in child.attrs and child.attrs['class'] == ['hinshi']:
                        logger.green('Hinshi')
                        hinshi_text = child.text.strip()
                        logger.blue(f'\thinshi_text: {hinshi_text}')
                    elif len(child.attrs) == 0 and child.text.strip() == '':
                        logger.green('Ignore 1')
                        pass # Ignore. Usually just a <br> or <br/>
                    elif len(child.attrs) == 0 and str.isdigit(child.text.strip()):
                        logger.green('Definition Number')
                        definition_number = int(child.text.strip())
                        logger.blue(f'\tdefinition_number: {definition_number}')
                    elif 'org' in child.attrs and child.attrs['org'] == '―':
                        logger.green('Origin Word')
                        origin_word_text = child.text.strip()
                        logger.blue(f'\torigin_word_text: {origin_word_text}')
                    elif 'href' in child.attrs and child.name == 'a':
                        logger.green('Related Word Link')
                        related_word_url = f"https://kotobank.jp{child['href']}"
                        related_word_text = child.text.strip()
                        related_word_link = Link(url=related_word_url, text=related_word_text)
                        logger.blue(f'\trelated_word_link: {related_word_link}')
                    elif len(child.attrs) == 0 and child.name == 'b' and len(child.text.strip()) > 0:
                        logger.green('Bold Text')
                        bold_text = child.text.strip()
                        logger.blue(f'\tbold_text: {bold_text}')
                    elif child.name == 'span' and 'class' in child.attrs and child['class'] == ['kigo']:
                        logger.green('Kigo Word')
                        kigo_text = child.text.strip()
                        logger.blue(f'\tkigo_text: {kigo_text}')
                    elif 'class' in child.attrs and child['class'] == ['media'] and child.name == 'div':
                        logger.green('Media')
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
                        logger.blue(f'\tfullsize_img_link: {fullsize_img_link}')
                        logger.blue(f'\tsmallsize_img_link: {smallsize_img_link}')
                    elif child.name == 'br' and 'clear' in child.attrs and child.attrs['clear'] == 'all':
                        logger.green(f'Ignore 2')
                        pass # Ignore. Appears to come after a media tag.
                    elif child.name == 'span' and 'type' in child.attrs and child.attrs['type'] == '原綴':
                        logger.green('元綴')
                        mototsudzuri_text = child.text.strip()
                        logger.blue(f'\tmototsudzuri_text: {mototsudzuri_text}')
                    elif child.name == 'br' and len(child.attrs) == 0 and len(child.text.strip()) > 0 and len(child.find_all(name='a', href=True)) > 0:
                        logger.green('Related Word Link List')
                        related_word_html_list = child.find_all(name='a', href=True)
                        related_word_link_list = LinkList()
                        for related_word_html in related_word_html_list:
                            related_word_url = f"https://kotobank.jp{related_word_html['href']}"
                            related_word_text = related_word_html.text.strip()
                            related_word_link = Link(url=related_word_url, text=related_word_text)
                            related_word_link_list.append(related_word_link)
                        logger.blue(f'\trelated_word_link_list: {related_word_link_list}')
                    elif child.name == 'sup' and len(child.attrs) == 0 and len(child.text.strip()) > 0:
                        logger.green(f'Superscript')
                        superscript_text = child.text.strip()
                        logger.blue(f'\tsuperscript_text: {superscript_text}')
                    elif child.name == 'br' and len(child.attrs) == 0 and child.find(name='table') is not None:
                        logger.green(f'Table')
                        table_html = child.find(name='table')
                        import pandas as pd
                        table_dfs = pd.read_html(str(child))
                        table_dicts = [table_df.to_dict() for table_df in table_dfs]
                        logger.blue(f'\ttable_dicts: {table_dicts}')
                    elif child.name == 'span' and 'type' in child.attrs and child.attrs['type'] == '歴史':
                        logger.green('歴史')
                        rekishi_text = child.text.strip()
                        logger.blue(f'\trekishi_text: {rekishi_text}')
                    elif child.name == 'i' and len(child.attrs) == 0 and len(child.text.strip()) > 0:
                        logger.green('Italic Text')
                        italic_text = child.text.strip()
                        logger.blue(f'\titalic_text: {italic_text}')
                    else:
                        logger.red(f'TODO')
                        logger.red(f'\tchild.text.strip(): {child.text.strip()}')
                        logger.red(f'\tchild.name: {child.name}')
                        logger.red(f'\tchild.attrs: {child.attrs}')
                        logger.red(child)
                        logger.red(f'\tself.url: {self.url}')
                        logger.red(f'\tself.title: {self.title}')
                        raise Exception
                else:
                    raise Exception(f'Unknown type(child): {type(child)}')
            # import sys
            # sys.exit()

    def parse_dictionary(self, dictionary_title_text: str, ex_cf_html_list: List[Tag], strict: bool=True):
        if dictionary_title_text == 'デジタル大辞泉の解説':
            self.parse_digital_daijisen(ex_cf_html_list)
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '大辞林 第三版の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '精選版 日本国語大辞典の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == 'ブリタニカ国際大百科事典 小項目事典の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '日本大百科全書(ニッポニカ)の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '百科事典マイペディアの解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典 第２版の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == 'デジタル大辞泉プラスの解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == 'ナビゲート ビジネス基本用語集の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の夢遊病の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の賃金の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '動植物名よみかた辞典　普及版の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == 'デジタル版 日本人名大辞典+Plusの解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '朝日日本歴史人物事典の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の微妙の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の投網の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の異端審問の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の寝室の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '防府市歴史用語集の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の経典の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の相方の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の声帯模写の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の消火の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内のpassageの言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == 'リフォーム用語集の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内のお盆の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '栄養・生化学辞典の解説':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の授乳の言及':
            if strict:
                raise NotImplementedError
        elif dictionary_title_text == '世界大百科事典内の共謀の言及':
            if strict:
                raise NotImplementedError
        else:
            logger.error(f'Unknown dictionary_title_text: {dictionary_title_text}')
            if strict:
                raise Exception

from common_utils.file_utils import file_exists
from src.refactored.jisho_matches import SearchWordMatchesHandler
import json

if not file_exists('iter_save.json'):
    iter_dict = {'iter': 0}
else:
    iter_dict = json.load(open('iter_save.json', 'r'))

search_word_matches_handler = SearchWordMatchesHandler.load_from_path('analyze_parse_dump/sw_matches_dump.json')
for i, search_word_matches in enumerate(search_word_matches_handler):
    if i < iter_dict['iter']:
        continue
    logger.yellow(f'search_word_matches.search_word: {search_word_matches.search_word}')
    parser = KotobankWordHtmlParser.from_search_word(search_word_matches.search_word)
    parser.parse()
    iter_dict['iter'] = i
    json.dump(iter_dict, open('iter_save.json', 'w'))

# # parser = KotobankWordHtmlParser.from_search_word('余り')
# # parser = KotobankWordHtmlParser.from_search_word('passage')
# # parser = KotobankWordHtmlParser.from_search_word('隼')
# # parser = KotobankWordHtmlParser.from_search_word('王妃')
# # parser = KotobankWordHtmlParser.from_search_word('豊臣')
# # parser = KotobankWordHtmlParser.from_search_word('センチ')
# # parser = KotobankWordHtmlParser.from_search_word('奇特')
# # parser = KotobankWordHtmlParser.from_search_word('作法')
# parser = KotobankWordHtmlParser.from_search_word('展開')
# parser.parse()