from tqdm import tqdm
import urllib
from src.refactored.browser_history import CommonBrowserHistoryItemGroupList
from src.refactored.jisho_structs import JishoSearchHtmlParser
from common_utils.file_utils import make_dir_if_not_exists
from common_utils.path_utils import get_all_files_of_extension, get_rootname_from_path

parse_dump_dir = 'jisho_parse_dump'
make_dir_if_not_exists(parse_dump_dir)
existing_dump_paths = get_all_files_of_extension(parse_dump_dir, extension='json')
dumped_search_word_list = [get_rootname_from_path(existing_dump_path) for existing_dump_path in existing_dump_paths]

group_list = CommonBrowserHistoryItemGroupList.load_from_path('jisho_grouped_history.json')
search_word_list = []
url_list = []

pbar = tqdm(total=len(group_list), unit='word(s)')
for group in group_list:
    encoded_search_word = group.url.replace('https://jisho.org/search/', '')
    decoded_search_word = urllib.parse.unquote(encoded_search_word)
    pbar.set_description(decoded_search_word)
    if decoded_search_word not in search_word_list:
        search_word_list.append(decoded_search_word)
        url_list.append(group.url)
    else:
        idx = search_word_list.index(decoded_search_word)
        existing_url = url_list[idx]
        raise Exception(
            f"""
            Found two unique urls for the same search word.
            search_word: {decoded_search_word}
            existing_url: {existing_url}
            new_url: {group.url}
            """
        )
    skip = False
    for invalid_str in ['#kanji', '#sentences', '#names']:
        if invalid_str in decoded_search_word:
            skip = True
            break
    if skip or decoded_search_word in dumped_search_word_list:
        pbar.update()
        continue
    parser = JishoSearchHtmlParser(url=group.url)
    search_query = parser.parse()
    dump_path = f'{parse_dump_dir}/{decoded_search_word}.json'
    search_query.save_to_path(dump_path, overwrite=False)
    dumped_search_word_list.append(decoded_search_word)
    pbar.update()
