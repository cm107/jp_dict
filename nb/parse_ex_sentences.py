import pickle
from src.conf.paths import PathConf
from src.util.loaders import load_word_matches
from src.lib.history_parsing.word_match_filter import default_filter
from common_utils.check_utils import check_dir_exists
from src.lib.word_results import WordResult
from src.lib.jap_vocab import OtherForm
import json
from logger import logger
from common_utils.adv_file_utils import get_dirpaths_in_dir
from common_utils.path_utils import get_filename
from common_utils.check_utils import check_file_exists, check_value

def get_example_sentences(search_word_list: str, ex_sentence_dirpath: str, max_num_results: int=None):
    check_dir_exists(ex_sentence_dirpath)
    # ex_sentence_dirpaths = get_dirpaths_in_dir(dir_path=PathConf.ex_sentences_dir)
    ex_sentence_dirpaths = get_dirpaths_in_dir(dir_path=ex_sentence_dirpath)
    if len(ex_sentence_dirpaths) == 0:
        logger.error(f"No example sentences found under: {ex_sentence_dirpath}")
        raise Exception

    example_sentences = []
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
                    if max_num_results is not None and len(example_sentences) == max_num_results:
                        return example_sentences
    return example_sentences

def word_result_buffer(word_result: WordResult) -> WordResult:
    return word_result

def other_form_buffer(other_form: OtherForm) -> OtherForm:
    return other_form

def print_sentence_results(filtered_results: list, search_mode: int):
    """
    search_mode
    0: Search writing only
    1: Search writing first, and search reading if there are no results
    2: Search both reading and writing
    """
    for result in filtered_results:
        search_word = result['search_word']
        matching_result = result['matching_results'][0]
        word_result = word_result_buffer(matching_result)

        writing_only_search_word_list = []
        full_search_word_list = []

        match_writing = word_result.jap_vocab.writing
        match_reading = word_result.jap_vocab.reading
        full_search_word_list.extend([match_writing, match_reading])
        writing_only_search_word_list.append(match_writing)
        other_forms = word_result.vocab_entry.other_forms.other_form_list if word_result.vocab_entry.other_forms is not None else []
        for other_form in other_forms:
            other_form = other_form_buffer(other_form)
            other_form_writing = other_form.kanji_writing
            other_form_reading = other_form.kana_writing
            full_search_word_list.append(other_form_writing)
            writing_only_search_word_list.append(other_form_writing)
            if other_form_reading is not None:
                full_search_word_list.append(other_form_reading)

        check_value(item=search_mode, valid_value_list=[0, 1, 2])
        flag = False
        if search_mode == 0:
            example_sentences = get_example_sentences(writing_only_search_word_list, ex_sentence_dirpath=PathConf.ex_sentences_dir, max_num_results=None)
        elif search_mode == 1:
            example_sentences = get_example_sentences(writing_only_search_word_list, ex_sentence_dirpath=PathConf.ex_sentences_dir, max_num_results=None)
            if len(example_sentences) == 0:
                flag = True
                example_sentences = get_example_sentences(full_search_word_list, ex_sentence_dirpath=PathConf.ex_sentences_dir, max_num_results=10)
        elif search_mode == 2:
            example_sentences = get_example_sentences(full_search_word_list, ex_sentence_dirpath=PathConf.ex_sentences_dir, max_num_results=10)
        else:
            raise Exception

        logger.yellow(f"{match_writing}:")
        for i, example_sentence in enumerate(example_sentences):
            if flag:
                logger.cyan(f"\t{i}: {example_sentence}")
            else:
                logger.purple(f"\t{i}: {example_sentence}")

jlpt_all_notes_save_path = f"{PathConf.anki_dir}/jlpt_all_save.pkl"
jlpt_all_vocab_list = pickle.load(open(jlpt_all_notes_save_path, 'rb'))
anime_vocab_notes_save_path = f"{PathConf.anki_dir}/anime_vocab_save.pkl"
anime_vocab_vocab_list = pickle.load(open(anime_vocab_notes_save_path, 'rb'))

word_matches_save_path = f"{PathConf.word_matches_save_dir}/test.pkl"
matching_results = load_word_matches(word_matches_save_path)
filtered_results = default_filter(matching_results=matching_results, learned_lists=[jlpt_all_vocab_list, anime_vocab_vocab_list])

print_sentence_results(filtered_results=filtered_results, search_mode=1)