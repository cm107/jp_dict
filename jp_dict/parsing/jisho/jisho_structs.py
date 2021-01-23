from __future__ import annotations
from typing import List, Any, cast
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag
from common_utils.base.basic import BasicLoadableObject, BasicLoadableHandler, BasicHandler
from logger import logger
from ..util.char_lists import hiragana_chars, katakana_chars, misc_kana_chars
from ..common import Link, LinkList

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
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        tab1 = '\t' * (indent + 1)
        print_str = f'{tab}Word Representation:'
        print_str += f'\n{tab1}{self.writing}（{self.reading}）'
        return print_str

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

    @property
    def simple_repr(self) -> str:
        return f'{self.writing}（{self.reading}）'

class JapaneseSentence(
    BasicLoadableHandler['JapaneseSentence', 'WordRepresentation'],
    BasicHandler['JapaneseSentence', 'WordRepresentation']
):
    def __init__(self, words: List[WordRepresentation]=None):
        super().__init__(obj_type=WordRepresentation, obj_list=words)
        self.words = self.obj_list
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}{self.writing}'

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
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{self.japanese_sentence.custom_str(indent=indent)}'
        print_str += f'{tab}{self.english_translation}'
        return print_str

    @classmethod
    def from_dict(cls, item_dict: dict) -> ExampleSentence:
        return ExampleSentence(
            japanese_sentence=JapaneseSentence.from_dict_list(item_dict['japanese_sentence']),
            english_translation=item_dict['english_translation']
        )

class ExampleSentenceList(
    BasicLoadableHandler['ExampleSentenceList', 'ExampleSentence'],
    BasicHandler['ExampleSentenceList', 'ExampleSentence']
):
    def __init__(self, sentences: List[ExampleSentence]=None):
        super().__init__(obj_type=ExampleSentence, obj_list=sentences)
        self.sentences = self.obj_list
    
    def custom_str(self, indent: int=0) -> str:
        print_str = ''
        for i, sentence in enumerate(self):
            if i == 0:
                print_str += f'{sentence.custom_str(indent=indent)}'
            else:
                print_str += f'\n{sentence.custom_str(indent=indent)}'

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> ExampleSentenceList:
        return ExampleSentenceList([ExampleSentence.from_dict(item_dict) for item_dict in dict_list])

class ConceptLabels(BasicLoadableObject['ConceptLabels']):
    def __init__(
        self, is_common: bool=False,
        jlpt_level: int=None,
        wanikani_level: int=None
    ):
        super().__init__()
        self.is_common = is_common
        self.jlpt_level = jlpt_level
        self.wanikani_level = wanikani_level

    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        tab1 = '\t' * (indent + 1)
        print_str = f'{tab}Concept Labels:'
        print_str += f'\n{tab1}'
        first = True
        if self.is_common:
            if first:
                print_str += f'Common'
                first = False
            else:
                print_str += f', Common'
        if self.is_jlpt:
            if first:
                print_str += f'JLPT N{self.jlpt_level}'
                first = False
            else:
                print_str += f', JLPT N{self.jlpt_level}'
        if self.is_wanikani:
            if first:
                print_str += f'Wanikani Level {self.wanikani_level}'
                first = False
            else:
                print_str += f', Wanikani Level {self.wanikani_level}'
        return print_str

    @property
    def is_jlpt(self) -> bool:
        return self.jlpt_level is not None
    
    @property
    def is_wanikani(self) -> bool:
        return self.wanikani_level is not None
    
    @property
    def has_label(self) -> bool:
        return self.is_common or self.is_jlpt or self.is_wanikani

class SupplementaryLinks(BasicLoadableObject['SupplementaryLinks']):
    def __init__(
        self, audio_links: LinkList=None,
        collocation_links: LinkList=None,
        other_links: LinkList=None
    ):
        super().__init__()
        self.audio_links = audio_links if audio_links is not None else LinkList()
        self.collocation_links = collocation_links if collocation_links is not None else LinkList()
        self.other_links = other_links if other_links is not None else LinkList()
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> SupplementaryLinks:
        return SupplementaryLinks(
            audio_links=LinkList.from_dict_list(item_dict['audio_links']) if item_dict['audio_links'] is not None else None,
            collocation_links=LinkList.from_dict_list(item_dict['collocation_links']) if item_dict['collocation_links'] is not None else None,
            other_links=LinkList.from_dict_list(item_dict['other_links']) if item_dict['other_links'] is not None else None
        )

    @property
    def has_audio_links(self) -> bool:
        return len(self.audio_links) > 0
    
    @property
    def has_collocation_links(self) -> bool:
        return len(self.collocation_links) > 0
    
    @property
    def has_other_links(self) -> bool:
        return len(self.other_links) > 0

class PlainText(BasicLoadableObject['PlainText']):
    def __init__(self, text: str, tag: str):
        super().__init__()
        self.text = text
        self.tag = tag
    
    def __str__(self) -> str:
        return f'{self.text} *{self.tag}*'
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        return f'{tab}{self.text}'

class PlainTextWithLink(BasicLoadableObject['PlainTextWithLink']):
    def __init__(self, text: str, link: Link, tag: str):
        super().__init__()
        self.text = text
        self.link = link
        self.tag = tag
    
    def __str__(self) -> str:
        return f'{self.text}[{self.link.text}]({self.link.url}) *{self.tag}*'

    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}{self.text}[{self.link.text}]'
        return print_str

    @classmethod
    def from_dict(cls, item_dict: dict) -> PlainTextWithLink:
        return PlainTextWithLink(
            text=item_dict['text'],
            link=Link.from_dict(item_dict['link']),
            tag=item_dict['tag']
        )

class SupplementalInfo(BasicLoadableObject['SupplementalInfo']):
    def __init__(self, part_list: List[Any]):
        for part in part_list:
            assert type(part) in [PlainText, PlainTextWithLink]
        self.part_list = part_list
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}'
        for i, part in enumerate(self.part_list):
            if i == 0:
                print_str += part.custom_str(indent=0)
            else:
                print_str += f', {part.custom_str(indent=0)}'
        return print_str

    @property
    def tag(self) -> PlainText:
        for part in self.part_list:
            if part.tag == 'tag':
                return part
        return None
    
    @property
    def has_tag(self) -> bool:
        return self.tag is not None

    @property
    def info(self) -> PlainText:
        for part in self.part_list:
            if part.tag == 'info':
                return part
        return None

    @property
    def has_info(self) -> bool:
        return self.info is not None

    @property
    def restriction(self) -> PlainText:
        for part in self.part_list:
            if part.tag == 'restriction':
                return part
        return None
    
    @property
    def has_restriction(self) -> bool:
        return self.restriction is not None

    @property
    def see_also(self) -> PlainTextWithLink:
        for part in self.part_list:
            if part.tag == 'see_also':
                return part
        return None
    
    @property
    def has_see_also(self) -> bool:
        return self.see_also is not None

    @property
    def antonym(self) -> PlainTextWithLink:
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
                part_list.append(PlainText.from_dict(item_dict))
            elif set(list(item_dict.keys())) == set(['text', 'link', 'tag']):
                part_list.append(PlainTextWithLink.from_dict(item_dict))
            else:
                raise TypeError(f'Could not resolve the specific SupplementalInfoStructs type from the following item_dict:\n{item_dict}')
        return SupplementalInfo(part_list)

class MeaningTags(BasicLoadableObject['MeaningTags']):
    def __init__(self, meaning_tag_text: str):
        self.meaning_tag_text = meaning_tag_text

    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}{self.meaning_tag_text}'
        return print_str

    # Part Related
    @property
    def tag_parts(self) -> List[MeaningTags]:
        return [MeaningTags(part_str) for part_str in self.meaning_tag_text.split(', ')]

    @property
    def num_parts(self) -> int:
        return len(self.tag_parts)

    # Unique
    @property
    def is_other_forms(self) -> bool:
        return self.meaning_tag_text == 'Other forms'
    
    @property
    def is_notes(self) -> bool:
        return self.meaning_tag_text == 'Notes'
    
    # Basic
    @property
    def is_suffix(self) -> bool:
        return 'Suffix' in self.meaning_tag_text
    
    @property
    def is_prefix(self) -> bool:
        return 'Prefix' in self.meaning_tag_text

    @property
    def is_conjunction(self) -> bool:
        return 'Conjunction' in self.meaning_tag_text

    @property
    def is_particle(self) -> bool:
        return 'Particle' in self.meaning_tag_text

    @property
    def is_auxiliary(self) -> bool:
        return 'Auxiliary' in self.meaning_tag_text

    @property
    def is_counter(self) -> bool:
        return 'Counter' in self.meaning_tag_text
    
    @property
    def is_place(self) -> bool:
        return 'Place' in self.meaning_tag_text

    @property
    def is_expression(self) -> bool:
        return 'Expression' in self.meaning_tag_text

    @property
    def is_full_name(self) -> bool:
        return 'Full name' in self.meaning_tag_text
    
    @property
    def is_organization(self) -> bool:
        return 'Organization' in self.meaning_tag_text

    @property
    def is_company(self) -> bool:
        return 'Company' in self.meaning_tag_text
    
    @property
    def is_train_station(self) -> bool:
        return 'Train station' in self.meaning_tag_text

    @property
    def is_wikipedia_definition(self) -> bool:
        return 'Wikipedia definition' in self.meaning_tag_text

    @property
    def is_numeric(self) -> bool:
        return 'Numeric' in self.meaning_tag_text

    @property
    def is_unclassified(self) -> bool:
        return 'Unclassified' in self.meaning_tag_text

    @property
    def is_not_tagged(self) -> bool:
        return 'No Meaning Tag' in self.meaning_tag_text

    # Noun Subcategories
    @property
    def is_noun(self) -> bool:
        return 'Noun' in self.meaning_tag_text

    @property
    def is_noun_used_as_suffix(self) -> bool:
        return 'Noun - used as a suffix' in self.meaning_tag_text
    
    @property
    def is_noun_used_as_prefix(self) -> bool:
        return 'Noun - used as a prefix' in self.meaning_tag_text
    
    @property
    def is_adverbial_noun(self) -> bool:
        return 'Adverbial noun' in self.meaning_tag_text
    
    @property
    def is_temporal_noun(self) -> bool:
        return 'Temporal noun' in self.meaning_tag_text

    @property
    def is_pronoun(self) -> bool:
        return 'Pronoun' in self.meaning_tag_text

    # Verb Subcategories
    @property
    def is_suru_verb(self) -> bool:
        return 'Suru verb' in self.meaning_tag_text
    
    @property
    def is_suru_verb_irregular(self) -> bool:
        return 'Suru verb - irregular' in self.meaning_tag_text

    @property
    def is_suru_verb_special_class(self) -> bool:
        return 'Suru verb - special class' in self.meaning_tag_text

    @property
    def is_su_verb_precursor_to_modern_suru(self) -> bool:
        return 'Su verb - precursor to the modern suru' in self.meaning_tag_text

    @property
    def is_kuru_verb_special_class(self) -> bool:
        return 'Kuru verb - special class' in self.meaning_tag_text

    @property
    def is_ichidan_verb(self) -> bool:
        return 'Ichidan verb' in self.meaning_tag_text

    @property
    def is_transitive_verb(self) -> bool:
        return 'Transitive verb' in self.meaning_tag_text

    @property
    def is_intransitive_verb(self) -> bool:
        return 'intransitive verb' in self.meaning_tag_text

    @property
    def is_auxiliary_verb(self) -> bool:
        return 'Auxiliary verb' in self.meaning_tag_text

    @property
    def is_godan_verb_with_bu_ending(self) -> bool:
        return 'Godan verb with bu ending' in self.meaning_tag_text

    @property
    def is_godan_verb_with_ru_ending(self) -> bool:
        return 'Godan verb with ru ending' in self.meaning_tag_text

    @property
    def is_godan_verb_with_ru_ending_irregular(self) -> bool:
        return 'Godan verb with ru ending (irregular verb)' in self.meaning_tag_text

    @property
    def is_godan_verb_with_su_ending(self) -> bool:
        return 'Godan verb with su ending' in self.meaning_tag_text

    @property
    def is_godan_verb_with_ku_ending(self) -> bool:
        return 'Godan verb with ku ending' in self.meaning_tag_text

    @property
    def is_godan_verb_with_mu_ending(self) -> bool:
        return 'Godan verb with mu ending' in self.meaning_tag_text
    
    @property
    def is_godan_verb_with_u_ending(self) -> bool:
        return 'Godan verb with u ending' in self.meaning_tag_text

    @property
    def is_godan_verb_with_u_ending_special_class(self) -> bool:
        return 'Godan verb with u ending (special class)' in self.meaning_tag_text

    @property
    def is_godan_verb_with_tsu_ending(self) -> bool:
        return 'Godan verb with tsu ending' in self.meaning_tag_text

    @property
    def is_godan_verb_with_gu_ending(self) -> bool:
        return 'Godan verb with gu ending' in self.meaning_tag_text

    @property
    def is_godan_verb_iku_yuku_special_class(self) -> bool:
        return 'Godan verb - Iku/Yuku special class' in self.meaning_tag_text

    @property
    def is_godan_verb_with_nu_ending(self) -> bool:
        return 'Godan verb with nu ending' in self.meaning_tag_text

    @property
    def is_godan_verb_aru_special_class(self) -> bool:
        return 'Godan verb - aru special class' in self.meaning_tag_text

    @property
    def is_ichidan_verb_zuru_verb_alternative_form_of_jiru_verbs(self) -> bool:
        return 'Ichidan verb - zuru verb (alternative form of -jiru verbs)' in self.meaning_tag_text

    @property
    def is_nidan_verb_upper_class_with_tsu_ending_archaic(self) -> bool:
        return 'Nidan verb (upper class) with tsu ending (archaic)' in self.meaning_tag_text

    @property
    def is_nidan_verb_lower_class_with_yu_ending_archaic(self) -> bool:
        return 'Nidan verb (lower class) with yu ending (archaic)' in self.meaning_tag_text

    @property
    def is_yodan_verb_with_hu_fu_ending_archaic(self) -> bool:
        return 'Yodan verb with hu/fu ending (archaic)' in self.meaning_tag_text

    @property
    def is_yodan_verb_with_ru_ending_archaic(self) -> bool:
        return 'Yodan verb with ru ending (archaic)' in self.meaning_tag_text

    @property
    def is_yodan_verb_with_ku_ending_archaic(self) -> bool:
        return 'Yodan verb with ku ending (archaic)' in self.meaning_tag_text

    @property
    def is_irregular_nu_verb(self) -> bool:
        return 'Irregular nu verb' in self.meaning_tag_text

    # Adverb Subcategories
    @property
    def is_adverb(self) -> bool:
        return 'Adverb' in self.meaning_tag_text
    
    @property
    def is_adverb_taking_to_particle(self) -> bool:
        return "Adverb taking the 'to' particle" in self.meaning_tag_text

    # Adjective Subcategories
    @property
    def is_no_adjective(self) -> bool:
        return 'No-adjective' in self.meaning_tag_text

    @property
    def is_na_adjective(self) -> bool:
        return 'Na-adjective' in self.meaning_tag_text

    @property
    def is_archaic_formal_form_of_na_adjective(self) -> bool:
        return 'Archaic/formal form of na-adjective' in self.meaning_tag_text

    @property
    def is_i_adjective(self) -> bool:
        return 'I-adjective' in self.meaning_tag_text

    @property
    def is_i_adjective_yoi_ii_class(self) -> bool:
        return 'I-adjective (yoi/ii class)' in self.meaning_tag_text

    @property
    def is_taru_adjective(self) -> bool:
        return 'Taru-adjective' in self.meaning_tag_text

    @property
    def is_shiku_adjective_archaic(self) -> bool:
        return 'Shiku adjective (archaic)' in self.meaning_tag_text

    # Other
    @property
    def noun_or_verb_acting_prenominally(self) -> bool:
        return 'Noun or verb acting prenominally' in self.meaning_tag_text

    @property
    def is_prenoun_adjectival(self) -> bool:
        return 'Pre-noun adjectival' in self.meaning_tag_text

    # Known/Unknown Tag Verification
    @property
    def known_tags_dict(self) -> dict:
        return {
            'Other forms': 'is_other_forms',
            'Notes': 'is_notes',
            'Suffix': 'is_suffix',
            'Prefix': 'is_prefix',
            'Conjunction': 'is_conjunction',
            'Particle': 'is_particle',
            'Auxiliary': 'is_auxiliary',
            'Counter': 'is_counter',
            'Place': 'is_place',
            'Expression': 'is_expression',
            'Full name': 'is_full_name',
            'Organization': 'is_organization',
            'Company': 'is_company',
            'Train station': 'is_train_station',
            'Wikipedia definition': 'is_wikipedia_definition',
            'Numeric': 'is_numeric',
            'Unclassified': 'is_unclassified',
            'No Meaning Tag': 'is_not_tagged',
            'Noun': 'is_noun',
            'Noun - used as a suffix': 'is_noun_used_as_suffix',
            'Noun - used as a prefix': 'is_noun_used_as_prefix',
            'Adverbial noun': 'is_adverbial_noun',
            'Temporal noun': 'is_temporal_noun',
            'Pronoun': 'is_pronoun',
            'Suru verb': 'is_suru_verb',
            'Suru verb - irregular': 'is_suru_verb_irregular',
            'Suru verb - special class': 'is_suru_verb_special_class',
            'Su verb - precursor to the modern suru': 'is_su_verb_precursor_to_modern_suru',
            'Kuru verb - special class': 'is_kuru_verb_special_class',
            'Ichidan verb': 'is_ichidan_verb',
            'Transitive verb': 'is_transitive_verb',
            'intransitive verb': 'is_intransitive_verb',
            'Auxiliary verb': 'is_auxiliary_verb',
            'Godan verb with bu ending': 'is_godan_verb_with_bu_ending',
            'Godan verb with ru ending': 'is_godan_verb_with_ru_ending',
            'Godan verb with ru ending (irregular verb)': 'is_godan_verb_with_ru_ending_irregular',
            'Godan verb with su ending': 'is_godan_verb_with_su_ending',
            'Godan verb with ku ending': 'is_godan_verb_with_ku_ending',
            'Godan verb with mu ending': 'is_godan_verb_with_mu_ending',
            'Godan verb with u ending': 'is_godan_verb_with_u_ending',
            'Godan verb with u ending (special class)': 'is_godan_verb_with_u_ending_special_class',
            'Godan verb with tsu ending': 'is_godan_verb_with_tsu_ending',
            'Godan verb with gu ending': 'is_godan_verb_with_gu_ending',
            'Godan verb - Iku/Yuku special class': 'is_godan_verb_iku_yuku_special_class',
            'Godan verb with nu ending': 'is_godan_verb_with_nu_ending',
            'Godan verb - aru special class': 'is_godan_verb_aru_special_class',
            'Ichidan verb - zuru verb (alternative form of -jiru verbs)': 'is_ichidan_verb_zuru_verb_alternative_form_of_jiru_verbs',
            'Nidan verb (upper class) with tsu ending (archaic)': 'is_nidan_verb_upper_class_with_tsu_ending_archaic',
            'Nidan verb (lower class) with yu ending (archaic)': 'is_nidan_verb_lower_class_with_yu_ending_archaic',
            'Yodan verb with hu/fu ending (archaic)': 'is_yodan_verb_with_hu_fu_ending_archaic',
            'Yodan verb with ru ending (archaic)': 'is_yodan_verb_with_ru_ending_archaic',
            'Yodan verb with ku ending (archaic)': 'is_yodan_verb_with_ku_ending_archaic',
            'Irregular nu verb': 'is_irregular_nu_verb',
            'Adverb': 'is_adverb',
            "Adverb taking the 'to' particle": 'is_adverb_taking_to_particle',
            'No-adjective': 'is_no_adjective',
            'Na-adjective': 'is_na_adjective',
            'Archaic/formal form of na-adjective': 'is_archaic_formal_form_of_na_adjective',
            'I-adjective': 'is_i_adjective',
            'I-adjective (yoi/ii class)': 'is_i_adjective_yoi_ii_class',
            'Taru-adjective': 'is_taru_adjective',
            'Shiku adjective (archaic)': 'is_shiku_adjective_archaic',
            'Noun or verb acting prenominally': 'noun_or_verb_acting_prenominally',
            'Pre-noun adjectival': 'is_prenoun_adjectival'
        }

    def verify_known_tag_methods(self, raise_exception_on_fail: bool=True):
        for tag_str, property_str in self.known_tags_dict.items():
            property_names = [p for p in dir(type(self)) if isinstance(getattr(type(self), p), property)]
            if property_str not in property_names:
                message = f"""
                '{property_str}' from MeaningTags.known_tags_dict
                couldn't be found in the properties of MeaningTags.
                Please add/fix the property.
                """
                if raise_exception_on_fail:
                    raise Exception(message)
                else:
                    print(message)
            if not getattr(MeaningTags(tag_str), property_str):
                message = f"""
                known_tags_dict['{tag_str}'] = '{property_str}'
                is registered, but MeaningTags({tag_str}).{property_str}
                returned False.
                Please check/fix the definition of MeaningTags.{property_str}
                """
                if raise_exception_on_fail:
                    raise Exception(message)
                else:
                    print(message)
    
    def verify_is_known_tag(self, raise_exception_on_fail: bool=False):
        for tag in self.tag_parts:
            if tag.meaning_tag_text not in self.known_tags_dict.keys():
                message = f"""
                '{tag.meaning_tag_text}' not found in MeaningTags.known_tags_dict.keys()
                Either a property hasn't been implemented for '{tag.meaning_tag_text}' yet
                or MeaningTags.known_tags_dict.keys() is out-of-date.
                Please fix.
                """
                if raise_exception_on_fail:
                    raise Exception(message)
                else:
                    print(message)
            elif not getattr(tag, self.known_tags_dict[tag.meaning_tag_text]):
                message = f"""
                Found '{tag.meaning_tag_text}' in MeaningTags.known_tags_dict.keys(),
                which corresponds to MeaningTags.{self.known_tags_dict[tag.meaning_tag_text]},
                but MeaningTags('{tag.meaning_tag_text}').{self.known_tags_dict[tag.meaning_tag_text]} returned False.
                Please check/fix the definition of MeaningTags.{self.known_tags_dict[tag.meaning_tag_text]}
                """

    @property
    def contains_unknown_tag(self) -> bool:
        for tag in self.tag_parts:
            if tag.meaning_tag_text not in self.known_tags_dict.keys():
                return True
        return False
    
    @property
    def unknown_tag_parts(self) -> List[MeaningTags]:
        return [tag for tag in self.tag_parts if tag.meaning_tag_text not in self.known_tags_dict.keys()]

class MeaningWrapper(BasicLoadableObject['MeaningWrapper']):
    def __init__(
        self,
        section_divider_text: str=None, meaning_text: str=None,
        supplemental_info: SupplementalInfo=None,
        meaning_abstract_text: str=None, meaning_abstract_link: Link=None,
        sentences: ExampleSentenceList=None
    ):
        self.section_divider_text = section_divider_text
        self.meaning_text = meaning_text
        self.supplemental_info = supplemental_info
        self.meaning_abstract_text = meaning_abstract_text
        self.meaning_abstract_link = meaning_abstract_link
        self.sentences = sentences
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}'
        if self.section_divider_text is not None:
            print_str += f'{self.section_divider_text} '
        if self.meaning_text is not None:
            print_str += f'{self.meaning_text}'
        if self.supplemental_info is not None:
            print_str += f' [{self.supplemental_info.custom_str(indent=0)}]'
        if self.meaning_abstract_text is not None or self.meaning_abstract_link is not None:
            if self.meaning_abstract_text is not None and self.meaning_abstract_link is not None:
                print_str += f' [{self.meaning_abstract_text} ({self.meaning_abstract_link.text})]'
            elif self.meaning_abstract_text is not None and self.meaning_abstract_link is None:
                print_str += f' [{self.meaning_abstract_text}]'
            elif self.meaning_abstract_text is None and self.meaning_abstract_link is not None:
                print_str += f' [({self.meaning_abstract_link.text})]'
            else:
                raise Exception
        if self.sentences is not None:
            print_str += f'\n{self.sentences.custom_str(indent=indent)}'
        return print_str

    @classmethod
    def from_dict(cls, item_dict: dict) -> MeaningWrapper:
        return MeaningWrapper(
            section_divider_text=item_dict['section_divider_text'] if item_dict['section_divider_text'] is not None else None,
            meaning_text=item_dict['meaning_text'] if item_dict['meaning_text'] is not None else None,
            supplemental_info=SupplementalInfo.from_dict_list(item_dict['supplemental_info']) if item_dict['supplemental_info'] is not None else None,
            meaning_abstract_text=item_dict['meaning_abstract_text'] if item_dict['meaning_abstract_text'] is not None else None,
            meaning_abstract_link=Link.from_dict(item_dict['meaning_abstract_link']) if item_dict['meaning_abstract_link'] is not None else None,
            sentences=ExampleSentenceList.from_dict_list(item_dict['sentences']) if item_dict['sentences'] is not None else None
        )

    @property
    def has_section_divider(self) -> bool:
        return self.section_divider_text is not None
    
    @property
    def has_meaning(self) -> bool:
        return self.meaning_text is not None
    
    @property
    def has_supplemental_info(self) -> bool:
        return self.supplemental_info is not None
    
    @property
    def has_meaning_abstract(self) -> bool:
        return self.meaning_abstract_text is not None
    
    @property
    def has_meaning_abstract_link(self) -> bool:
        return self.meaning_abstract_link is not None
    
    @property
    def has_sentences(self) -> bool:
        return self.sentences is not None

class MeaningWrapperHandler(
    BasicLoadableHandler['MeaningWrapperHandler', 'MeaningWrapper'],
    BasicHandler['MeaningWrapperHandler', 'MeaningWrapper']
):
    def __init__(self, wrapper_list: List[MeaningWrapper]=None):
        super().__init__(obj_type=MeaningWrapper, obj_list=wrapper_list)
        self.wrapper_list = self.obj_list

    def custom_str(self, indent: int=0) -> str:
        print_str = ''
        for i, wrapper in enumerate(self):
            if i == 0:
                print_str += f'{wrapper.custom_str(indent=indent)}'
            else:
                print_str += f'\n{wrapper.custom_str(indent=indent)}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> MeaningWrapperHandler:
        return MeaningWrapperHandler([MeaningWrapper.from_dict(item_dict) for item_dict in dict_list])

class MeaningGroup(BasicLoadableObject['MeaningGroup']):
    def __init__(self, meaning_tags: MeaningTags, meaning_list: MeaningWrapperHandler=None):
        self.meaning_tags = meaning_tags
        self.meaning_list = meaning_list if meaning_list is not None else MeaningWrapperHandler()

    def custom_str(self, indent: int=0) -> str:
        print_str = ''
        print_str += f'{self.meaning_tags.custom_str(indent=indent)}'
        print_str += f'\n{self.meaning_list.custom_str(indent=indent+1)}'
        return print_str

    @classmethod
    def from_dict(cls, item_dict: dict) -> MeaningGroup:
        return MeaningGroup(
            meaning_tags=MeaningTags.from_dict(item_dict['meaning_tags']),
            meaning_list=MeaningWrapperHandler.from_dict_list(item_dict['meaning_list']) if item_dict['meaning_list'] is not None else None
        )

class MeaningGroupHandler(
    BasicLoadableHandler['MeaningGroupHandler', 'MeaningGroup'],
    BasicHandler['MeaningGroupHandler', 'MeaningGroup']
):
    def __init__(self, groups: List[MeaningGroup]=None):
        super().__init__(obj_type=MeaningGroup, obj_list=groups)
        self.groups = self.obj_list

    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}Meanings:'
        for i, group in enumerate(self):
            print_str += f'\n{group.custom_str(indent=indent+1)}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> MeaningGroupHandler:
        return MeaningGroupHandler([MeaningGroup.from_dict(item_dict) for item_dict in dict_list])

class OtherForm(BasicLoadableObject['OtherForm']):
    def __init__(self, writing: str, reading: str=None):
        super().__init__()
        self.writing = writing
        self.reading = reading

    def __str__(self) -> str:
        if self.reading is not None:
            return f'{self.writing} 【{self.reading}】'
        else:
            return self.writing
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        return f'{tab}{self.__str__()}'

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

    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}Other forms'
        print_str += f'\n{tab}{self.__str__()}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> OtherFormList:
        return OtherFormList([OtherForm.from_dict(item_dict) for item_dict in dict_list])

class Note(BasicLoadableObject['Note']):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}{self.text}'
        return print_str

class NoteList(
    BasicLoadableHandler['NoteList', 'Note'],
    BasicHandler['NoteList', 'Note']
):
    def __init__(self, notes: List[Note]=None):
        super().__init__(obj_type=Note, obj_list=notes)
        self.notes = self.obj_list
    
    def custom_str(self, indent: int=0) -> str:
        print_str = 'Notes'
        for note in self:
            print_str += f'\n{note.custom_str(indent=indent)}'

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> NoteList:
        return NoteList([Note.from_dict(item_dict) for item_dict in dict_list])

class MeaningSection(BasicLoadableObject['MeaningSection']):
    def __init__(self, meaning_groups: MeaningGroupHandler, other_forms: OtherFormList=None, notes: NoteList=None):
        super().__init__()
        self.meaning_groups = meaning_groups
        self.other_forms = other_forms
        self.notes = notes

    def custom_str(self, indent: int=0) -> str:
        print_str = f'{self.meaning_groups.custom_str(indent=indent)}'
        if self.has_other_forms:
            print_str += f'\n{self.other_forms.custom_str(indent=indent)}'
        if self.has_notes:
            print_str += f'\n{self.notes.custom_str(indent=indent)}'
        return print_str

    @classmethod
    def from_dict(cls, item_dict: dict) -> MeaningSection:
        return MeaningSection(
            meaning_groups=MeaningGroupHandler.from_dict_list(item_dict['meaning_groups']),
            other_forms=OtherFormList.from_dict_list(item_dict['other_forms']) if item_dict['other_forms'] is not None else None,
            notes=NoteList.from_dict_list(item_dict['notes']) if item_dict['notes'] is not None else None
        )

    @property
    def has_other_forms(self) -> bool:
        return self.other_forms is not None
    
    @property
    def has_notes(self) -> bool:
        return self.notes is not None

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

    def construct_group_handler(self) -> MeaningGroupHandler:
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

    def construct_meaning_section(self) -> MeaningSection:
        return MeaningSection(
            meaning_groups=self.construct_group_handler(),
            other_forms=self.other_forms,
            notes=self.notes
        )

    def print_parts(self):
        for part in self.meaning_part_list:
            if isinstance(part, MeaningTags):
                logger.purple(part)
            elif isinstance(part, MeaningWrapper):
                logger.white(part)
            else:
                raise Exception
    
    def summarize(self):
        groups = self.construct_group_handler()
        for group in groups:
            logger.blue('================')
            for meaning in group.meaning_list:
                if meaning.sentences is not None:
                    logger.purple(f'meaning.sentences[0].japanese_sentence.writing: {meaning.sentences[0].japanese_sentence.writing}')
                    logger.purple(f'meaning.sentences[0].japanese_sentence.reading: {meaning.sentences[0].japanese_sentence.reading}')
        logger.blue(f'self.other_forms: {self.other_forms}')
        logger.blue(f'self.notes: {self.notes}')

class DictionaryEntry(BasicLoadableObject['DictionaryEntry']):
    def __init__(
        self, word_representation: WordRepresentation, concept_labels: ConceptLabels,
        supplementary_links: SupplementaryLinks, meaning_section: MeaningSection
    ):
        super().__init__()
        self.word_representation = word_representation
        self.concept_labels = concept_labels
        self.supplementary_links = supplementary_links
        self.meaning_section = meaning_section

    def custom_str(self, indent: int=0) -> str:
        print_str = f'{self.word_representation.custom_str(indent=indent)}'
        if self.concept_labels.has_label:
            print_str += f'\n{self.concept_labels.custom_str(indent=indent)}'
        print_str += f'\n{self.meaning_section.custom_str(indent=indent)}'
        return print_str

    @classmethod
    def from_dict(cls, item_dict: dict) -> DictionaryEntry:
        return DictionaryEntry(
            word_representation=WordRepresentation.from_dict(item_dict['word_representation']),
            concept_labels=ConceptLabels.from_dict(item_dict['concept_labels']),
            supplementary_links=SupplementaryLinks.from_dict(item_dict['supplementary_links']),
            meaning_section=MeaningSection.from_dict(item_dict['meaning_section'])
        )
    
    def same_entry_as(self, other, strict: bool=True) -> bool:
        if isinstance(other, DictionaryEntry):
            if strict:
                return self == other
            else:
                same_wr = self.word_representation == other.word_representation
                same_other_forms = self.meaning_section.other_forms == other.meaning_section.other_forms
                same_meaning_len = len(self.meaning_section.meaning_groups) == len(other.meaning_section.meaning_groups)
                return same_wr and same_other_forms and same_meaning_len
        else:
            return NotImplemented

class DictionaryEntryList(
    BasicLoadableHandler['DictionaryEntryList', 'DictionaryEntry'],
    BasicHandler['DictionaryEntryList', 'DictionaryEntry']
):
    def __init__(self, entry_list: List[DictionaryEntry]=None):
        super().__init__(obj_type=DictionaryEntry, obj_list=entry_list)
        self.entry_list = self.obj_list
    
    def custom_str(self, indent: int=0) -> str:
        print_str = ''
        for i, entry in enumerate(self):
            if i == 0:
                print_str += f'{entry.custom_str(indent=indent)}'
            else:
                print_str += f'\n\n{entry.custom_str(indent=indent)}'
        return print_str

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> DictionaryEntryList:
        return DictionaryEntryList([DictionaryEntry.from_dict(item_dict) for item_dict in dict_list])

    def contains_same_entry_as(self, other, strict: bool=True) -> bool:
        if isinstance(other, DictionaryEntry):
            if strict:
                return other in self
            else:
                for entry in self:
                    if entry.same_entry_as(other=other, strict=strict):
                        return True
                return False
        else:
            return NotImplemented

class GrammarBreakdown(BasicLoadableObject['GrammarBreakdown']):
    def __init__(self, dictionary_version_link: Link, explanation: str, form_text_list: List[str]):
        super().__init__()
        self.dictionary_version_link = dictionary_version_link
        self.explanation = explanation
        self.form_text_list = form_text_list

    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        tab1 = '\t' * (indent + 1)
        print_str = f'{tab}{self.explanation}'
        for form_text in self.form_text_list:
            print_str += f'\n{tab1}{form_text}'
        return print_str

    @classmethod
    def from_dict(cls, item_dict: dict) -> GrammarBreakdown:
        return GrammarBreakdown(
            dictionary_version_link=Link.from_dict(item_dict['dictionary_version_link']),
            explanation=item_dict['explanation'],
            form_text_list=item_dict['form_text_list']
        )

class NumberConversion(BasicLoadableObject['NumberConversion']):
    def __init__(self, japanese_number_text: str, converted_number_text: str):
        super().__init__()
        self.japanese_number_text = japanese_number_text
        self.converted_number_text = converted_number_text
    
    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        return f'{tab}{self.japanese_number_text} is {self.converted_number_text}'

class ResultArea(BasicLoadableObject['ResultArea']):
    def __init__(self, grammar_breakdown: GrammarBreakdown=None, number_conversion: NumberConversion=None):
        super().__init__()
        self.grammar_breakdown = grammar_breakdown
        self.number_conversion = number_conversion
    
    def custom_str(self, indent: int=0) -> str:
        new_line_char = ''
        print_str = ''
        if self.has_grammar_breakdown:
            print_str += f'{new_line_char}{self.grammar_breakdown.custom_str(indent=indent)}'
            new_line_char = '\n'
        if self.has_number_conversion:
            print_str += f'{new_line_char}{self.number_conversion.custom_str(indent=indent)}'
            new_line_char = '\n'
        return print_str

    @property
    def has_grammar_breakdown(self) -> bool:
        return self.grammar_breakdown is not None

    @property
    def has_number_conversion(self) -> bool:
        return self.number_conversion is not None

    @property
    def is_empty(self) -> bool:
        return not self.has_grammar_breakdown and not self.has_number_conversion

    def to_dict(self) -> dict:
        result = {}
        if self.has_grammar_breakdown:
            result['grammar_breakdown'] = self.grammar_breakdown.to_dict()
        if self.has_number_conversion:
            result['number_conversion'] = self.number_conversion.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> ResultArea:
        return ResultArea(
            grammar_breakdown=GrammarBreakdown.from_dict(item_dict['grammar_breakdown']) if 'grammar_breakdown' in item_dict else None,
            number_conversion=NumberConversion.from_dict(item_dict['number_conversion']) if 'number_conversion' in item_dict else None
        )

class JishoSearchQuery(BasicLoadableObject['JishoSearchQuery']):
    def __init__(
        self, url: str, title: str, result_count: int,
        exact_matches: DictionaryEntryList, nonexact_matches: DictionaryEntryList,
        result_area: ResultArea=None, more_words_link: Link=None,
        history_group_id: int=None
    ):
        super().__init__()
        self.url = url
        self.title = title
        self.result_count = result_count
        self.exact_matches = exact_matches
        self.nonexact_matches = nonexact_matches
        self.result_area = result_area
        self.more_words_link = more_words_link
        self.history_group_id = history_group_id

    def custom_str(self, indent: int=0) -> str:
        tab = '\t' * indent
        print_str = f'{tab}URL: {self.url}'
        print_str += f'\n{tab}Title: {self.title}'
        print_str += f'\n{tab}Result Count: {self.result_count}'
        if len(self.exact_matches) > 0:
            print_str += f'\n{tab}Exact Matches:'
            print_str += f'\n{self.exact_matches.custom_str(indent=indent+1)}'
        if len(self.nonexact_matches) > 0:
            print_str += f'\n{tab}Non-Exact Matches:'
            print_str += f'\n{self.nonexact_matches.custom_str(indent=indent+1)}'
        if self.result_area is not None and not self.result_area.is_empty:
            print_str += f'\n{tab}Result Area:'
            print_str += f'\n{self.result_area.custom_str(indent=indent+1)}'
        if self.more_words_link is not None:
            print_str += f'\n{tab}More Words: {self.more_words_link.__str__()}'
        return print_str

    @property
    def simple_str(self) -> str:
        return self.custom_str(indent=0)

    @classmethod
    def from_dict(cls, item_dict: dict) -> JishoSearchQuery:
        return JishoSearchQuery(
            url=item_dict['url'],
            title=item_dict['title'],
            result_count=item_dict['result_count'],
            exact_matches=DictionaryEntryList.from_dict_list(item_dict['exact_matches']),
            nonexact_matches=DictionaryEntryList.from_dict_list(item_dict['nonexact_matches']),
            result_area=ResultArea.from_dict(item_dict['result_area']) if 'result_area' in item_dict and item_dict['result_area'] is not None else None,
            more_words_link=Link.from_dict(item_dict['more_words_link']) if item_dict['more_words_link'] is not None else None,
            history_group_id=item_dict['history_group_id'] if 'history_group_id' in item_dict else None
        )

    @property
    def has_matches(self) -> bool:
        return self.result_count > 0

    @property
    def has_more_words_link(self) -> bool:
        return self.more_words_link is not None

    @property
    def matches(self) -> DictionaryEntryList:
        return self.exact_matches + self.nonexact_matches

class JishoSearchQueryHandler(
    BasicLoadableHandler['JishoSearchQueryHandler', 'JishoSearchQuery'],
    BasicHandler['JishoSearchQueryHandler', 'JishoSearchQuery']
):
    def __init__(self, query_list: List[JishoSearchQuery]=None):
        super().__init__(obj_type=JishoSearchQuery, obj_list=query_list)
        self.query_list = self.obj_list
    
    def custom_str(self, indent: int=0) -> str:
        print_str = ''
        for i, query in enumerate(self):
            if i == 0:
                print_str += f'{query.custom_str(indent=indent)}'
            else:
                print_str += f'\n\n{query.custom_str(indent=indent)}'
        return print_str

    @property
    def simple_str(self) -> str:
        return self.custom_str(indent=0)

    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> JishoSearchQueryHandler:
        return JishoSearchQueryHandler([JishoSearchQuery.from_dict(item_dict) for item_dict in dict_list])

class JishoSearchHtmlParser:
    def __init__(self, url: str):
        assert url.startswith('https://jisho.org/search/')
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
        encoded_search_word = self.url.replace('https://jisho.org/search/', '')
        decoded_search_word = urllib.parse.unquote(encoded_search_word)
        return decoded_search_word

    @classmethod
    def from_search_word(cls, search_word: str) -> JishoSearchHtmlParser:
        search_url = f'https://jisho.org/search/{search_word}'
        return JishoSearchHtmlParser(url=search_url)

    def parse(self, history_group_id: int=None) -> JishoSearchQuery:
        main_results_html = self._soup.find(name='div', attrs={'id': 'main_results'})
        matches_exist, result_area = self.parse_result_area(main_results_html)
        primary_html = main_results_html.find(name='div', attrs={'id': 'primary'}) if matches_exist else None
        has_primary = primary_html is not None

        if has_primary:
            exact_block_html = primary_html.find(name='div', attrs={'class': 'exact_block'}) # Exact matches
            concepts_html = primary_html.find(name='div', attrs={'class': 'concepts'}) # Non-exact matches
            has_exact_block = exact_block_html is not None
            has_concepts = concepts_html is not None
        else:
            exact_block_html = None
            concepts_html = None
            has_exact_block = False
            has_concepts = False

        is_valid_search = has_primary and (has_exact_block or has_concepts)

        if matches_exist and is_valid_search:
            (result_count0, exact_matches) = self.parse_exact_matches(exact_block_html) if has_exact_block else (None, DictionaryEntryList())
            (result_count1, nonexact_matches, more_words_link) = self.parse_nonexact_matches(concepts_html) if has_concepts else (None, DictionaryEntryList(), None)
            result_count = result_count0 if result_count0 is not None else result_count1
            assert result_count is not None
        else:
            if matches_exist and primary_html is None and result_area.is_empty:
                raise Exception(
                    f"""
                    Failed to parse primary_html, but no explanation of the failure was found in result_area.
                    Perhaps there is some other information in the html for result_area that hasn't been parsed yet.
                    """
                )
            result_count = 0
            exact_matches = DictionaryEntryList()
            nonexact_matches = DictionaryEntryList()
            more_words_link = None
            print('No results found.')
        
        search_query = JishoSearchQuery(
            url=self.url,
            title=self.title,
            result_count=result_count,
            exact_matches=exact_matches, nonexact_matches=nonexact_matches,
            result_area=result_area, more_words_link=more_words_link,
            history_group_id=history_group_id
        )

        return search_query
    
    def parse_result_area(self, main_results_html: Tag) -> (bool, ResultArea):
        matches_exist = True
        grammar_breakdown = None
        number_conversion = None

        result_area_html = main_results_html.find(name='div', attrs={'id': 'result_area'})
        has_result_area = result_area_html is not None
        if not has_result_area:
            raise Exception(f"Couldn't find result area.")
        result_area_part_html_list = result_area_html.find_all(name='div')
        for result_area_part_html in result_area_part_html_list:
            if 'class' in result_area_part_html.attrs:
                if result_area_part_html['class'] == ['fact', 'grammar-breakdown']:
                    grammar_breakdown_explanation_html = result_area_part_html.find(name='h6')
                    grammar_breakdown_explanation_text = grammar_breakdown_explanation_html.text.strip()
                    dictionary_version_link_html = grammar_breakdown_explanation_html.find(name='a', href=True)
                    dictionary_version_link_text = dictionary_version_link_html.text.strip()
                    dictionary_version_link_url = f"https://jisho.org{dictionary_version_link_html['href']}"
                    dictionary_version_link = Link(
                        url=dictionary_version_link_url,
                        text=dictionary_version_link_text
                    )
                    grammar_breakdown_form_list_wrapper_html = result_area_part_html.find(name='ul', attrs={'class': 'no-bullet'})
                    grammar_breakdown_form_html_list = grammar_breakdown_form_list_wrapper_html.find_all(name='li')
                    grammar_breakdown_form_text_list = []
                    for grammar_breakdown_form_html in grammar_breakdown_form_html_list:
                        grammar_breakdown_form_text = grammar_breakdown_form_html.text.strip()
                        grammar_breakdown_form_text_list.append(grammar_breakdown_form_text)
                    grammar_breakdown = GrammarBreakdown(
                        dictionary_version_link=dictionary_version_link,
                        explanation=grammar_breakdown_explanation_text,
                        form_text_list=grammar_breakdown_form_text_list
                    )
                elif result_area_part_html['class'] == ['fact'] and result_area_part_html['id'] == 'number_conversion':
                    japanese_number_html = result_area_part_html.find(name='em')
                    japanese_number_text = japanese_number_html.text.strip()
                    converted_number_html = result_area_part_html.find(name='strong')
                    converted_number_text = converted_number_html.text.strip()
                    number_conversion = NumberConversion(
                        japanese_number_text=japanese_number_text,
                        converted_number_text=converted_number_text
                    )
                else:
                    raise Exception(
                        f"""
                        Encountered unknown result_area_part_html['class']: {result_area_part_html['class']}
                        url: {self.url}
                        """
                    )
            elif 'id' in result_area_part_html.attrs:
                if result_area_part_html['id'] == 'no-matches':
                    matches_exist = False
                else:
                    val = result_area_part_html['id']
                    val_str = f'{val}' if type(val) is not str else f"'{val}'"
                    raise Exception(
                        f"""
                        Encountered unknown result_area_part_html['id']: {val_str}
                        url: {self.url}
                        """
                    )
        result_area = ResultArea(
            grammar_breakdown=grammar_breakdown,
            number_conversion=number_conversion
        )
        return matches_exist, result_area

    def parse_exact_matches(self, exact_block_html: Tag) -> (int, DictionaryEntryList):
        result_count_html = exact_block_html.find(name='span', attrs={'class': 'result_count'})
        result_count = int(result_count_html.text.replace('—', '').replace('found', '').replace(' ', ''))
        concept_light_clearfix_html_list = exact_block_html.find_all(name='div', attrs={'class': 'concept_light clearfix'})
        exact_matches = DictionaryEntryList()
        for concept_light_clearfix_html in concept_light_clearfix_html_list:
            dictionary_entry = self.parse_concept_light_clearfix(concept_light_clearfix_html)
            exact_matches.append(dictionary_entry)
        return result_count, exact_matches

    def parse_nonexact_matches(self, concepts_html: Tag) -> (int, DictionaryEntryList, Link):
        result_count_html = concepts_html.find(name='span', attrs={'class': 'result_count'})
        result_count = int(result_count_html.text.replace('—', '').replace('found', '').replace(' ', '')) if result_count_html is not None else None
        concept_light_clearfix_html_list = concepts_html.find_all(name='div', attrs={'class': 'concept_light clearfix'}) # Non-exact match list
        nonexact_matches = DictionaryEntryList()
        for concept_light_clearfix_html in concept_light_clearfix_html_list:
            dictionary_entry = self.parse_concept_light_clearfix(concept_light_clearfix_html)
            nonexact_matches.append(dictionary_entry)
        more_html = concepts_html.find(name='a', attrs={'class': 'more'}, href=True)
        more_words_link_exists = more_html is not None
        more_words_link = None
        if more_words_link_exists:
            more_words_url = f"https:{more_html['href']}"
            more_words_link = Link(url=more_words_url, text='More Words')
        return result_count, nonexact_matches, more_words_link

    def parse_concept_light_clearfix(self, concept_light_clearfix_html: Tag) -> DictionaryEntry:
        word_representation = self.parse_word_representation(concept_light_clearfix_html)
        concept_labels = self.parse_concept_labels(concept_light_clearfix_html)
        supplementary_links = self.parse_supplementary_links(concept_light_clearfix_html)
        meaning_section = self.parse_meanings(concept_light_clearfix_html)

        dictionary_entry = DictionaryEntry(
            word_representation=word_representation,
            concept_labels=concept_labels,
            supplementary_links=supplementary_links,
            meaning_section=meaning_section
        )
        return dictionary_entry

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
            jlpt_level=jlpt_level,
            wanikani_level=wanikani_level
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
            audio_links=LinkList(audio_link_list),
            collocation_links=LinkList(collocation_link_list),
            other_links=LinkList(other_link_list)
        )
        return supplementary_links

    def parse_meanings(self, concept_light_clearfix_html: Tag) -> MeaningSection:
        concept_light_meanings_html = concept_light_clearfix_html.find(name='div', attrs={'class': 'concept_light-meanings medium-9 columns'})
        meaning_wrapper_html = concept_light_meanings_html.find(name='div', attrs={'class': 'meanings-wrapper'})
        light_details_link_html = concept_light_clearfix_html.find(name='a', attrs={'class': 'light-details_link'}, href=True)
        meaning_part_html_list = meaning_wrapper_html.find_all(name='div', recursive=False)
        meaning_parser = MeaningParser()
        current_meaning_tag = cast(MeaningTags, None)
        for meaning_part_html in meaning_part_html_list:
            if meaning_part_html['class'] == ['meaning-tags']:
                meaning_tag_text = meaning_part_html.text.strip()
                meaning_tag = MeaningTags(meaning_tag_text)
                meaning_tag.verify_is_known_tag(raise_exception_on_fail=False)
                meaning_parser.append(meaning_tag)
                current_meaning_tag = meaning_tag
            elif meaning_part_html['class'] == ['meaning-wrapper']:
                if current_meaning_tag is not None and current_meaning_tag.meaning_tag_text == 'Other forms':
                    other_form_html_list = meaning_part_html.find_all(name='span', attrs={'class': 'break-unit'})
                    other_forms = OtherFormList()
                    for other_form_html in other_form_html_list:
                        other_form_text = other_form_html.text.strip().replace(' ', '')
                        if '【' and '】' in other_form_text:
                            left_bracket_idx, right_bracket_idx = other_form_text.index('【'), other_form_text.index('】')
                            other_form_writing = other_form_text[:left_bracket_idx]
                            other_form_reading = other_form_text[left_bracket_idx+1:right_bracket_idx]
                        else:
                            other_form_writing = other_form_text
                            other_form_reading = None
                        other_form = OtherForm(writing=other_form_writing, reading=other_form_reading)
                        other_forms.append(other_form)
                    meaning_parser.append(other_forms)
                elif current_meaning_tag is not None and current_meaning_tag.meaning_tag_text == 'Notes':
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
                        section_divider_text=section_divider_text,
                        meaning_text=meaning_text,
                        supplemental_info=supplemental_info,
                        meaning_abstract_text=meaning_abstract_text,
                        meaning_abstract_link=meaning_abstract_link,
                        sentences=sentences
                    )
                    if current_meaning_tag is None: # This case exists too, although not very often.
                        meaning_parser.append(
                            MeaningTags('No Meaning Tag')
                        )
                    meaning_parser.append(meaning_wrapper)
            else:
                raise Exception(f"Unexpected meaning_part_html['class']: {meaning_part_html['class']}")
        meaning_section = meaning_parser.construct_meaning_section()
        return meaning_section

    def parse_supplemental_info(self, supplemental_info_html: Tag) -> SupplementalInfo:
        supplemental_info_part_html_list = supplemental_info_html.find_all(name='span', attrs={'class': 'sense-tag'})
        supplemental_info_parts = []
        for supplemental_info_part_html in supplemental_info_part_html_list:
            if supplemental_info_part_html['class'] in [['sense-tag', 'tag-tag'], ['sense-tag', 'tag-info'], ['sense-tag', 'tag-restriction'], ['sense-tag', 'tag-source']]:
                tag_text = supplemental_info_part_html.text.strip()
                plain_text = PlainText(
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
                plain_text_with_link = PlainTextWithLink(
                    text=tag_text, link=Link(url=part_link_url, text=part_link_text),
                    tag=supplemental_info_part_html['class'][1].replace('tag-','')
                )
                supplemental_info_parts.append(plain_text_with_link)
            else:
                raise Exception(
                    f"""
                    url: {self.url}
                    Unexpected supplemental_info_part_html['class']: {supplemental_info_part_html['class']}
                    supplemental_info_part_html.text.strip(): {supplemental_info_part_html.text.strip()}
                    """
                )
        supplemental_info = SupplementalInfo(supplemental_info_parts)
        return supplemental_info

    def parse_sentences(self, sentences_html: Tag) -> ExampleSentenceList:
        example_sentences = ExampleSentenceList()
        sentence_html_list = sentences_html.find_all(name='div', attrs={'class': 'sentence'})
        for sentence_html in sentence_html_list:
            sentence_text = sentence_html.text.strip()
            english_translation_html = sentence_html.find(name='li', attrs={'class': 'english'})
            english_translation_text = english_translation_html.text.strip()
            sentence_text = sentence_text.replace(english_translation_text, '')
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
                            # Note: Assume that unlinked_text doesn't contain kanji here, but there are exceptions.
                            # for char_str in unlinked_text:
                                # assert char_str in hiragana_chars + katakana_chars + misc_kana_chars
                                
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