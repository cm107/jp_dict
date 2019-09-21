import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, ResultSet
from ...util.checkers import check_page_response_status
from ...util.previews import preview_soup_nested_tag_children, preview_tag_children, \
    preview_html_nested_tag_children
from ...util.previews import blue_text, green_text, yellow_text, red_text, std_text
from ...util.getters import get_response, get_soup, get_soup_child, get_soup_nested_tag_child, \
    get_tag_child, get_all_tag_children, get_html_nested_tag_child
from ...util.utils import get_kana_maps
from ...lib.jap_vocab import JapaneseVocab, OtherForm, OtherForms
from ...lib.definition import DefinitionSection, DefinitionGroup, Definitions
from ...lib.misc import Notes
from ...lib.vocab_entry import VocabularyEntry
from ...lib.supplemental_info import SupplementalInfo, CategoryLabel, SeeAlsoLink, \
    RestrictionInfo, AdditionalInfo, AntonymLink, SourceInfo
from ...lib.concept import ConceptLabels
from ...lib.word_results import WordResult, WordResultHandler
from ...submodules.logger.logger_handler import logger

class JishoWordSearchCore:
    def __init__(self):
        # primary_results
        self.word_exact_matches = None
        self.word_other_matches = None

        # secondary_results
        self.kanji_results = None
        self.sentence_results = None
        self.name_results = None
        self.other_dictionaries = None

        # word_exact_matches
        self.word_result_count = None

        # Word Result Handler
        self.word_result_handler = WordResultHandler()

    def search(self, search_word: str, page_limit: int=None, silent: bool=True):
        url = 'https://jisho.org/search/{}'.format(search_word)
        page_number = 1
        while True:
            if not silent:
                logger.yellow(f'=========================Page {page_number}==============================')
            search_soup = self.get_soup(url)
            search_results = self.get_search_results(search_soup)
            self.parse_search_results(search_results)

            self.parse_word_result_count()
            if self.word_exact_matches is not None:
                self.parse_word_matches(self.word_exact_matches, category='exact_matches')
            if self.word_other_matches is not None:
                self.parse_word_matches(self.word_other_matches, category='other_matches')
            
            if not silent:
                self.word_result_handler.print_display_queue()

            url = self.parse_more_words_link_url(self.word_other_matches)
            if url is not None:
                page_number += 1
                if page_limit is not None and page_number > page_limit:
                    break
            else:
                break

    def get_soup(self, url: str):
        page = get_response(url)
        check_page_response_status(page)
        return get_soup(page)

    def parse_word_result_count(self):
        if self.word_exact_matches is not None:
            word_result_count = str(get_html_nested_tag_child(self.word_exact_matches, [1, 1, 0]))
        else:
            word_result_count = str(get_html_nested_tag_child(self.word_other_matches, [1, 1, 0]))
        self.word_result_count = int(word_result_count.replace(' — ', '').replace(' found', ''))
        self.word_result_handler.specify_num_results(self.word_result_count)

    def parse_word_matches(self, matches: Tag, category: str=None):
        entry_results = matches.find_all('div', 'concept_light clearfix')
        for i in range(len(entry_results)):
            japanese_wrapper = entry_results[i].find('div', 'concept_light-wrapper columns zero-padding')
            if japanese_wrapper is None:
                japanese_wrapper = entry_results[i].find('div', 'concept_light-wrapper concept_light-long_representation columns zero-padding')
            temp = entry_results[i].find('div', 'concept_light-meanings medium-9 columns')
            meanings_wrapper = temp.find('div', 'meanings-wrapper')
            jap_vocab = self.get_jap_vocab(japanese_wrapper)
            vocab_entry = self.get_vocab_entry(meanings_wrapper)

            concept_status = japanese_wrapper.find('div', 'concept_light-status')
            concept_labels = self.get_concept_labels(concept_status)

            if concept_labels is not None:
                word_result = WordResult(
                    jap_vocab=jap_vocab,
                    concept_labels=concept_labels,
                    vocab_entry=vocab_entry)
            else:
                word_result = WordResult(
                    jap_vocab=jap_vocab,
                    concept_labels=None,
                    vocab_entry=vocab_entry)
            
            self.word_result_handler.add(word_result, category)

    def get_concept_labels(self, concept_status: Tag) -> ConceptLabels:
        use_concept_labels = False
        if concept_status is not None:
            is_common_word = concept_status.find('span', 'concept_light-tag concept_light-common success label') is not None
            if is_common_word:
                use_concept_labels = True

            label_tags = concept_status.find_all('span', 'concept_light-tag label')
            if label_tags is not None:
                jlpt_level = None
                wanikani_level = None
                for label_tag in label_tags:
                    label_tag_text = label_tag.text
                    if 'JLPT' in label_tag_text:
                        jlpt_level = int(label_tag_text.replace('JLPT N', ''))
                        use_concept_labels = True
                    elif 'Wanikani' in label_tag_text:
                        wanikani_level = int(label_tag_text.replace('Wanikani level ', ''))
                        use_concept_labels = True
                    else:
                        raise NotImplementedError('Concept Label {} not accounted for.'.format(label_tag_text))
        
        if not use_concept_labels:
            return None
        
        return ConceptLabels(
            is_common_word=is_common_word,
            jlpt_level=jlpt_level,
            wanikani_level=wanikani_level
            )

    def parse_more_words_link_url(self, concepts: Tag):
        more_words = concepts.find('a', 'more', href=True)
        if more_words is None:
            return None
        more_words_url = more_words['href']
        return 'https:' + more_words_url

    def get_search_results(self, soup: BeautifulSoup):
        return get_soup_nested_tag_child(soup, [2, 3, 7, 1, 1, 3])

    def parse_search_results(self, search_results: Tag):
        primary_results = search_results.find(name='div', id='primary')
        secondary_results = search_results.find(name='div', id='secondary')

        self.word_exact_matches = primary_results.find('div', 'exact_block')
        self.word_other_matches = primary_results.find('div', 'concepts')
        self.kanji_results = secondary_results.find('div', 'kanji_light_block')
        self.sentence_results = secondary_results.find('div', 'sentences_block')
        self.name_results = secondary_results.find('div', 'names_block')
        self.other_dictionaries = secondary_results.find(name='aside', id='other_dictionaries')

    def get_jap_vocab(self, japanese_wrapper: Tag) -> JapaneseVocab:
        japanese = japanese_wrapper.find('div', 'concept_light-readings japanese japanese_gothic')\
            .find('div', 'concept_light-representation')
        furigana = japanese.find('span', 'furigana')
        furigana_children = furigana.find_all('span')
        furigana_parts = []
        for furigana_child in furigana_children:
            if len(furigana_child.text) > 0:
                furigana_parts.append(furigana_child.text)
        nominal_writing = japanese.find('span', 'text')
        okurigana_children = nominal_writing.find_all('span')
        okurigana_parts = []
        for okurigana_child in okurigana_children:
            if len(okurigana_child.text) > 0:
                okurigana_parts.append(okurigana_child.text)
        text = nominal_writing.text.replace('\n', '').replace(' ', '')
        kana_maps = get_kana_maps(text, furigana_parts, okurigana_parts)
        jap_vocab = JapaneseVocab(
            kana_maps=kana_maps
        )
        return jap_vocab

    def get_def_section(self, meaning_section: Tag) -> DefinitionSection:
        meaning_section_divider = meaning_section.find('span', 'meaning-definition-section_divider').text
        meaning_section_number = int(meaning_section_divider.replace('.',''))
        meaning_section_definition = meaning_section.find('span', 'meaning-meaning').text
        supplemental_info_tag = meaning_section.find('span', 'supplemental_info')
        supplemental_info = self.get_supplemental_info(supplemental_info_tag)
            
        return DefinitionSection(meaning_section_number, meaning_section_definition, supplemental_info)

    def get_vocab_entry(self, meanings_wrapper: Tag) -> VocabularyEntry:
        definitions = None
        other_forms = None
        notes = None
        
        tag_children = get_all_tag_children(meanings_wrapper)
        def_sections = []
        meaning_section_usage = ''
        def_groups = []
        for i in range(len(tag_children)):
            class_name = tag_children[i].get("class")[0]
            if class_name == 'meaning-tags':
                if len(def_sections) > 0 and meaning_section_usage != '':
                    def_group = DefinitionGroup(meaning_section_usage, def_sections)
                    def_groups.append(def_group)
                    def_sections = []
                meaning_section_usage = tag_children[i].text
            else:
                if meaning_section_usage != '':
                    tag_child = tag_children[i]
                    if meaning_section_usage == 'Other forms':
                        other_forms_section = tag_child.find('span', 'meaning-meaning', recursive=True)
                        other_forms = self.get_other_forms(other_forms_section)
                    elif meaning_section_usage == 'Notes':
                        notes_text = tag_child.text
                        notes = Notes(notes_text)
                    else:
                        # Meaning Section
                        meaning_section = tag_child.find('div', 'meaning-definition zero-padding')
                        def_section = self.get_def_section(meaning_section)
                        def_sections.append(def_section)
        if len(def_sections) > 0 and meaning_section_usage != '':
            def_group = DefinitionGroup(meaning_section_usage, def_sections)
            def_groups.append(def_group)
            def_sections = []
        definitions = Definitions(def_groups)
        vocab_entry = VocabularyEntry(definitions=definitions, other_forms=other_forms, notes=notes)
        return vocab_entry

    def get_other_forms(self, other_forms_section: Tag) -> OtherForms:
        other_forms_children = other_forms_section.find_all('span', 'break-unit')
        other_form_list = []
        for other_forms_child in other_forms_children:
            other_form_text = other_forms_child.text
            other_form_text_parts = other_form_text.split(' ')
            if len(other_form_text_parts) == 2:
                other_form_kanji_writing = other_form_text_parts[0]
                other_form_kana_writing = other_form_text_parts[1].replace('【', '').replace('】', '')
                other_form = OtherForm(other_form_kanji_writing, other_form_kana_writing)
            elif len(other_form_text_parts) == 1:
                other_form_kanji_writing = other_form_text_parts[0]
                other_form = OtherForm(other_form_kanji_writing, None)
            else:
                raise Exception('other_form_text_parts size of {} not accounted for'.format(len(other_form_text_parts)))
            other_form_list.append(other_form)
        return OtherForms(other_form_list)

    def get_supplemental_info(self, supplemental_info_tag: Tag) -> SupplementalInfo:
        use_supplemental_info = False

        category_label = None
        see_also_link = None
        restriction_info = None
        additional_info = None
        antonym_link = None
        source_info = None
        if supplemental_info_tag is not None:
            use_supplemental_info = True
            success = False
            category_label_tag = supplemental_info_tag.find('span', 'sense-tag tag-tag')
            see_also_tag = supplemental_info_tag.find('span', 'sense-tag tag-see_also')
            restriction_tag = supplemental_info_tag.find('span', 'sense-tag tag-restriction')
            info_tag = supplemental_info_tag.find('span', 'sense-tag tag-info')
            antonym_tag = supplemental_info_tag.find('span', 'sense-tag tag-antonym')
            source_info_tag = supplemental_info_tag.find('span', 'sense-tag tag-source')
            if category_label_tag is not None:
                success = True
                category_label_text = category_label_tag.text
                category_label = CategoryLabel(category_label_text)
            if see_also_tag is not None:
                success = True
                see_also = see_also_tag.find('a', href=True)
                see_also_text = see_also.text
                see_also_url = 'https://jisho.org' + see_also['href']
                see_also_link = SeeAlsoLink(see_also_text, see_also_url)
            if restriction_tag is not None:
                success = True
                restriction_text = restriction_tag.text
                restriction_info = RestrictionInfo(restriction_text)
            if info_tag is not None:
                success = True
                additional_info_text = info_tag.text
                additional_info = AdditionalInfo(additional_info_text)
            if antonym_tag is not None and len(antonym_tag) > 0:
                success = True
                if type(antonym_tag) is ResultSet:
                    antonym_tag = antonym_tag[0]
                antonym = antonym_tag.find_next('a', href=True)
                antonym_text = antonym.text
                antonym_url = 'https://jisho.org' + antonym['href']
                antonym_link = AntonymLink(antonym_text, antonym_url)
            if source_info_tag is not None:
                success = True
                source_info_text = source_info_tag.text
                source_info = SourceInfo(source_info_text)
            if not success:
                # print(red_text + 'HERE' + std_text)
                raise Exception('Supplemental Info item needs to be implemented.')
        
        supplemental_info = None
        if use_supplemental_info:
            supplemental_info = SupplementalInfo(
                category_label=category_label,
                see_also_link=see_also_link,
                restriction_info=restriction_info,
                additional_info=additional_info,
                antonym_link=antonym_link,
                source_info=source_info
            )
        return supplemental_info