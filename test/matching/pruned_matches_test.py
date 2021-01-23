from tqdm import tqdm
from logger import logger
from jp_dict.parsing.jisho.jisho_matches import SearchWordMatchesHandler, DictionaryEntryMatchList
from common_utils.file_utils import make_dir_if_not_exists, file_exists

parse_data_dir = '/home/clayton/workspace/prj/data_keep/data/study/parse_data'
jisho_matches_path = f'{parse_data_dir}/jisho_matches.json'
jisho_matches = SearchWordMatchesHandler.load_from_path(jisho_matches_path)
mode_test_dump_dir = 'mode_test_dump'
make_dir_if_not_exists(mode_test_dump_dir)

logger.info(f'Base Mode Test')
base_save = f'{mode_test_dump_dir}/base.json'
if not file_exists(base_save):
    entry_match_list = DictionaryEntryMatchList()
    entry_match_list.add_pruned_matches(handler=jisho_matches.unique, mode=0, show_pbar=True, leave_pbar=True)
    entry_match_list.save_to_path(base_save, overwrite=True)
else:
    entry_match_list = DictionaryEntryMatchList.load_from_path(base_save)
logger.purple(f'\tlen(entry_match_list): {len(entry_match_list)}')

for mode in [0, 1, 2]:
    logger.info(f"Mode {mode} Test")
    save_path = f'{mode_test_dump_dir}/mode{mode}.json'
    if not file_exists(save_path):
        temp_match_list = entry_match_list.copy()
        temp_match_list.add_pruned_matches(handler=jisho_matches.non_unique, mode=mode, show_pbar=True, leave_pbar=True)
        temp_match_list.save_to_path(save_path, overwrite=True)
    else:
        temp_match_list = DictionaryEntryMatchList.load_from_path(save_path)
    logger.purple(f'\tlen(temp_match_list): {len(temp_match_list)}')

# Conclusion: Although it is the most strict, Mode 1 seems to work fine for pruning results with multiple matches.