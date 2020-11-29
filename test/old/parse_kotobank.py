from common_utils.file_utils import make_dir_if_not_exists
from src.refactored.jisho_matches import SearchWordMatchesHandler
from common_utils.path_utils import get_all_files_of_extension, get_rootname_from_path
from tqdm import tqdm

from src.refactored.kotobank.kotobank_structs import KotobankWordHtmlParser

search_word_matches_handler = SearchWordMatchesHandler.load_from_path('analyze_parse_dump/sw_matches_dump.json')

dump_dir = 'kotobank_dump'
make_dir_if_not_exists(dump_dir)
searched_words = [get_rootname_from_path(path) for path in get_all_files_of_extension(dump_dir, extension='json')]
pbar = tqdm(total=len(search_word_matches_handler), unit='searches')

for search_word_matches in search_word_matches_handler:
    pbar.set_description(search_word_matches.search_word)
    if search_word_matches.search_word in searched_words:
        pbar.update()
        continue
    parser = KotobankWordHtmlParser.from_search_word(search_word_matches.search_word)
    result = parser.parse()
    result.save_to_path(f'{dump_dir}/{search_word_matches.search_word}.json')
    searched_words.append(search_word_matches.search_word)
    pbar.update()

# # parser = KotobankWordHtmlParser.from_search_word('余り')
# # parser = KotobankWordHtmlParser.from_search_word('passage')
# # parser = KotobankWordHtmlParser.from_search_word('隼')
# # parser = KotobankWordHtmlParser.from_search_word('王妃')
# # parser = KotobankWordHtmlParser.from_search_word('豊臣')
# # parser = KotobankWordHtmlParser.from_search_word('センチ')
# # parser = KotobankWordHtmlParser.from_search_word('奇特')
# # parser = KotobankWordHtmlParser.from_search_word('作法')
# parser = KotobankWordHtmlParser.from_search_word('展開')
# parser.parse()