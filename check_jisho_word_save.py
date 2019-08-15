import pickle
from src.submodules.logger.logger_handler import logger
from src.conf.paths import PathConf

cache_file_path = PathConf.jisho_history_word_list_save_path
cache_dict = pickle.load(open(cache_file_path, 'rb'))
search_word_cache_handler = cache_dict['search_word_cache_handler']

search_word_cache_handler.print_cache_summary()