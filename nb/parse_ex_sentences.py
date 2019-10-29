import pickle
from src.conf.paths import PathConf
from src.util.loaders import load_word_matches
from src.lib.history_parsing.word_match_filter import default_filter

jlpt_all_notes_save_path = f"{PathConf.anki_dir}/jlpt_all_save.pkl"
jlpt_all_vocab_list = pickle.load(open(jlpt_all_notes_save_path, 'rb'))
anime_vocab_notes_save_path = f"{PathConf.anki_dir}/anime_vocab_save.pkl"
anime_vocab_vocab_list = pickle.load(open(anime_vocab_notes_save_path, 'rb'))

word_matches_save_path = f"{PathConf.word_matches_save_dir}/test.pkl"
matching_results = load_word_matches(word_matches_save_path)
filtered_results = default_filter(matching_results=matching_results, learned_lists=[jlpt_all_vocab_list, anime_vocab_vocab_list])

import json
from logger import logger
from common_utils.adv_file_utils import get_dirpaths_in_dir
from common_utils.path_utils import get_filename
from common_utils.check_utils import check_file_exists

def get_example_sentences(search_word_list: str):
    example_sentences = []
    ex_sentence_dirpaths = get_dirpaths_in_dir(dir_path=PathConf.ex_sentences_dir)

    for ex_sentence_dirpath in ex_sentence_dirpaths:
        # logger.cyan(f"ex_sentence_dirpath: {ex_sentence_dirpath}")
        index_path = f"{ex_sentence_dirpath}/index.json"
        check_file_exists(index_path)
        index_dict = json.load(open(index_path, 'r'))
        # index_dict = json.dumps(index_dict, indent=2, ensure_ascii=False)
        # logger.purple(index_dict)
        chapter_dict = index_dict['chapter_dict']
        # logger.cyan(chapter_dict)
        for chapter_number, chapter_data in chapter_dict.items():
            section_dict = chapter_data['section_dict']
            for section_number, section_data in section_dict.items():
                section_title = section_data['title']
                # logger.yellow(f"======Chapter {chapter_number}, Section {section_number}: {section_title}========")
                save_path = section_data['save_path']
                save_filename = get_filename(save_path)
                save_path = f"{ex_sentence_dirpath}/{save_filename}"
                check_file_exists(save_path)
                section_json_dict = json.load(open(save_path, 'r'))
                section_content = section_json_dict['content']
                for line_number, line_text in section_content.items():
                    # logger.purple(f"{line_number}: {line_text}")
                    for word in search_word_list:
                        if word in line_text:
                            example_sentences.append(line_text)
                            break
    return example_sentences

from src.lib.word_results import WordResult
from src.lib.jap_vocab import OtherForm
def word_result_buffer(word_result: WordResult) -> WordResult:
    return word_result

def other_form_buffer(other_form: OtherForm) -> OtherForm:
    return other_form

for result in filtered_results:
    search_word = result['search_word']
    matching_result = result['matching_results'][0]
    word_result = word_result_buffer(matching_result)

    search_word_list = []

    match_writing = word_result.jap_vocab.writing
    match_reading = word_result.jap_vocab.reading
    search_word_list.extend([match_writing, match_reading])
    other_forms = word_result.vocab_entry.other_forms.other_form_list if word_result.vocab_entry.other_forms is not None else []
    for other_form in other_forms:
        other_form = other_form_buffer(other_form)
        other_form_writing = other_form.kanji_writing
        other_form_reading = other_form.kana_writing
        search_word_list.extend([other_form_writing, other_form_reading])
    
    example_sentences = get_example_sentences(search_word_list)
    logger.yellow(f"{match_writing}:")
    for i, example_sentence in enumerate(example_sentences):
        logger.purple(f"\t{i}: {example_sentence}")
