from __future__ import annotations
from src.refactored.jisho_structs import JishoSearchQuery, DictionaryEntryList
from common_utils.path_utils import get_all_files_of_extension, get_rootname_from_path
from logger import logger
from tqdm import tqdm
from src.refactored.jisho_matches import SearchWordMatches, SearchWordMatchesHandler

jisho_parse_dump_dir = 'jisho_parse_dump'
dump_paths = get_all_files_of_extension(jisho_parse_dump_dir, extension='json')

sw_matches_handler = SearchWordMatchesHandler()

pbar = tqdm(total=len(dump_paths), unit='dump(s)')
pbar.set_description('Searching For Matches')
for dump_path in dump_paths:
    exact_matches = DictionaryEntryList()
    search_word = get_rootname_from_path(dump_path)
    query = JishoSearchQuery.load_from_path(dump_path)
    writing_match_idx_list = []
    reading_match_idx_list = []
    all_matches = query.exact_matches + query.nonexact_matches
    for i in range(len(all_matches)):
        if all_matches[i].word_representation.writing == search_word:
            writing_match_idx_list.append(i)
        if all_matches[i].word_representation.reading == search_word:
            reading_match_idx_list.append(i)
    if len(writing_match_idx_list) > 0:
        for idx in writing_match_idx_list:
            exact_matches.append(all_matches[idx])
    elif len(reading_match_idx_list) > 0:
        for idx in reading_match_idx_list:
            exact_matches.append(all_matches[idx])
    else:
        pass
    sw_matches = SearchWordMatches(search_word=search_word, matches=exact_matches)
    sw_matches_handler.append(sw_matches)
    pbar.update()
sw_matches_handler.save_to_path('sw_matches_dump.json', overwrite=True)

unique_sw_matches_handler = sw_matches_handler.get_unique()

for sw_matches in unique_sw_matches_handler: # These will be used when parsing from kotobank
    logger.cyan(f'Search Word: {sw_matches.search_word}')
    logger.purple(sw_matches.matches.custom_str())

logger.yellow(f'Number of Unique Matches: {len(unique_sw_matches_handler)}')