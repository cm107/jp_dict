import pickle
import requests
from bs4 import BeautifulSoup
import bs4
from src.util.char_lists import circle_number_char2int
from logger import logger
# from src.lib.kotobank.dictionary_parsers import parse_content_area, \
#     parse_main_writing_and_reading, parse_article_list, \
#     parse_digital_daijisen, parse_daijirin_daisanpan, \
#     parse_seisenpan_nihonkokugodaijisho
from src.lib.kotobank.dictionary_parsers import KotobankContent

def get_soup(url: str) -> (int, BeautifulSoup):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html5lib') if response.status_code == 200 else None
    return response.status_code, soup

base_search_url = "https://kotobank.jp/word/"
search_word_list = ['類語', '道聴塗説', '日数', '次第']

for search_word in search_word_list:
    logger.yellow(f"============search_word: {search_word}============")
    search_url = f"{base_search_url}{search_word}"
    logger.white(f'search_url: {search_url}')
    response = requests.get(search_url)
    status_code, soup = get_soup(url=search_url)

    if status_code == 200:
        content = KotobankContent.from_soup(soup)

        # content_area = parse_content_area(soup=soup)
        # main_writing, main_reading = parse_main_writing_and_reading(content_area=content_area)
        # article_list = parse_article_list(content_area=content_area)
        # logger.white(f'main_writing: {main_writing}, main_reading: {main_reading}')
        # for i, article in enumerate(article_list):
        #     dictionary_name = (
        #         article.find(name='h2')
        #     ).text.replace('の解説', '')
        #     logger.cyan(f'dictionary_name: {dictionary_name}')
        #     ex_cf_list = article.find_all(name='div', class_='ex cf')
        #     specific_reading_and_writing_list = [ex_cf.find(name='h3').text for ex_cf in ex_cf_list]
        #     description_list = [ex_cf.find(name='section', class_='description') for ex_cf in ex_cf_list]
        #     for description, specific_reading_and_writing in zip(description_list, specific_reading_and_writing_list):
        #         specific_reading, specific_writing = (
        #             specific_reading_and_writing
        #             .replace('】', '').replace('‐', '')
        #             .split('【')
        #         )
        #         logger.blue(f'specific_reading: {specific_reading}, specific_writing: {specific_writing}')
        #         if dictionary_name == 'デジタル大辞泉':
        #             definition_dict = parse_digital_daijisen(description_html=description)
        #             for def_num, def_text in definition_dict.items():
        #                 logger.blue(f'{def_num}: {def_text}')
        #         elif dictionary_name == '大辞林 第三版':
        #             definition_dict = parse_daijirin_daisanpan(description_html=description)
        #             for def_num, def_text in definition_dict.items():
        #                 logger.blue(f'{def_num}: {def_text}')
        #         elif dictionary_name == '精選版 日本国語大辞典':
        #             root_definition_dict = parse_seisenpan_nihonkokugodaijisho(description_html=description)
        #             for usage_number, definition_dict in root_definition_dict.items():
        #                 logger.blue(f"{usage_number}: {definition_dict['usage_text']}")
        #                 for def_number, def_dict in definition_dict.items():
        #                     logger.blue(f"\t{def_number}: ({def_dict['usage']}) {def_dict['definition_text']}")
        #                     for example in def_dict['examples']:
        #                         logger.blue(f'\t\t{example}')
        #         else:
        #             logger.error(f"Unidentified dictionary_name: {dictionary_name}")
        #             raise Exception
    else:
        logger.error(f"Encountered status_code: {status_code}")
        raise Exception