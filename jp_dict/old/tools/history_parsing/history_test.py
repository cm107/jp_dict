from src.lib.history_parser import HistoryParser
import requests, pickle
from bs4 import BeautifulSoup
from src.lib.cache import Cache, CacheHandler
from logger import logger
from common_utils.file_utils import file_exists
from common_utils.path_utils import get_script_dir

script_dir = get_script_dir()
history_json_path = f'{script_dir}/Takeout/Chrome/BrowserHistory.json'
# icon_dump_dir = f'{script_dir}/icon_dump'

# history_parser = HistoryParser(history_json_path=history_json_path)
# history_parser.load()
# # history_parser.download_all_favicon(icon_dump_dir=icon_dump_dir)
# # history_parser.print_url_frequencies()
# ===================

cache_file_path = 'cache.pkl'

latest_index_completed = None

if not file_exists(cache_file_path):
    history_parser = HistoryParser(history_json_path=history_json_path)
    history_parser.load()
    relevant_urls = history_parser.get_urls_that_start_with('https://jisho.org/search')
    search_word_cache_handler = CacheHandler()
else:
    cache_dict = pickle.load(open(cache_file_path, 'rb'))
    search_word_cache_handler = cache_dict['search_word_cache_handler']
    relevant_urls = cache_dict['relevant_urls']
    latest_index_completed = cache_dict['latest_index_completed']

for i, url in zip(range(len(relevant_urls)), relevant_urls):
    if latest_index_completed is not None and i <= latest_index_completed:
        logger.info(f"{i}: Result in cache. Skipping.")
        continue
    response = requests.get(url)
    if response.status_code != 200:
        logger.warning(f"Encountered status_code: {response.status_code}")
        logger.warning(f"Skipping {url}")
        continue
    soup = BeautifulSoup(response.text, 'html.parser')
    search_word = soup.title.text.split('-')[0][:-1]
    logger.blue(f"{i}: {search_word}")
    url_word_pair = {'url': url, 'search_word': search_word}
    search_word_cache = Cache(url_word_pair)
    search_word_cache_handler.process(item=url_word_pair, item_key='url')
    latest_index_completed = i
    cache_dict = {}
    cache_dict['search_word_cache_handler'] = search_word_cache_handler
    cache_dict['relevant_urls'] = relevant_urls
    cache_dict['latest_index_completed'] = latest_index_completed
    pickle.dump(cache_dict, open(cache_file_path, 'wb'))
# ===================