import pickle
from ..submodules.common_utils.check_utils import check_file_exists

from ..lib.history_parsing.cache import CacheHandler

def load_search_word_cache_handler(cache_path: str) -> CacheHandler:
    check_file_exists(cache_path)
    cache_dict = pickle.load(open(cache_path, 'rb'))
    search_word_cache_handler = cache_dict['search_word_cache_handler']
    return search_word_cache_handler

def load_word_matches(word_matches_save_path: str) -> dict:
    check_file_exists(word_matches_save_path)
    matching_results_dict = pickle.load(open(word_matches_save_path, 'rb'))
    return matching_results_dict