from __future__ import annotations
from typing import List, Dict
from tqdm import tqdm
from datetime import datetime
from collections import OrderedDict

from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler
from common_utils.file_utils import dir_exists
from ..jisho.jisho_matches import DictionaryEntryMatchList as JishoEntries, \
    DictionaryEntryMatch as JishoEntry
from ..kotobank.kotobank_structs import KotobankResult, KotobankResultList
from ..util.char_lists import convert_katakana2hiragana, nonkanji_chars
from ...util.time_utils import get_localtime_from_time_usec, \
    get_utc_time_from_time_usec
from ..anki.export_txt_parser import AnkiExportTextData
from ...anki.note_structs import ParsedVocabularyFields, ParsedVocabularyFieldsList
from .kanji_info import WritingKanjiInfo, WritingKanjiInfoList
from ...anki.connect import AnkiConnect

class CombinedResult(BasicLoadableObject['CombinedResult']):
    def __init__(self, jisho_result: JishoEntry, kotobank_result: KotobankResult=None):
        self.jisho_result = jisho_result
        self.kotobank_result = kotobank_result

    @classmethod
    def from_dict(cls, item_dict: dict) -> CombinedResult:
        return CombinedResult(
            jisho_result=JishoEntry.from_dict(item_dict['jisho_result']),
            kotobank_result=KotobankResult.from_dict(item_dict['kotobank_result']) if item_dict['kotobank_result'] is not None else None
        )

    def to_vocabulary_fields(self, order_idx: int=None) -> ParsedVocabularyFields:
        common = 'common' if self.jisho_result.entry.concept_labels.is_common else ''
        jlpt_level = self.jisho_result.entry.concept_labels.jlpt_level
        jlpt_level = str(jlpt_level) if jlpt_level is not None else ''
        wanikani_level = self.jisho_result.entry.concept_labels.wanikani_level
        wanikani_level = str(wanikani_level) if wanikani_level is not None else ''
        # searched_words = str(self.jisho_result.search_words).replace('[', '').replace(']', '')
        searched_words = ''
        for search_word, datetime_list in self.localtime_info.items():
            if len(searched_words) == 0:
                searched_words += f'{search_word}: {len(datetime_list)}'
            else:
                searched_words += f', {search_word}: {len(datetime_list)}'
        cumulative_search_localtimes = ''
        for i, localtime in enumerate(self.cumulative_search_localtimes):
            if i == 0:
                cumulative_search_localtimes += localtime.strftime('%Y/%m/%d %H:%M:%S')
            else:
                cumulative_search_localtimes += f", {localtime.strftime('%Y/%m/%d %H:%M:%S')}"

        if self.kotobank_result is not None:
            daijisen = self.kotobank_result.digital_daijisen_content
            daijisen = daijisen.custom_str(indent=0) if daijisen is not None else ''
            daijisen = daijisen.replace('\n', '<br>')

            seisenpan = self.kotobank_result.seisenpan_content
            seisenpan = seisenpan.custom_str(indent=0) if seisenpan is not None else ''
            seisenpan = seisenpan.replace('\n', '<br>')

            ndz = self.kotobank_result.ndz_content
            ndz = ndz.custom_str(indent=0) if ndz is not None else ''
            ndz = ndz.replace('\n', '<br>')
        else:
            daijisen = ''
            seisenpan = ''
            ndz = ''
        kotobank_search_link = f'<a href="https://kotobank.jp/word/{self.kotobank_result.search_word}">Kotobank search for {self.kotobank_result.search_word}</a>' \
            if self.kotobank_result is not None else ''
        jisho_search_link = f'<a href="https://jisho.org/search/{self.jisho_result.entry.word_representation.writing}">Jisho search for {self.jisho_result.entry.word_representation.writing}</a>' \
            if self.jisho_result.entry.word_representation is not None else ''
        ejje_sentence_search_link = f'<a href="https://ejje.weblio.jp/sentence/content/{self.jisho_result.entry.word_representation.writing}">Weblio sentence search for {self.jisho_result.entry.word_representation.writing}</a>' \
            if self.jisho_result.entry.word_representation is not None else '' #TODO
        weblio_search_link = f'<a href="https://www.weblio.jp/content/{self.jisho_result.entry.word_representation.writing}">Weblio search for {self.jisho_result.entry.word_representation.writing}</a>' \
            if self.jisho_result.entry.word_representation is not None else ''
        return ParsedVocabularyFields(
            writing=self.jisho_result.entry.word_representation.writing,
            reading=self.jisho_result.entry.word_representation.reading,
            common=common,
            jlpt_level=jlpt_level,
            wanikani_level=wanikani_level,
            eng_definition=self.jisho_result.entry.meaning_section.custom_str().replace('\n', '<br>'),
            daijisen=daijisen,
            seisenpan=seisenpan,
            ndz=ndz,
            links=self.jisho_result.entry.supplementary_links.html,
            jisho_search_link=jisho_search_link,
            kotobank_search_link=kotobank_search_link,
            ejje_sentence_search_link=ejje_sentence_search_link,
            weblio_search_link=weblio_search_link,
            searched_words=searched_words,
            search_word_hit_count=str(self.search_word_hit_count),
            cumulative_search_localtimes=cumulative_search_localtimes,
            order_idx=str(order_idx) if order_idx is not None else "",
            unique_id=str(self.earliest_time_usec),
        )

    @property
    def time_usec_info(self) -> Dict[str, List[int]]:
        return self.jisho_result.search_words_time_usec

    @time_usec_info.setter
    def time_usec_info(self, time_usec_info: Dict[str, List[int]]):
        self.jisho_result.search_words_time_usec = time_usec_info

    @property
    def localtime_info(self) -> Dict[str, List[datetime]]:
        return {
            search_word: [get_localtime_from_time_usec(time_usec) for time_usec in time_usec_list]
            for search_word, time_usec_list in self.time_usec_info.items()
        }

    @property
    def earliest_time_usec(self) -> int:
        cum_time_usec_list = []
        for search_word, time_usec_list in self.time_usec_info.items():
            cum_time_usec_list.extend(time_usec_list)
        return min(cum_time_usec_list)

    @property
    def search_word_hit_count(self) -> int:
        count = 0
        for search_word, time_usec_list in self.time_usec_info.items():
            count += len(time_usec_list)
        return count

    @property
    def cumulative_search_localtimes(self) -> List[datetime]:
        cumulative_localtimes = []
        for search_word, localtime_list in self.localtime_info.items():
            cumulative_localtimes.extend(localtime_list)
        return cumulative_localtimes

    @property
    def first_search_localtime(self) -> datetime:
        return min(self.cumulative_search_localtimes)
    
    @property
    def last_search_localtime(self) -> datetime:
        return max(self.cumulative_search_localtimes)
    
    @property
    def first_and_last_localtime(self) -> (datetime, datetime):
        localtimes = self.cumulative_search_localtimes
        return (min(localtimes), max(localtimes))

    @property
    def is_common_word(self) -> bool:
        return self.jisho_result.entry.concept_labels.is_common
    
    @property
    def is_jlpt(self) -> bool:
        return self.jisho_result.entry.concept_labels.is_jlpt

    @property
    def jlpt_level(self) -> int:
        return self.jisho_result.entry.concept_labels.jlpt_level

    @property
    def is_wanikani(self) -> bool:
        return self.jisho_result.entry.concept_labels.is_wanikani
    
    @property
    def wanikani_level(self) -> int:
        return self.jisho_result.entry.concept_labels.wanikani_level

    def custom_str(self, indent: int=0) -> str:
        print_str = self.jisho_result.custom_str(indent=indent)
        if self.kotobank_result is not None:
            print_str += '\n' + self.kotobank_result.custom_str(indent=indent)
        return print_str
    
    @property
    def simple_repr(self) -> str:
        return self.custom_str()

    @classmethod
    def from_match(cls, entry_match: JishoEntry, kotobank_dump_dir: str, verbose: bool=False) -> CombinedResult:
        assert dir_exists(kotobank_dump_dir)
        kotobank_results = KotobankResultList()
        # print(entry_match.entry.word_representation.custom_str())
        # print(f'entry_match.linked_kotobank_queries: {entry_match.linked_kotobank_queries}')
        for linked_query in entry_match.linked_kotobank_queries:
            kotobank_result = KotobankResult.load_from_path(f'{kotobank_dump_dir}/{linked_query}.json')
            kotobank_results.append(kotobank_result)
        
        # Use naive approach for now.
        if len(kotobank_results) == 0:
            if verbose:
                print(f"Warning: No results found for {entry_match.entry.word_representation.writing}")
            chosen_kotobank_result = None
        elif len(kotobank_results) == 1:
            chosen_kotobank_result = kotobank_results[0]
        else:
            chosen_kotobank_results = []
            for kotobank_result0 in kotobank_results:
                if convert_katakana2hiragana(kotobank_result0.main_title.reading) == convert_katakana2hiragana(entry_match.entry.word_representation.reading):
                    chosen_kotobank_results.append(kotobank_result0)
            if len(chosen_kotobank_results) == 0:
                for kotobank_result0 in kotobank_results:
                    if convert_katakana2hiragana(kotobank_result0.main_title.writing) == convert_katakana2hiragana(entry_match.entry.word_representation.reading):
                        chosen_kotobank_results.append(kotobank_result0)
                if len(chosen_kotobank_results) == 0:
                    for kotobank_result0 in kotobank_results:
                        if convert_katakana2hiragana(kotobank_result0.main_title.writing) == convert_katakana2hiragana(entry_match.entry.word_representation.writing):
                            chosen_kotobank_results.append(kotobank_result0)
            if len(chosen_kotobank_results) == 1:
                chosen_kotobank_result = chosen_kotobank_results[0]
            elif len(chosen_kotobank_results) == 0:
                if verbose:
                    print(f'entry_match.entry.word_representation.simple_repr: {entry_match.entry.word_representation.simple_repr}')
                    print(f'kotobank: {[kotobank_result.main_title.simple_repr for kotobank_result0 in kotobank_results]}')
                    print(f"Couldn't match any kotobank results to the jisho entry based on writing/reading.")
                chosen_kotobank_result = None
            else:
                kotobank_result_with_most_dictionaries = None
                most_dictionaries = 0
                digital_daijisen_found = False
                for kotobank_result0 in kotobank_results:
                    num_dictionaries = len(kotobank_result0.main_area.articles)
                    if kotobank_result_with_most_dictionaries is None or num_dictionaries > most_dictionaries:
                        kotobank_result_with_most_dictionaries = kotobank_result0
                        most_dictionaries = num_dictionaries
                        if 'デジタル大辞泉の解説' in kotobank_result_with_most_dictionaries.main_area.articles.dictionary_names:
                            digital_daijisen_found = True
                    elif num_dictionaries == most_dictionaries and not digital_daijisen_found and 'デジタル大辞泉の解説' in kotobank_result.main_area.articles.dictionary_names:
                        digital_daijisen_found = True
                        kotobank_result_with_most_dictionaries = kotobank_result0
                chosen_kotobank_result = kotobank_result_with_most_dictionaries
        return CombinedResult(jisho_result=entry_match, kotobank_result=chosen_kotobank_result)

    @property
    def writing_kanji_list(self) -> List[str]:
        chars = [char for char in list(self.jisho_result.entry.word_representation.writing) if char not in nonkanji_chars]
        # return list(set(chars))
        return chars

class CombinedResultList(
    BasicLoadableHandler['CombinedResultList', 'CombinedResult'],
    BasicHandler['CombinedResultList', 'CombinedResult']
):
    def __init__(self, result_list: List[CombinedResult]=None):
        super().__init__(obj_type=CombinedResult, obj_list=result_list)
        self.result_list = self.obj_list

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> CombinedResultList:
        return CombinedResultList([CombinedResult.from_dict(item_dict) for item_dict in dict_list])

    def custom_str(self, indent: int=0, num_line_breaks: int=2) -> str:
        print_str = ''
        first = True
        line_breaks = lambda x: '\n' * x
        for result in self:
            if first:
                print_str += result.custom_str(indent=indent)
                first = False
            else:
                print_str += f'{line_breaks(num_line_breaks)}{result.custom_str(indent=indent)}'
        return print_str

    @property
    def simple_repr(self) -> str:
        return self.custom_str()

    @classmethod
    def from_matches(
        cls, entry_matches: JishoEntries, kotobank_dump_dir: str,
        show_pbar: bool=True, leave_pbar: bool=True,
        verbose: bool=False
    ) -> CombinedResultList:
        results = CombinedResultList()
        pbar = tqdm(total=len(entry_matches), unit='matches', leave=leave_pbar) if show_pbar else None
        if pbar is not None:
            print('Combining Jisho and Kotobank Results')
        for entry_match in entry_matches:
            if pbar is not None:
                pbar.set_description(entry_match.entry.word_representation.writing)
            result = CombinedResult.from_match(
                entry_match=entry_match,
                kotobank_dump_dir=kotobank_dump_dir,
                verbose=verbose
            )
            if result is not None:
                results.append(result)
            if pbar is not None:
                pbar.update()
        if pbar is not None:
            pbar.close()
        return results

    def plot_timeofday_distribution(self, save_path: str='localtime_plot.png', mode: str='localtime'):
        # Google browser history uses time_usec, which seems to be based on utc.
        # Thus, it would be appropriate to first add the utc timezone to the datetime object and then convert
        # to your local timezone.
        import matplotlib.pyplot as plt
        import seaborn as sns
        import datetime

        cum_localtime_list = []
        for result in self:
            for search_word, time_usec_list in result.time_usec_info.items():
                if mode == 'localtime':
                    localtime_list = [get_localtime_from_time_usec(time_usec) for time_usec in time_usec_list]
                else:
                    localtime_list = [get_utc_time_from_time_usec(time_usec) for time_usec in time_usec_list]
                cum_localtime_list.extend(localtime_list)
        
        ax = sns.displot(data=[localtime.hour for localtime in cum_localtime_list])
        plt.savefig(save_path)
        plt.clf()
        plt.close('all')
    
    def sort_by_jlpt(self, jlpt_first: bool=True, reverse: bool=True):
        jlpt_results = self.get(is_jlpt=True)
        non_jlpt_results = self.get(is_jlpt=False)
        jlpt_results.sort(attr_name='jlpt_level', reverse=reverse)
        if jlpt_first:
            self.obj_list = (jlpt_results + non_jlpt_results).obj_list
        else:
            self.obj_list = (non_jlpt_results + jlpt_results).obj_list

    def sort_by_wanikani(self, wanikani_first: bool=True, reverse: bool=False):
        wanikani_results = self.get(is_wanikani=True)
        non_wanikani_results = self.get(is_wanikani=False)
        wanikani_results.sort(attr_name='wanikani_level', reverse=reverse)
        if wanikani_first:
            self.obj_list = (wanikani_results + non_wanikani_results).obj_list
        else:
            self.obj_list = (non_wanikani_results + wanikani_results).obj_list

    def recommended_sort(self, show_pbar: bool=False, leave_pbar: bool=True):
        # Note: The most important sorts come last while the least important ones come first.
        pbar = tqdm(total=5, unit='sorts', leave=leave_pbar) if show_pbar else None
        if pbar is not None:
            pbar.set_description('Sorting by localtime')
        self.sort(attr_name='first_search_localtime') # Initial order
        if pbar is not None:
            pbar.update()
            pbar.set_description('Sorting by wanikani')
        self.sort_by_wanikani(wanikani_first=True, reverse=False)
        if pbar is not None:
            pbar.update()
            pbar.set_description('Sorting by jlpt')
        self.sort_by_jlpt(jlpt_first=True, reverse=True)
        if pbar is not None:
            pbar.update()
            pbar.set_description('Sorting by common words')
        self.sort(attr_name='is_common_word', reverse=True)
        if pbar is not None:
            pbar.update()
            pbar.set_description('Sorting by hit count')
        self.sort(attr_name='search_word_hit_count', reverse=True) # Order by hit count
        if pbar is not None:
            pbar.update()
            pbar.close()
    
    def filter_out_anki_export(self, path: str, show_pbar: bool=True, leave_pbar: bool=True) -> CombinedResultList:
        filtered_results = CombinedResultList()
        export_data = AnkiExportTextData.parse_from_txt(path)

        pbar = tqdm(total=len(self), unit='result(s)', leave=leave_pbar) if show_pbar else None
        if pbar is not None:
            pbar.set_description('Filtering Out Results From Export')
        for result in self:
            if not export_data.contains(writing=result.jisho_result.entry.word_representation.writing):
                filtered_results.append(result)
            if pbar is not None:
                pbar.update()
        if pbar is not None:
            pbar.close()
        return filtered_results
    
    def to_vocabulary_fields_list(self) -> ParsedVocabularyFieldsList:
        fields_list = ParsedVocabularyFieldsList()
        for i, result in enumerate(self):
            fields_list.append(result.to_vocabulary_fields(order_idx=i))
        return fields_list
    
    def get_all_writing_kanji(self, include_hit_count: bool=False, show_pbar: bool=True, leave_pbar: bool=True) -> WritingKanjiInfoList:
        info_list = WritingKanjiInfoList()
        pbar = tqdm(total=len(self), unit='result(s)', leave=leave_pbar) if show_pbar else None
        for result in self:
            if pbar is not None:
                pbar.set_description(f'Parsing Kanji From: {result.jisho_result.entry.word_representation.writing}')
            for i, kanji in enumerate(result.writing_kanji_list):
                if include_hit_count:
                    hit_count = result.search_word_hit_count
                else:
                    hit_count = 1
                earliest_time_usec = result.earliest_time_usec
                relevant_info_list = info_list.get(kanji=kanji)
                if len(relevant_info_list) == 0:
                    info = WritingKanjiInfo(
                        kanji=kanji, hit_count=hit_count,
                        used_in=[result.jisho_result.entry.word_representation.writing],
                        earliest_time_usec=earliest_time_usec, earliest_pos_idx=i
                    )
                    info_list.append(info)
                elif len(relevant_info_list) == 1:
                    relevant_info = relevant_info_list[0]
                    relevant_info.hit_count += hit_count
                    if result.jisho_result.entry.word_representation.writing not in relevant_info.used_in:
                        relevant_info.used_in.append(result.jisho_result.entry.word_representation.writing)
                    if earliest_time_usec < relevant_info.earliest_time_usec:
                        relevant_info.earliest_time_usec = earliest_time_usec
                        relevant_info.earliest_pos_idx = i
                else:
                    raise Exception
            if pbar is not None:
                pbar.update()
        if pbar is not None:
            pbar.close()
        info_list.sort(attr_name='hit_count', reverse=True)
        return info_list
    
    def add_or_update_anki(self, deck_name: str, open_browser: bool=False):
        anki_connect = AnkiConnect()
        if 'parsed_vocab' not in anki_connect.get_model_names():
            anki_connect.create_parsed_vocab_model()
        else:
            anki_connect.update_parsed_vocab_templates_and_styling()
        if deck_name not in anki_connect.get_deck_names():
            anki_connect.create_deck(deck=deck_name)
        anki_connect.add_or_update_parsed_vocab_notes(
            deck_name=deck_name,
            fields_list=self.to_vocabulary_fields_list()
        )
        if open_browser:
            anki_connect.gui_card_browse(query=f'deck:{deck_name}')