from logger import logger
from src.refactored.jisho_structs import JishoSearchHtmlParser, JishoSearchQueryHandler

search_word = '日'
# search_word = '落ちる'
# search_word = 'ニヤリ'
# search_word = '送り仮名'
# search_word = '日記帳'
# search_word = '学'
# search_word = 'lsdgkj'

from common_utils.file_utils import make_dir_if_not_exists
query_save_dir = 'queries'
make_dir_if_not_exists(query_save_dir)

query_handler = JishoSearchQueryHandler()
parser = JishoSearchHtmlParser.from_search_word(search_word)
count = 1
logger.cyan(f'===========Page {count}============')
logger.yellow(parser.url)
search_query = parser.parse()
query_handler.append(search_query)
while search_query.has_more_words_link:
    count += 1
    logger.cyan(f'===========Page {count}============')
    parser = JishoSearchHtmlParser(search_query.more_words_link.url)
    logger.yellow(parser.url)
    search_query = parser.parse()
    query_handler.append(search_query)
query_handler.save_to_path(f'{query_save_dir}/{search_word}_query.json', overwrite=True)