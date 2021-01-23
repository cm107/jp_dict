from tqdm import tqdm
import urllib
from jp_dict.parsing.browser_history import CommonBrowserHistoryItemGroupList
from jp_dict.parsing.jisho.jisho_structs import JishoSearchQuery
from common_utils.file_utils import file_exists

parse_data_dir = '/home/clayton/workspace/prj/data_keep/data/study/parse_data'
jisho_grouped_history_path = f'{parse_data_dir}/jisho_grouped_history.json'
group_list = CommonBrowserHistoryItemGroupList.load_from_path(jisho_grouped_history_path)
jisho_parse_dump_dir = f'{parse_data_dir}/jisho_parse_dump'

pbar = tqdm(total=len(group_list), unit='word(s)')
for group in group_list:
    encoded_search_word = group.url.replace('https://jisho.org/search/', '')
    decoded_search_word = urllib.parse.unquote(encoded_search_word)
    pbar.set_description(decoded_search_word)

    skip = False
    for invalid_str in ['#kanji', '#sentences', '#names']:
        if invalid_str in decoded_search_word:
            skip = True
            break
    if skip:
        if pbar is not None:
            pbar.update()
        continue

    dump_path = f'{jisho_parse_dump_dir}/{decoded_search_word}.json'
    assert file_exists(dump_path), f"Couldn't find {dump_path}"
    search_query = JishoSearchQuery.load_from_path(dump_path)
    search_query.history_group_id = group.id
    search_query.save_to_path(dump_path, overwrite=True)
    pbar.update()
pbar.close()