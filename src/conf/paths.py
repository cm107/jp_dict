from ..submodules.common_utils.path_utils import get_script_dir, rel_to_abs_path
from ..submodules.common_utils.file_utils import link_exists, create_softlink

class PathConf:
    root_dir = rel_to_abs_path(f'{get_script_dir()}/../..')
    logger_log_dir = f"{root_dir}/src/submodules/logger/logs"
    logs_dir = f'{root_dir}/logs'
    if not link_exists(logs_dir):
        create_softlink(src_path=logger_log_dir, dst_path=logs_dir)
    data_dir = f'{root_dir}/data'
    favicon_dir = f'{data_dir}/favicon'
    word_list_save_dir = f"{data_dir}/word_list_save"
    jisho_history_word_list_save_path = f"{word_list_save_dir}/jisho_history_word_list.pkl"
    word_matches_save_dir = f"{data_dir}/word_matches"
    