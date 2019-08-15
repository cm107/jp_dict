"""
Script for updating jisho word list, where the word list is saved as a pkl file.

Usage:
    update_jisho_word_list.py (--history_json_path PATH) [--save_file_path PATH]
    update_jisho_word_list.py (-h | --help)

Options:
    --history_json_path Path to the Chrome history json file that was exported from Chrome.
    --save_file_path Path to where you would like to save your word list.
    -h --help   Show this message and exit
"""

from docopt import docopt
args = docopt(__doc__, version='Alpha 1.0')
print(args)

import requests, pickle
from bs4 import BeautifulSoup
from src.submodules.logger.logger_handler import logger
from src.submodules.common_utils.file_utils import file_exists
from src.lib.history_parsing.cache import Cache, CacheHandler
from src.lib.history_parsing.history_parser import HistoryParser
from src.submodules.logger.log_writer import log_writer
from src.submodules.common_utils.path_utils import rel_to_abs_path
from src.conf.paths import PathConf

history_json_path = args['--history_json_path']
history_json_path = rel_to_abs_path(history_json_path) if history_json_path is not None \
    else None
if not file_exists(history_json_path):
    logger.error(f"File not found: {history_json_path}")
    raise Exception

save_file_path = args['--save_file_path']
save_file_path = rel_to_abs_path(save_file_path) if save_file_path is not None \
    else PathConf.jisho_history_word_list_save_path

history_parser = HistoryParser(history_json_path=history_json_path)
history_parser.load()
relevant_times, relevant_urls = history_parser.get_urls_that_start_with('https://jisho.org/search')

if not file_exists(save_file_path):
    search_word_cache_handler = CacheHandler()
else:
    cache_dict = pickle.load(open(save_file_path, 'rb'))
    search_word_cache_handler = cache_dict['search_word_cache_handler']

for i, time_usec, url in zip(range(len(relevant_urls)), relevant_times, relevant_urls):
    # found, _ = search_word_cache_handler.search_item(item={'url': url, 'search_word': None}, item_key='url')
    found, duplicate = search_word_cache_handler.check_url(url=url, time_usec=time_usec)
    if not found:
        response = requests.get(url)
        if response.status_code != 200:
            logger.warning(f"Encountered status_code: {response.status_code}")
            logger.warning(f"Skipping {url}")
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        search_word = soup.title.text.split('-')[0][:-1]
        logger.blue(f"{i}: {search_word}")
        url_word_pair = {'url': url, 'search_word': search_word}
        search_word_cache_handler.process(item=url_word_pair, time_usec=time_usec, item_key='url')
    else:
        if not duplicate:
            logger.yellow(f"{i}: URL already in cache (hit) - {url}")
        else:
            logger.yellow(f"{i}: Duplicate found in cache (no hit) - {url}")
    cache_dict = {}
    cache_dict['search_word_cache_handler'] = search_word_cache_handler
    pickle.dump(cache_dict, open(save_file_path, 'wb'))

log_writer.write_all_logs()