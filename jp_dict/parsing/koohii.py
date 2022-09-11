from __future__ import annotations
from typing import List
import os
from webbot import Browser
from bs4 import BeautifulSoup
from tqdm import tqdm
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, \
    BasicHandler
from ..anki.note_structs import ParsedKanjiFields, ParsedKanjiFieldsList
from ..parsing.combined.kanji_info import WritingKanjiInfoList
from ..anki.connect import AnkiConnect

class KoohiiResult(BasicLoadableObject['KoohiiResult']):
    def __init__(
        self,
        lesson_name: str, frame_num: int,
        kanji: str, reading: str, stroke_count: int,
        keyword: str,
        new_shared_stories: List[str], shared_stories: List[str],
        hit_count: int=0, used_in: List[str]=None,
        earliest_time_usec: int=None, earliest_pos_idx: int=None
    ):
        super().__init__()
        self.lesson_name = lesson_name
        self.frame_num = frame_num
        self.kanji = kanji
        self.reading = reading
        self.stroke_count = stroke_count
        self.keyword = keyword
        self.new_shared_stories = new_shared_stories
        self.shared_stories = shared_stories
        self.hit_count = hit_count
        self.used_in = used_in if used_in is not None else []
        self.earliest_time_usec = earliest_time_usec
        self.earliest_pos_idx = earliest_pos_idx
    
    def __str__(self) -> str:
        print_str = f'{self.lesson_name}, Frame {self.frame_num}'
        print_str += f'\nKanji: {self.kanji} ({self.reading}), Stroke Count: {self.stroke_count}'
        print_str += f'\nKeyword: {self.keyword}'
        print_str += f'\nHit Count: {self.hit_count}'
        print_str += f'\nUsed In: {self.used_in}'
        if len(self.new_shared_stories) > 0:
            print_str += f'\nNew Stories:'
            for i, new_shared_story in enumerate(self.new_shared_stories):
                print_str += f'\n{i+1}. {new_shared_story}'
        if len(self.shared_stories) > 0:
            print_str += f'\nStories:'
            for i, shared_story in enumerate(self.shared_stories):
                print_str += f'\n{i+1}. {shared_story}'
        return print_str
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> KoohiiResult:
        return KoohiiResult(
            lesson_name=item_dict['lesson_name'],
            frame_num=item_dict['frame_num'],
            kanji=item_dict['kanji'],
            reading=item_dict['reading'],
            stroke_count=item_dict['stroke_count'],
            keyword=item_dict['keyword'],
            new_shared_stories=item_dict['new_shared_stories'],
            shared_stories=item_dict['shared_stories'],
            hit_count=item_dict['hit_count'],
            used_in=item_dict['used_in'] if 'used_in' in item_dict else None,
            earliest_time_usec=item_dict['earliest_time_usec'] if 'earliest_time_usec' in item_dict else None,
            earliest_pos_idx=item_dict['earliest_pos_idx'] if 'earliest_pos_idx' in item_dict else None
        )
    
    def to_kanji_fields(self, order_idx: int=None) -> ParsedKanjiFields:
        jisho_word_base_url = 'https://jisho.org/word'
        return ParsedKanjiFields(
            lesson_name=self.lesson_name,
            frame_num=str(self.frame_num),
            kanji=self.kanji,
            reading=self.reading,
            stroke_count=str(self.stroke_count),
            keyword=self.keyword,
            new_shared_stories='<br>'.join(self.new_shared_stories),
            shared_stories='<br>'.join(self.shared_stories),
            hit_count=str(self.hit_count),
            used_in=', '.join(
                [
                    f'<a href="{jisho_word_base_url}/{word}">{word}</a>'
                    for word in self.used_in
                ]
            ),
            order_idx=str(order_idx) if order_idx is not None else "",
            unique_id=f'{self.earliest_time_usec}-{self.earliest_pos_idx}'
        )

class KoohiiResultList(
    BasicLoadableHandler['KoohiiResultList', 'KoohiiResult'],
    BasicHandler['KoohiiResultList', 'KoohiiResult']
):
    def __init__(self, results: List[KoohiiResult]=None):
        super().__init__(obj_type=KoohiiResult, obj_list=results)
        self.results = self.obj_list
    
    def __str__(self) -> str:
        print_str = ''
        for i, result in enumerate(self):
            if i == 0:
                print_str += result.__str__()
            else:
                print_str += f'\n\n{result.__str__()}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> KoohiiResultList:
        return KoohiiResultList([KoohiiResult.from_dict(item_dict) for item_dict in dict_list])

    def filter_out_kanji(self, kanji_list: List[str]) -> KoohiiResultList:
        filtered_results = KoohiiResultList()
        for result in self:
            if result.kanji not in kanji_list:
                filtered_results.append(result)
        return filtered_results
    
    def to_kanji_fields(self) -> ParsedKanjiFieldsList:
        return ParsedKanjiFieldsList([result.to_kanji_fields(order_idx=i) for i, result in enumerate(self)])

    def add_or_update_anki(self, deck_name: str, open_browser: bool=False, anki_connect: AnkiConnect=None):
        if anki_connect is None:
            anki_connect = AnkiConnect()
        if 'parsed_kanji' not in anki_connect.get_model_names():
            anki_connect.create_parsed_kanji_model()
        else:
            anki_connect.update_parsed_kanji_templates_and_styling()
        if deck_name not in anki_connect.get_deck_names():
            anki_connect.create_deck(deck=deck_name)
        anki_connect.add_or_update_parsed_kanji_notes(
            deck_name=deck_name,
            fields_list=self.to_kanji_fields()
        )
        if open_browser:
            anki_connect.gui_card_browse(query=f'deck:{deck_name}')

class KoohiiParser:
    def __init__(self, username: str, password: str, showWindow: bool=False):
        self.web = Browser(showWindow=showWindow)
        self._username = username
        self._password = password

    def login(self):
        self.web.go_to('https://kanji.koohii.com/account')
        self.web.type(self._username, into='Username')
        self.web.type(self._password, into='Password')
        self.web.click('Sign In')
        soup = BeautifulSoup(self.web.get_page_source(), 'html.parser')
        page_title = soup.title.text.strip()
        if page_title == 'Sign In - Kanji Koohii':
            # Still on sign-in page.
            formerrormessage_html = soup.find(name='div', class_='formerrormessage')
            formerrormessage_str = formerrormessage_html.text.strip() if formerrormessage_html is not None else None
            if formerrormessage_str is not None:
                raise Exception(formerrormessage_str)
            else:
                raise Exception('Still on sign-in page. Cause is unknown.')
        elif page_title != 'Kanji Koohii':
            raise Exception(f'Got unexpected page title after sign-in: {page_title}')
    
    def get_search_soup(self, search_kanji: str, login_if_necessary: bool=True) -> BeautifulSoup:
        search_url = f'https://kanji.koohii.com/study/kanji/{search_kanji}'
        self.web.go_to(search_url)
        soup = BeautifulSoup(self.web.get_page_source(), 'html.parser')
        page_title = soup.title.text.strip()
        if page_title == 'Sign In - Kanji Koohii':
            if login_if_necessary:
                self.login()
                soup = self.get_search_soup(search_kanji=search_kanji, login_if_necessary=False)
            else:
                raise Exception('Failed to re-login.')
        elif page_title == 'Oops, please retry in a short moment':
            import time
            time.sleep(1)
            soup = self.get_search_soup(search_kanji=search_kanji, login_if_necessary=login_if_necessary)
        return soup

    def parse(
        self, search_kanji: str, hit_count: int=0, used_in: List[str]=None,
        earliest_time_usec: int=None, earliest_pos_idx: int=None
    ) -> KoohiiResult:
        soup = self.get_search_soup(search_kanji=search_kanji)
        row_html = soup.find(name='div', class_='row')
        h2_html = (
            soup
            .find(name='div', id='main_container')
            .find(name='h2')
        )
        if row_html is None:
            if h2_html is not None and h2_html.text.strip() == 'Sign in':
                raise Exception("Not logged in anymore. Need to log back in.")
            else:
                raise Exception
        if h2_html.text.strip() == 'Search : No results':
            return KoohiiResult(
                lesson_name='',
                frame_num=-1,
                kanji=search_kanji,
                reading='',
                stroke_count=-1,
                keyword='',
                new_shared_stories=[],
                shared_stories=[],
                hit_count=hit_count,
                used_in=used_in if used_in is not None else [],
                earliest_time_usec=earliest_time_usec,
                earliest_pos_idx=earliest_pos_idx
            )


        # lesson_name_html = (
        #     row_html
        #     .find(name='div', class_='col-md-9')
        #     .find(name='div', id='EditStoryComponent')
        #     .find(name='div', style='position:relative;')
        #     .find(name='h2')
        # )
        col_whatever_html = row_html.find(name='div', class_='col-md-9')
        if col_whatever_html is None:
            col_whatever_html = row_html.find(name='div', class_='col-lg-9') # Are they all like this now?
        edit_story_component_html = col_whatever_html.find(name='div', id='EditStoryComponent')
        position_relative_html = edit_story_component_html.find(name='div', style='position:relative;')
        lesson_name_html = position_relative_html.find(name='h2')

        lesson_name = lesson_name_html.text.strip()
        frame_num_html = row_html.find(name='div', title='Frame number', class_='framenum')
        frame_num = frame_num_html.text.strip()
        assert frame_num.isdigit(), f'frame_num: {frame_num} is not a digit'
        frame_num = int(frame_num)
        keyword_html = row_html.find(name='span', class_='JSEditKeyword')
        keyword = keyword_html.text.strip()
        kanji_html = row_html.find(name='div', class_='kanji')
        kanji = kanji_html.text.strip()
        stroke_count_html = row_html.find(name='div', title='Stroke count', class_='strokecount')
        stroke_count_text = stroke_count_html.text.strip().split(']')[0].split('[')[1]
        assert stroke_count_text.isdigit(), f'stroke_count_text: {stroke_count_text} is not a digit'
        stroke_count = int(stroke_count_text)
        reading = stroke_count_html.find(name='span', class_='cj-k').text.strip()

        new_shared_story_html_list = (
            row_html
            .find(name='div', id='sharedstories-new')
            .find_all(name='div', class_='story')
        )
        new_shared_story_text_list = [html.text.strip() for html in new_shared_story_html_list]
        shared_story_html_list = (
            row_html
            .find(name='div', id='SharedStoriesListComponent')
            .find_all(name='div', class_='story')
        )
        shared_story_text_list = [html.text.strip() for html in shared_story_html_list]
        return KoohiiResult(
            lesson_name=lesson_name,
            frame_num=frame_num,
            kanji=kanji,
            reading=reading,
            stroke_count=stroke_count,
            keyword=keyword,
            new_shared_stories=new_shared_story_text_list,
            shared_stories=shared_story_text_list,
            hit_count=hit_count,
            used_in=used_in if used_in is not None else [],
            earliest_time_usec=earliest_time_usec,
            earliest_pos_idx=earliest_pos_idx
        )
    
    def parse_batch(self, search_kanji_list: List[str], hit_count_list: List[int]=None, show_pbar: bool=True, leave_pbar: bool=True) -> KoohiiResultList:
        results = KoohiiResultList()
        if hit_count_list is None:
            hit_count_list = [0] * len(search_kanji_list)
        pbar = tqdm(total=len(search_kanji_list), unit='kanji', leave=leave_pbar) if show_pbar else None
        for search_kanji, hit_count in zip(search_kanji_list, hit_count_list):
            if pbar is not None:
                pbar.set_description(f'Parsing Koohii Data For: {search_kanji}')
            result = self.parse(search_kanji, hit_count=hit_count)
            results.append(result)
            if pbar is not None:
                pbar.update()
        if pbar is not None:
            pbar.close()
        return results
    
    def parse_and_save(
        self, kanji_info_list: WritingKanjiInfoList,
        save_dir: str='kanji_save',
        force: bool=False,
        sort_by_hit_count: bool=False,
        show_pbar: bool=True, leave_pbar: bool=True,
        combined_save_path: str=None,
        learned_kanji_txt_path: str=None, filtered_dump_path: str=None
    ):
        combined_results = KoohiiResultList() if combined_save_path is not None else None
        pbar = tqdm(total=len(kanji_info_list), unit='kanji', leave=leave_pbar) if show_pbar else None
        for kanji_info in kanji_info_list:
            if pbar is not None:
                pbar.set_description(f'Parsing Koohii Data For: {kanji_info.kanji}')
            if not os.path.isdir(save_dir):
                os.mkdir(save_dir)
            save_path = f'{save_dir}/{kanji_info.kanji}.json'
            if not os.path.isfile(save_path) or force:
                result = self.parse(
                    kanji_info.kanji,
                    hit_count=kanji_info.hit_count, used_in=kanji_info.used_in,
                    earliest_time_usec=kanji_info.earliest_time_usec,
                    earliest_pos_idx=kanji_info.earliest_pos_idx
                )
            else:
                result = KoohiiResult.load_from_path(save_path)
                result.hit_count = kanji_info.hit_count
                result.used_in = kanji_info.used_in
                result.earliest_time_usec = kanji_info.earliest_time_usec
                result.earliest_pos_idx = kanji_info.earliest_pos_idx
            result.save_to_path(save_path, overwrite=True)
            if combined_results is not None:
                combined_results.append(result)
            if pbar is not None:
                pbar.update()
        if pbar is not None:
            pbar.close()
        if combined_results is not None:
            if sort_by_hit_count:
                combined_results.sort(attr_name='hit_count', reverse=True)
            combined_results.save_to_path(combined_save_path, overwrite=True)
            if learned_kanji_txt_path is not None and filtered_dump_path is not None:
                f = open(learned_kanji_txt_path, 'r')
                lines = f.readlines()
                learned_kanji_list = [line.replace('\n', '') for line in lines]
                filtered_results = combined_results.filter_out_kanji(learned_kanji_list)
                filtered_results.save_to_path(filtered_dump_path, overwrite=True)