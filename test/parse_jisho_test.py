from typing import List
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag
from common_utils.base.basic import BasicLoadableObject

class WordRepresentation(BasicLoadableObject['WordRepresentation']):
    def __init__(self, text: str, furigana: str=None):
        super().__init__()
        self.text = text
        self.furigana = furigana

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
        print(f'word_representation: {word_representation}')

        concept_labels = self.parse_concept_labels(concept_light_clearfix_html)
        print(f'concept_labels: {concept_labels}')

        supplementary_links = self.parse_supplementary_links(concept_light_clearfix_html)
        print(f'supplementary_links:\n{supplementary_links}')

        concept_light_meanings_html = concept_light_clearfix_html.find(name='div', attrs={'class': 'concept_light-meanings medium-9 columns'}) # TODO
    
    def parse_word_representation(self, concept_light_clearfix_html: Tag) -> WordRepresentation:
        concept_light_representation_html = concept_light_clearfix_html.find(name='div', attrs={'class': 'concept_light-representation'})
        furigana_html = concept_light_representation_html.find(name='span', attrs={'class': 'furigana'})
        text_html = concept_light_representation_html.find(name='span', attrs={'class': 'text'})
        
        furigana = furigana_html.text.strip()
        text = text_html.text.strip()
        word_representation = WordRepresentation(text=text, furigana=furigana)
        return word_representation

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

parser = JishoSearchHtmlParser('日')
# parser = JishoSearchHtmlParser('落ちる')
# parser = JishoSearchHtmlParser('ニヤリ')
# parser = JishoSearchHtmlParser('lsdgkj')
parser.parse()
