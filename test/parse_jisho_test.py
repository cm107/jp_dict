from __future__ import annotations
from typing import List, Any, cast
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler
from logger import logger
from src.util.char_lists import hiragana_chars, katakana_chars, misc_kana_chars

class WordRepresentationPart(BasicLoadableObject['WordRepresentationPart']):
    def __init__(self, writing: str, reading: str=None):
        super().__init__()
        self.writing = writing
        self.reading = reading

class WordRepresentationPartList(
    BasicLoadableHandler['WordRepresentationPartList', 'WordRepresentationPart'],
    BasicHandler['WordRepresentationPartList', 'WordRepresentationPart']
):
    def __init__(self, part_list: List[WordRepresentationPart]=None):
        super().__init__(obj_type=WordRepresentationPart, obj_list=part_list)
        self.part_list = self.obj_list
    
    @classmethod
    def from_dict_list(self, dict_list: List[dict]) -> WordRepresentationPartList:
        return WordRepresentationPartList([WordRepresentationPart.from_dict(item_dict) for item_dict in dict_list])

class WordRepresentation(BasicLoadableObject['WordRepresentation']):
    def __init__(self, writing: str, reading: str, reading2writing_idx_list: List[int]=None):
        super().__init__()
        self._is_dirty_case = False
        if reading2writing_idx_list is not None:
            print(f'writing: {writing}')
            print(f'reading2writing_idx_list: {reading2writing_idx_list}')
            for idx in range(len(writing)):
                if idx not in reading2writing_idx_list:
                    self._is_dirty_case = True
                    break
            for i in range(len(reading2writing_idx_list)):
                if i > 0:
                    assert reading2writing_idx_list[i] >= reading2writing_idx_list[i-1]
        self.writing = writing
        self.reading = reading
        self.reading2writing_idx_list = reading2writing_idx_list if not self.is_dirty_case else None
    
    def to_part_list(self) -> WordRepresentationPartList:
        if self.reading2writing_idx_list is None:
            return WordRepresentationPartList([WordRepresentationPart(writing=self.writing, reading=self.reading)])
        else:
            part_dict = {idx: '' for idx in list(set(self.reading2writing_idx_list))}
            for idx in self.reading2writing_idx_list:
                part_dict[idx] += self.reading[idx]
            assert len(part_dict) == len(self.writing)
            part_list = []
            for reading_part, writing_char in zip(list(part_dict.values()), list(self.writing)):
                part_list.append(WordRepresentationPart(writing=writing_char, reading=reading_part))
            return WordRepresentationPartList(part_list)
    
    @classmethod
    def from_part_list(self, part_list: WordRepresentationPartList) -> WordRepresentation:
        assert len(part_list) >= 1
        if len(part_list) == 1:
            assert len(part_list[0].reading) >= 1
            if len(part_list[0].reading) == 1:
                assert len(part_list[0].writing) == 1
                return WordRepresentation(writing=part_list[0].writing, reading=part_list[0].reading, reading2writing_idx_list=[0])
            else:
                return WordRepresentation(writing=part_list[0].writing, reading=part_list[0].reading, reading2writing_idx_list=None)
        else:
            working_writing = ''
            working_reading = ''
            reading2writing_idx_list = []
            working_idx = None
            for part in part_list:
                working_idx = 0 if working_idx is None else working_idx + 1
                assert len(part.writing) == 1
                for i in range(len(part.reading)):
                    reading2writing_idx_list.append(working_idx)
                working_writing += part.writing
                working_reading += part.reading
            return WordRepresentation(writing=working_writing, reading=working_reading, reading2writing_idx_list=reading2writing_idx_list)
    
    @property
    def kanji_list(self) -> List[str]:
        return [part.writing for part in self.to_part_list() if part.writing != part.reading]

    @property
    def furigana_list(self) -> List[str]:
        return [part.reading for part in self.to_part_list() if part.writing != part.reading]
    
    @property
    def okurigana_list(self) -> List[str]:
        return [part.reading for part in self.to_part_list() if part.writing == part.reading]

    @property
    def is_dirty_case(self) -> bool:
        return self._is_dirty_case

class JapaneseSentence(
    BasicLoadableHandler['JapaneseSentence', 'WordRepresentation'],
    BasicHandler['JapaneseSentence', 'WordRepresentation']
):
    def __init__(self, words: List[WordRepresentation]=None):
        super().__init__(obj_type=WordRepresentation, obj_list=words)
        self.words = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> JapaneseSentence:
        return JapaneseSentence([WordRepresentation.from_dict(item_dict) for item_dict in dict_list])

    @property
    def writing_list(self) -> List[str]:
        return [word.writing for word in self]

    @property
    def writing(self) -> str:
        return ''.join(self.writing_list)

    @property
    def reading_list(self) -> List[str]:
        return [word.reading for word in self]
    
    @property
    def reading(self) -> str:
        return ''.join(self.reading_list)

class ExampleSentence(BasicLoadableObject['ExampleSentence']):
    def __init__(self, japanese_sentence: JapaneseSentence, english_translation: str):
        super().__init__()
        self.japanese_sentence = japanese_sentence
        self.english_translation = english_translation

class ExampleSentenceList(
    BasicLoadableHandler['ExampleSentenceList', 'ExampleSentence'],
    BasicHandler['ExampleSentenceList', 'ExampleSentence']
):
    def __init__(self, sentences: List[ExampleSentence]=None):
        super().__init__(obj_type=ExampleSentence, obj_list=sentences)
        self.sentences = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> ExampleSentenceList:
        return ExampleSentenceList([ExampleSentence.from_dict(item_dict) for item_dict in dict_list])

class ConceptLabels(BasicLoadableObject['ConceptLabels']):
    def __init__(
        self, is_common: bool=False,
        is_jlpt: bool=False, jlpt_level: int=None,
        is_wanikani: bool=False, wanikani_level: int=None
    ):
        super().__init__()
        self.is_common = is_common
        self.is_jlpt = is_jlpt
        self.jlpt_level = jlpt_level
        self.is_wanikani = is_wanikani
        self.wanikani_level = wanikani_level

class Link(BasicLoadableObject['Link']):
    def __init__(self, url: str, text: str=None):
        super().__init__()
        self.url = url
        self.text = text

class SupplementaryLinks(BasicLoadableObject['SupplementaryLinks']):
    def __init__(
        self, has_audio: bool=False, audio_link_list: List[Link]=None,
        has_collocations: bool=False, collocation_link_list: List[Link]=None,
        has_other_links: bool=False, other_link_list: List[Link]=None
    ):
        super().__init__()
        self.has_audio = has_audio
        self.audio_link_list = audio_link_list if audio_link_list is not None else []
        self.has_collocations = has_collocations
        self.collocation_link_list = collocation_link_list if collocation_link_list is not None else []
        self.has_other_links = has_other_links
        self.other_link_list = other_link_list if other_link_list is not None else []

class SupplementalInfoStructs:
    class PlainText(BasicLoadableObject['PlainText']):
        def __init__(self, text: str, tag: str):
            self.text = text
            self.tag = tag
        
        def __str__(self) -> str:
            return f'{self.text} *{self.tag}*'

    class PlainTextWithLink(BasicLoadableObject['PlainTextWithLink']):
        def __init__(self, text: str, link: Link, tag: str):
            self.text = text
            self.link = link
            self.tag = tag
        
        def __str__(self) -> str:
            return f'{self.text}[{self.link.text}]({self.link.url}) *{self.tag}*'

class SupplementalInfo(BasicLoadableObject['SupplementalInfo']):
    def __init__(self, part_list: List[Any]):
        for part in part_list:
            assert type(part) in [SupplementalInfoStructs.PlainText, SupplementalInfoStructs.PlainTextWithLink]
        self.part_list = part_list
    
    @property
    def tag(self) -> SupplementalInfoStructs.PlainText:
        for part in self.part_list:
            if part.tag == 'tag':
                return part
        return None
    
    @property
    def has_tag(self) -> bool:
        return self.tag is not None

    @property
    def info(self) -> SupplementalInfoStructs.PlainText:
        for part in self.part_list:
            if part.tag == 'info':
                return part
        return None

    @property
    def has_info(self) -> bool:
        return self.info is not None

    @property
    def restriction(self) -> SupplementalInfoStructs.PlainText:
        for part in self.part_list:
            if part.tag == 'restriction':
                return part
        return None
    
    @property
    def has_restriction(self) -> bool:
        return self.restriction is not None

    @property
    def see_also(self) -> SupplementalInfoStructs.PlainTextWithLink:
        for part in self.part_list:
            if part.tag == 'see_also':
                return part
        return None
    
    @property
    def has_see_also(self) -> bool:
        return self.see_also is not None

    @property
    def antonym(self) -> SupplementalInfoStructs.PlainTextWithLink:
        for part in self.part_list:
            if part.tag == 'antonym':
                return part
        return None
    
    @property
    def has_antonym(self) -> bool:
        return self.antonym is not None

    def to_dict(self) -> dict:
        return self.to_dict_list()

    def to_dict_list(self) -> List[dict]:
        return [struct_obj.to_dict() for struct_obj in self.part_list]

    @classmethod
    def from_dict(cls, item_dict: dict) -> SupplementalInfo:
        return cls.from_dict_list(item_dict)

    @classmethod
    def from_dict_list(self, dict_list: List[dict]) -> SupplementalInfo:
        part_list = []
        for item_dict in dict_list:
            if set(list(item_dict.keys())) == set(['text', 'tag']):
                part_list.append(SupplementalInfoStructs.PlainText.from_dict(item_dict))
            elif set(list(item_dict.keys())) == set(['text', 'link', 'tag']):
                part_list.append(SupplementalInfoStructs.PlainTextWithLink.from_dict(item_dict))
            else:
                raise TypeError(f'Could not resolve the specific SupplementalInfoStructs type from the following item_dict:\n{item_dict}')
        return SupplementalInfo(part_list)

class MeaningTags(BasicLoadableObject['MeaningTags']):
    def __init__(self, meaning_tag_text: str):
        self.meaning_tag_text = meaning_tag_text

    @property
    def is_other_forms_tag(self) -> bool:
        return self.meaning_tag_text == 'Other forms'
    
    @property
    def is_notes_tag(self) -> bool:
        return self.meaning_tag_text == 'Notes'

class MeaningWrapper(BasicLoadableObject['MeaningWrapper']):
    def __init__(
        self,
        has_section_divider: bool=False, section_divider_text: str=None,
        has_meaning: bool=False, meaning_text: str=None,
        has_supplemental_info: bool=False, supplemental_info: SupplementalInfo=None,
        has_meaning_abstract: bool=False, meaning_abstract_text: str=None,
        has_meaning_abstract_link: bool=False, meaning_abstract_link: Link=None,
        has_sentences: bool=False, sentences: ExampleSentenceList=None
    ):
        self.has_section_divider = has_section_divider
        self.section_divider_text = section_divider_text
        self.has_meaning = has_meaning
        self.meaning_text = meaning_text
        self.has_supplemental_info = has_supplemental_info
        self.supplemental_info = supplemental_info
        self.has_meaning_abstract = has_meaning_abstract
        self.meaning_abstract_text = meaning_abstract_text
        self.has_meaning_abstract_link = has_meaning_abstract_link
        self.meaning_abstract_link = meaning_abstract_link
        self.has_sentences = has_sentences
        self.sentences = sentences

class MeaningWrapperHandler(
    BasicLoadableHandler['MeaningWrapperHandler', 'MeaningWrapper'],
    BasicHandler['MeaningWrapperHandler', 'MeaningWrapper']
):
    def __init__(self, wrapper_list: List[MeaningWrapper]=None):
        super().__init__(obj_type=MeaningWrapper, obj_list=wrapper_list)
        self.wrapper_list = self.obj_list

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> MeaningWrapperHandler:
        return MeaningWrapperHandler([MeaningWrapper.from_dict(item_dict) for item_dict in dict_list])

class MeaningGroup(BasicLoadableObject['MeaningGroup']):
    def __init__(self, meaning_tags: MeaningTags, meaning_list: MeaningWrapperHandler=None):
        self.meaning_tags = meaning_tags
        self.meaning_list = meaning_list if meaning_list is not None else MeaningWrapperHandler()

class MeaningGroupHandler(
    BasicLoadableHandler['MeaningGroupHandler', 'MeaningGroup'],
    BasicHandler['MeaningGroupHandler', 'MeaningGroup']
):
    def __init__(self, groups: List[MeaningGroup]=None):
        super().__init__(obj_type=MeaningGroup, obj_list=groups)
        self.groups = self.obj_list

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> MeaningGroupHandler:
        return MeaningGroupHandler([MeaningGroup.from_dict(item_dict) for item_dict in dict_list])

class OtherForm(BasicLoadableObject['OtherForm']):
    def __init__(self, writing: str, reading: str):
        super().__init__()
        self.writing = writing
        self.reading = reading

    def __str__(self) -> str:
        return f'{self.writing} 【{self.reading}】'

class OtherFormList(
    BasicLoadableHandler['OtherFormList', 'OtherForm'],
    BasicHandler['OtherFormList', 'OtherForm']
):
    def __init__(self, other_forms: List[OtherForm]=None):
        super().__init__(obj_type=OtherForm, obj_list=other_forms)
        self.other_forms = self.obj_list
    
    def __str__(self) -> str:
        print_str = ''
        for i, other_form in enumerate(self):
            if i == 0:
                print_str += str(other_form)
            else:
                print_str += f'、{other_form}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> OtherFormList:
        return OtherFormList([OtherForm.from_dict(item_dict) for item_dict in dict_list])

class Note(BasicLoadableObject['Note']):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

class NoteList(
    BasicLoadableHandler['NoteList', 'Note'],
    BasicHandler['NoteList', 'Note']
):
    def __init__(self, notes: List[Note]=None):
        super().__init__(obj_type=Note, obj_list=notes)
        self.notes = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> NoteList:
        return NoteList([Note.from_dict(item_dict) for item_dict in dict_list])

class MeaningParser:
    def __init__(self):
        self.meaning_part_list = []
    
    @property
    def other_forms(self) -> OtherFormList:
        for part in self.meaning_part_list:
            if isinstance(part, OtherFormList):
                return part
        return None
    
    @property
    def notes(self) -> NoteList:
        for part in self.meaning_part_list:
            if isinstance(part, NoteList):
                return part
        return None

    def append(self, part: Any):
        possible_nontag_types = (MeaningWrapper, OtherFormList, NoteList)
        if isinstance(part, MeaningTags):
            if len(self.meaning_part_list) == 0:
                self.meaning_part_list.append(part)
            else:
                if isinstance(self.meaning_part_list[-1], MeaningTags):
                    raise TypeError('Cannot append two MeaningTags consecutively.')
                elif isinstance(self.meaning_part_list[-1], possible_nontag_types):
                    self.meaning_part_list.append(part)
                else:
                    raise Exception
        elif isinstance(part, possible_nontag_types):
            if len(self.meaning_part_list) == 0:
                raise TypeError(f'self.meaning_part_list cannot start with {possible_nontag_types}')
            else:
                self.meaning_part_list.append(part)
        else:
            raise TypeError(f'Cannot append {part.__class__.__name__} to self.meaning_part_list')

    def get_group_handler(self) -> MeaningGroupHandler:
        group_handler = MeaningGroupHandler()
        working_group = cast(MeaningGroup, None)
        for part in self.meaning_part_list:
            if isinstance(part, MeaningTags):
                if part.meaning_tag_text in ['Other forms', 'Notes']:
                    continue
                if working_group is None:
                    working_group = MeaningGroup(meaning_tags=part)
                else:
                    group_handler.append(working_group)
                    working_group = MeaningGroup(meaning_tags=part)
            elif isinstance(part, MeaningWrapper):
                working_group.meaning_list.append(part)
            elif isinstance(part, (OtherFormList, NoteList)):
                continue
            else:
                raise Exception
        if working_group is not None:
            if len(working_group.meaning_list) > 0:
                group_handler.append(working_group)
            else:
                raise Exception(f'During grouping, encountered leftover group without any meanings:\n{working_group}')
        return group_handler

    def print_parts(self):
        for part in self.meaning_part_list:
            if isinstance(part, MeaningTags):
                logger.purple(part)
            elif isinstance(part, MeaningWrapper):
                logger.white(part)
            else:
                raise Exception
    
    def summarize(self):
        groups = self.get_group_handler()
        for group in groups:
            logger.blue('================')
            for meaning in group.meaning_list:
                if meaning.sentences is not None:
                    logger.purple(f'meaning.sentences[0].japanese_sentence.writing: {meaning.sentences[0].japanese_sentence.writing}')
                    logger.purple(f'meaning.sentences[0].japanese_sentence.reading: {meaning.sentences[0].japanese_sentence.reading}')
        logger.blue(f'self.other_forms: {self.other_forms}')
        logger.blue(f'self.notes: {self.notes}')

class JishoSearchHtmlParser:
    def __init__(self, search_word: str):
        self.http = urllib3.PoolManager()
        page = self.http.request(method='GET', url=f'https://jisho.org/search/{search_word}')
        self.soup = BeautifulSoup(page.data, 'html.parser')
        self.parsed_data_dict = {}

    def parse(self):
        main_results_html = self.soup.find(name='div', attrs={'id': 'main_results'})
        no_matches_html = main_results_html.find(name='div', attrs={'id': 'no-matches'})
        matches_exist = no_matches_html is None
        self.parsed_data_dict['matches_exist'] = matches_exist
    
        if matches_exist:
            primary_html = main_results_html.find(name='div', attrs={'id': 'primary'})

            # Exact Results
            self.parse_exact_matches(primary_html)

            # Non-exact Results
            self.parse_nonexact_matches(primary_html)
        else:
            print('No results found.')
    
    def parse_exact_matches(self, primary_html: Tag):
        exact_block_html = primary_html.find(name='div', attrs={'class': 'exact_block'}) # Exact matches
        result_count_html = exact_block_html.find(name='span', attrs={'class': 'result_count'})
        result_count = int(result_count_html.text.replace('—', '').replace('found', '').replace(' ', ''))
        print(f'result_count: {result_count}')
        self.parsed_data_dict['result_count'] = result_count
        concept_light_clearfix_html_list = exact_block_html.find_all(name='div', attrs={'class': 'concept_light clearfix'})
        for concept_light_clearfix_html in concept_light_clearfix_html_list:
            self.parse_concept_light_clearfix(concept_light_clearfix_html)

    def parse_nonexact_matches(self, primary_html: Tag):
        concepts_html = primary_html.find(name='div', attrs={'class': 'concepts'}) # Non-exact matches
        concept_light_clearfix_html_list = concepts_html.find_all(name='div', attrs={'class': 'concept_light clearfix'}) # Non-exact match list
        more_html = concepts_html.find(name='a', attrs={'class': 'more'}, href=True)
        more_button_exists = more_html is not None
        if more_button_exists:
            more_words_url = f"https:{more_html['href']}"
            self.parsed_data_dict['more_words_url'] = more_words_url

    def parse_concept_light_clearfix(self, concept_light_clearfix_html: Tag):
        word_representation = self.parse_word_representation(concept_light_clearfix_html)
        logger.yellow(f'word_representation: {word_representation}')
        if word_representation.is_dirty_case:
            logger.red(f'word_representation.is_dirty_case: {word_representation.is_dirty_case}')

        concept_labels = self.parse_concept_labels(concept_light_clearfix_html)
        # logger.purple(f'concept_labels: {concept_labels}')

        supplementary_links = self.parse_supplementary_links(concept_light_clearfix_html)
        # logger.purple(f'supplementary_links:\n{supplementary_links}')

        self.parse_meanings(concept_light_clearfix_html)

    def parse_word_representation(self, concept_light_clearfix_html: Tag) -> WordRepresentation:
        concept_light_representation_html = concept_light_clearfix_html.find(name='div', attrs={'class': 'concept_light-representation'})
        furigana_html = concept_light_representation_html.find(name='span', attrs={'class': 'furigana'})
        text_html = concept_light_representation_html.find(name='span', attrs={'class': 'text'})
        text = text_html.text.strip()
        furigana = furigana_html.text.strip()

        furigana_part_html_list = furigana_html.find_all(name='span')
        furigana_str_list = []
        working_text = text
        for furigana_part_html in furigana_part_html_list:
            # print(f'furigana_part_html.attrs: {furigana_part_html.attrs}')
            # print(f'furigana_part_html.contents: {furigana_part_html.contents}')
            if 'class' in furigana_part_html.attrs and 'kanji' in furigana_part_html.attrs['class']:
                assert furigana_part_html.attrs['class'][0].startswith('kanji-') and furigana_part_html.attrs['class'][0].endswith('-up')
                furigana_str = furigana_part_html.contents[0]
                furigana_str_list.append(furigana_str)
                working_text = working_text[1:]
            else:
                if working_text[0] in hiragana_chars or working_text[0] in katakana_chars or working_text[0] in misc_kana_chars:
                    furigana_str_list.append(working_text[0])
                working_text = working_text[1:]
        if len(furigana_str_list) == len(text):
            part_list = WordRepresentationPartList([WordRepresentationPart(writing=text_char, reading=furigana_str) for furigana_str, text_char in zip(furigana_str_list, list(text))])
            return WordRepresentation.from_part_list(part_list)
        else:
            return WordRepresentation(writing=text, reading=furigana, reading2writing_idx_list=None)

    def parse_concept_labels(self, concept_light_clearfix_html: Tag) -> ConceptLabels:
        common_label_html = concept_light_clearfix_html.find(name='span', attrs={'class': 'concept_light-tag concept_light-common success label'})
        is_common = common_label_html is not None

        is_jlpt = False
        jlpt_level = None
        is_wanikani = False
        wanikani_level = None

        concept_light_label_html_list = concept_light_clearfix_html.find_all(name='span', attrs={'class': 'concept_light-tag label'})
        for concept_light_label_html in concept_light_label_html_list:
            if 'JLPT' in concept_light_label_html.text:
                is_jlpt = True
                jlpt_level = int(concept_light_label_html.text.replace('JLPT N', ''))
            elif 'Wanikani' in concept_light_label_html.text:
                is_wanikani = True
                wanikani_level = int(concept_light_label_html.text.replace('Wanikani level ', ''))
            else:
                raise Exception(f'Unaccounted for concept_light_label_html.text:\n{concept_light_label_html.text}')

        concept_labels = ConceptLabels( # Use
            is_common=is_common,
            is_jlpt=is_jlpt, jlpt_level=jlpt_level,
            is_wanikani=is_wanikani, wanikani_level=wanikani_level
        )
        return concept_labels
    
    def parse_supplementary_links(self, concept_light_clearfix_html: Tag) -> SupplementaryLinks:
        audio_html = concept_light_clearfix_html.find(name='audio')
        has_audio = audio_html is not None
        audio_link_list = []
        if has_audio:
            audio_source_html_list = audio_html.find_all(name='source', src=True)
            for audio_source_html in audio_source_html_list:
                audio_source_url = f"https:{audio_source_html['src']}"
                audio_link = Link(url=audio_source_url)
                audio_link_list.append(audio_link)

        collocations_html = concept_light_clearfix_html.find(name='div', attrs={'class': 'reveal-modal small'})
        has_collocations = collocations_html is not None
        collocation_link_list = []
        if has_collocations:
            collocation_link_html_list = collocations_html.find_all(name='li')
            for collocation_link_html in collocation_link_html_list:
                collocation_html = collocation_link_html.find(name='a', href=True)
                collocation_link_url = f"https://jisho.org{collocation_html['href']}"
                collocation_link_text = collocation_html.text.strip()
                collocation_link = Link(url=collocation_link_url, text=collocation_link_text)
                collocation_link_list.append(collocation_link)

        links_dropdown_html = concept_light_clearfix_html.find(name='ul', attrs={'class': 'f-dropdown'})
        has_other_links = links_dropdown_html is not None
        other_link_list = []
        if has_other_links:
            link_html_list = links_dropdown_html.find_all(name='li')
            for link_html in link_html_list:
                link_a_html = link_html.find(name='a', href=True)
                if link_a_html['href'].startswith('/search'):
                    link_url = f"https://jisho.org{link_a_html['href']}"
                elif link_a_html['href'].startswith('//jisho.org'):
                    link_url = f"https:{link_a_html['href']}"
                else:
                    link_url = link_a_html['href']
                link_text = link_a_html.text.strip()
                concept_link = Link(url=link_url, text=link_text)
                other_link_list.append(concept_link)

        supplementary_links = SupplementaryLinks(
            has_audio=has_audio, audio_link_list=audio_link_list,
            has_collocations=has_collocations, collocation_link_list=collocation_link_list,
            has_other_links=has_other_links, other_link_list=other_link_list
        )
        return supplementary_links

    def parse_meanings(self, concept_light_clearfix_html: Tag):
        concept_light_meanings_html = concept_light_clearfix_html.find(name='div', attrs={'class': 'concept_light-meanings medium-9 columns'}) # TODO
        meaning_wrapper_html = concept_light_meanings_html.find(name='div', attrs={'class': 'meanings-wrapper'})
        light_details_link_html = concept_light_clearfix_html.find(name='a', attrs={'class': 'light-details_link'}, href=True)
        meaning_part_html_list = meaning_wrapper_html.find_all(name='div', recursive=False)
        # print(f'len(meaning_part_html_list): {len(meaning_part_html_list)}')
        meaning_parser = MeaningParser()
        current_meaning_tag = cast(MeaningTags, None)
        for meaning_part_html in meaning_part_html_list:
            # logger.cyan(f"meaning_part_html['class']: {meaning_part_html['class']}")
            if meaning_part_html['class'] == ['meaning-tags']:
                meaning_tag_text = meaning_part_html.text.strip()
                meaning_tag = MeaningTags(meaning_tag_text)
                meaning_parser.append(meaning_tag)
                current_meaning_tag = meaning_tag
            elif meaning_part_html['class'] == ['meaning-wrapper']:
                if current_meaning_tag.meaning_tag_text == 'Other forms':
                    other_form_html_list = meaning_part_html.find_all(name='span', attrs={'class': 'break-unit'})
                    other_forms = OtherFormList()
                    for other_form_html in other_form_html_list:
                        other_form_text = other_form_html.text.strip().replace(' ', '')
                        left_bracket_idx, right_bracket_idx = other_form_text.index('【'), other_form_text.index('】')
                        other_form_writing = other_form_text[:left_bracket_idx]
                        other_form_reading = other_form_text[left_bracket_idx+1:right_bracket_idx]
                        other_form = OtherForm(writing=other_form_writing, reading=other_form_reading)
                        other_forms.append(other_form)
                    meaning_parser.append(other_forms)
                elif current_meaning_tag.meaning_tag_text == 'Notes':
                    note_html_list = meaning_part_html.find_all(name='div', attrs={'class': 'meaning-definition meaning-representation_notes zero-padding'})
                    notes = NoteList()
                    for note_html in note_html_list:
                        note_text = note_html.text.strip()
                        note = Note(note_text)
                        notes.append(note)
                    meaning_parser.append(notes)
                else:
                    meaning_definition_html = meaning_part_html.find(name='div', attrs={'class': 'meaning-definition zero-padding'})
                    if meaning_definition_html is None:
                        raise Exception(f'Failed to parse meaning_definition_html. Could be new special section.\ncurrent_meaning_tag:\n{current_meaning_tag}')
                    section_divider_html = meaning_definition_html.find(name='span', attrs={'class': 'meaning-definition-section_divider'})
                    has_section_divider = section_divider_html is not None
                    section_divider_text = None
                    if has_section_divider:
                        section_divider_text = section_divider_html.text.strip()
                    meaning_html = meaning_definition_html.find(name='span', attrs={'class': 'meaning-meaning'})
                    has_meaning = meaning_html is not None
                    meaning_text = None
                    if has_meaning:
                        meaning_text = meaning_html.text.strip()
                    supplemental_info_html = meaning_definition_html.find(name='span', attrs={'class': 'supplemental_info'})
                    has_supplemental_info = supplemental_info_html is not None
                    supplemental_info = None
                    if has_supplemental_info:
                        supplemental_info = self.parse_supplemental_info(supplemental_info_html)
                    meaning_abstract_html = meaning_definition_html.find(name='span', attrs={'class': 'meaning-abstract'})
                    has_meaning_abstract = meaning_abstract_html is not None
                    meaning_abstract_text = None
                    has_meaning_abstract_link = False
                    meaning_abstract_link = None
                    if has_meaning_abstract:
                        meaning_abstract_text = meaning_abstract_html.text.strip()
                        meaning_abstract_link_html = meaning_abstract_html.find(name='a', href=True)
                        has_meaning_abstract_link = meaning_abstract_link_html is not None
                        if has_meaning_abstract_link:
                            meaning_abstract_link_url = f"https:{meaning_abstract_link_html['href']}"
                            meaning_abstract_link_text = meaning_abstract_link_html.text.strip()
                            meaning_abstract_text = meaning_abstract_text.replace(meaning_abstract_link_text, '')
                            meaning_abstract_link = Link(url=meaning_abstract_link_url, text=meaning_abstract_link_text)

                    sentences_html = meaning_part_html.find(name='span', attrs={'class': 'sentences zero-padding'})
                    has_sentences = sentences_html is not None
                    sentences = cast(ExampleSentenceList, None)
                    if has_sentences:
                        sentences = self.parse_sentences(sentences_html)

                    meaning_wrapper = MeaningWrapper(
                        has_section_divider=has_section_divider, section_divider_text=section_divider_text,
                        has_meaning=has_meaning, meaning_text=meaning_text,
                        has_supplemental_info=has_supplemental_info, supplemental_info=supplemental_info,
                        has_meaning_abstract=has_meaning_abstract, meaning_abstract_text=meaning_abstract_text,
                        has_meaning_abstract_link=has_meaning_abstract_link, meaning_abstract_link=meaning_abstract_link,
                        has_sentences=has_sentences, sentences=sentences
                    )
                    meaning_parser.append(meaning_wrapper)
            else:
                raise Exception(f"Unexpected meaning_part_html['class']: {meaning_part_html['class']}")
        meaning_parser.summarize()

    def parse_supplemental_info(self, supplemental_info_html: Tag) -> SupplementalInfo:
        supplemental_info_part_html_list = supplemental_info_html.find_all(name='span', attrs={'class': 'sense-tag'})
        supplemental_info_parts = []
        for supplemental_info_part_html in supplemental_info_part_html_list:
            # print(f"supplemental_info_part_html['class']: {supplemental_info_part_html['class']}")
            if supplemental_info_part_html['class'] in [['sense-tag', 'tag-tag'], ['sense-tag', 'tag-info'], ['sense-tag', 'tag-restriction']]:
                tag_text = supplemental_info_part_html.text.strip()
                plain_text = SupplementalInfoStructs.PlainText(
                    text=tag_text,
                    tag=supplemental_info_part_html['class'][1].replace('tag-','')
                )
                supplemental_info_parts.append(plain_text)
            elif supplemental_info_part_html['class'] in [['sense-tag', 'tag-see_also'], ['sense-tag', 'tag-antonym']]:
                tag_text = supplemental_info_part_html.text.strip()
                part_link_html = supplemental_info_part_html.find(name='a', href=True)
                part_link_text = part_link_html.text.strip()
                part_link_url = f"https://jisho.org{part_link_html['href']}"
                tag_text = tag_text.replace(part_link_text, '')
                plain_text_with_link = SupplementalInfoStructs.PlainTextWithLink(
                    text=tag_text, link=Link(url=part_link_url, text=part_link_text),
                    tag=supplemental_info_part_html['class'][1].replace('tag-','')
                )
                supplemental_info_parts.append(plain_text_with_link)
            else:
                raise Exception(f"Unexpected supplemental_info_part_html['class']: {supplemental_info_part_html['class']}")
        supplemental_info = SupplementalInfo(supplemental_info_parts)
        return supplemental_info

    def parse_sentences(self, sentences_html: Tag) -> ExampleSentenceList:
        example_sentences = ExampleSentenceList()
        sentence_html_list = sentences_html.find_all(name='div', attrs={'class': 'sentence'})
        for sentence_html in sentence_html_list:
            sentence_text = sentence_html.text.strip()
            english_translation_html = sentence_html.find(name='li', attrs={'class': 'english'})
            english_translation_text = english_translation_html.text.strip()
            print(f'english_translation_text:\n{english_translation_text}')
            sentence_text = sentence_text.replace(english_translation_text, '')
            print(f'sentence_text:\n{sentence_text}')
            sentence_clearfix_html_list = sentence_html.find_all(name='li', attrs={'class': 'clearfix'})
            sentence_writing_parts = []
            sentence_reading_parts = []
            for sentence_clearfix_html in sentence_clearfix_html_list:
                unlinked_html = sentence_clearfix_html.find(name='span', attrs={'class': 'unlinked'})
                unlinked_text = unlinked_html.text.strip()
                furigana_html = sentence_clearfix_html.find(name='span', attrs={'class': 'furigana'})
                furigana_text = furigana_html.text.strip() if furigana_html is not None else unlinked_text
                success = False
                if furigana_html is not None:
                    while len(sentence_text) > 0:
                        if sentence_text.startswith(furigana_text):
                            # sentence_reading_parts.append(furigana_text)
                            sentence_text = sentence_text[len(furigana_text):]
                            assert sentence_text.startswith(unlinked_text)
                            sentence_writing_parts.append(unlinked_text)
                            sentence_text = sentence_text[len(unlinked_text):]
                            last_kanji_idx = None
                            for i, char in enumerate(unlinked_text):
                                if char not in hiragana_chars + katakana_chars + misc_kana_chars:
                                    last_kanji_idx = i
                            if last_kanji_idx is None:
                                raise Exception(
                                    f"""
                                    Couldn't find last kanji in unlinked_text:
                                    {unlinked_text}
                                    """
                                )
                            else:
                                okurigana_text = unlinked_text[last_kanji_idx+1:]
                                if len(okurigana_text) > 0:
                                    sentence_reading_parts.append(furigana_text + okurigana_text)
                                else:
                                    sentence_reading_parts.append(furigana_text)
                            success = True
                            break
                        else:
                            sentence_writing_parts.append(sentence_text[0])
                            sentence_reading_parts.append(sentence_text[0])
                            sentence_text = sentence_text[1:]
                else:
                    while len(sentence_text) > 0:
                        if sentence_text.startswith(unlinked_text):
                            sentence_writing_parts.append(unlinked_text)
                            for char_str in unlinked_text:
                                assert char_str in hiragana_chars + katakana_chars + misc_kana_chars
                            sentence_reading_parts.append(unlinked_text)
                            sentence_text = sentence_text[len(unlinked_text):]
                            success = True
                            break
                        else:
                            sentence_writing_parts.append(sentence_text[0])
                            sentence_reading_parts.append(sentence_text[0])
                            sentence_text = sentence_text[1:]
                if not success:
                    raise Exception(
                        f"""
                        Failed to parse example sentence parts.
                        unlinked_text: {unlinked_text}
                        furigana_text: {furigana_text}
                        furigana_html is not None: {furigana_html is not None}
                        sentence_text: {sentence_text}
                        """
                    )
            if len(sentence_text) > 0:
                sentence_writing_parts.append(sentence_text)
                sentence_reading_parts.append(sentence_text)
                sentence_text = ''
            assert len(sentence_writing_parts) == len(sentence_reading_parts)
            japanese_sentence = JapaneseSentence(
                [
                    WordRepresentation(writing=writing_part, reading=reading_part) \
                        for writing_part, reading_part in zip(sentence_writing_parts, sentence_reading_parts)
                ]
            )
            example_sentence = ExampleSentence(japanese_sentence=japanese_sentence, english_translation=english_translation_text)
            example_sentences.append(example_sentence)
        return example_sentences

# parser = JishoSearchHtmlParser('日')
parser = JishoSearchHtmlParser('落ちる')
# parser = JishoSearchHtmlParser('ニヤリ')
# parser = JishoSearchHtmlParser('送り仮名')
# parser = JishoSearchHtmlParser('日記帳')
# parser = JishoSearchHtmlParser('lsdgkj')
parser.parse()
