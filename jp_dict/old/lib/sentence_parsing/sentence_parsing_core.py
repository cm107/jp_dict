import json
from logger import logger
from common_utils.check_utils import check_dir_exists
from common_utils.adv_file_utils import get_dirpaths_in_dir
from common_utils.path_utils import get_filename
from common_utils.check_utils import check_file_exists, check_value
from src.lib.jisho.word_results import WordResult
from src.lib.jisho.jap_vocab import OtherForm

def get_example_sentences(search_word_list: str, ex_sentence_root_dir: str, max_num_results: int=None):
    check_dir_exists(ex_sentence_root_dir)
    ex_sentence_dirpaths = get_dirpaths_in_dir(dir_path=ex_sentence_root_dir)
    if len(ex_sentence_dirpaths) == 0:
        logger.error(f"No example sentence directories found under: {ex_sentence_root_dir}")
        raise Exception

    example_sentences = []
    for ex_sentence_dirpath in ex_sentence_dirpaths:
        index_path = f"{ex_sentence_dirpath}/index.json"
        check_file_exists(index_path)
        index_dict = json.load(open(index_path, 'r'))
        chapter_dict = index_dict['chapter_dict']
        for chapter_number, chapter_data in chapter_dict.items():
            section_dict = chapter_data['section_dict']
            for section_number, section_data in section_dict.items():
                section_title = section_data['title']
                save_path = section_data['save_path']
                save_filename = get_filename(save_path)
                save_path = f"{ex_sentence_dirpath}/{save_filename}"
                check_file_exists(save_path)
                section_json_dict = json.load(open(save_path, 'r'))
                section_content = section_json_dict['content']
                for line_number, line_text in section_content.items():
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

def get_search_word_list(word_result: WordResult) -> (list, list):
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

    return writing_only_search_word_list, full_search_word_list

def search_for_example_sentences(writing_only_search_word_list: list, full_search_word_list: list, ex_sentence_root_dir: str, search_mode: int=0) -> (bool, list):
    check_value(item=search_mode, valid_value_list=[0, 1, 2])
    speculation_flag = False
    if search_mode == 0:
        example_sentences = get_example_sentences(writing_only_search_word_list, ex_sentence_root_dir=ex_sentence_root_dir, max_num_results=None)
    elif search_mode == 1:
        example_sentences = get_example_sentences(writing_only_search_word_list, ex_sentence_root_dir=ex_sentence_root_dir, max_num_results=None)
        if len(example_sentences) == 0:
            speculation_flag = True
            example_sentences = get_example_sentences(full_search_word_list, ex_sentence_root_dir=ex_sentence_root_dir, max_num_results=10)
    elif search_mode == 2:
        example_sentences = get_example_sentences(full_search_word_list, ex_sentence_root_dir=ex_sentence_root_dir, max_num_results=10)
    else:
        raise Exception
    return speculation_flag, example_sentences

def get_example_sentences_for_filtered_result(filtered_result: dict, ex_sentence_root_dir: str, search_mode: int=0) -> (bool, str, list):
    search_word = filtered_result['search_word']
    matching_result = filtered_result['matching_results'][0]
    word_result = word_result_buffer(matching_result)
    writing_only_search_word_list, full_search_word_list = get_search_word_list(word_result=word_result)
    match_writing = word_result.jap_vocab.writing

    speculation_flag, example_sentences = search_for_example_sentences(
        writing_only_search_word_list=writing_only_search_word_list,
        full_search_word_list=full_search_word_list,
        ex_sentence_root_dir=ex_sentence_root_dir,
        search_mode=search_mode
    )
    return speculation_flag, match_writing, example_sentences

def print_sentence_results(filtered_results: list, ex_sentence_root_dir: str, search_mode: int=0):
    """
    search_mode
    0: Search writing only
    1: Search writing first, and search reading if there are no results
    2: Search both reading and writing
    """
    for filtered_result in filtered_results:
        speculation_flag, match_writing, example_sentences = get_example_sentences_for_filtered_result(
            filtered_result=filtered_result,
            ex_sentence_root_dir=ex_sentence_root_dir,
            search_mode=search_mode
        )

        logger.yellow(f"{match_writing}:")
        for i, example_sentence in enumerate(example_sentences):
            if speculation_flag:
                logger.cyan(f"\t{i}: {example_sentence}")
            else:
                logger.purple(f"\t{i}: {example_sentence}")