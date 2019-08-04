import pickle
from src.submodules.logger.logger_handler import logger
from src.conf.paths import PathConf

cache_file_path = PathConf.jisho_history_word_list_save_path
cache_dict = pickle.load(open(cache_file_path, 'rb'))
search_word_cache_handler = cache_dict['search_word_cache_handler']
relevant_urls = cache_dict['relevant_urls']
latest_index_completed = cache_dict['latest_index_completed']

search_word_cache_handler.print_cache_summary()
percent_complete = round(100*latest_index_completed/len(relevant_urls))
logger.purple(f"{latest_index_completed}/{len(relevant_urls)} ({percent_complete}%)")