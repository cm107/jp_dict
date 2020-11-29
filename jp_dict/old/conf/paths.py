from common_utils.path_utils import get_script_dir, rel_to_abs_path
from common_utils.file_utils import link_exists, create_softlink
from logger import logger

class PathConf:
    root_dir = rel_to_abs_path(f'{get_script_dir()}/../..')
    if not link_exists(f"{root_dir}/logs"):
        logger.link_log_dir(root_dir)
    data_dir = f'{root_dir}/data'
    favicon_dir = f'{data_dir}/favicon'
    word_list_save_dir = f"{data_dir}/word_list_save"
    jisho_history_word_list_save_path = f"{word_list_save_dir}/jisho_history_word_list.pkl"
    word_matches_save_dir = f"{data_dir}/word_matches"
    anki_dir = f"{data_dir}/anki"
    ex_sentences_dir = f"{data_dir}/ex_sentences"
    jisho_soup_root_dir = f"{data_dir}/jisho_soup"
    jisho_soups_dir = f"{jisho_soup_root_dir}/soups"