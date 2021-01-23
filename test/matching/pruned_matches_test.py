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

comparison_dir = f'{mode_test_dump_dir}/comparison'
make_dir_if_not_exists(comparison_dir)
for pair in [('base', 0), ('base', 1), ('base', 2), (1, 0), (0, 2), (1, 2)]:
    x_key, y_key = pair

    def load(key) -> DictionaryEntryMatchList:
        if key == 'base':
            return DictionaryEntryMatchList.load_from_path(base_save)
        elif type(key) is int:
            return DictionaryEntryMatchList.load_from_path(f'{mode_test_dump_dir}/mode{mode}.json')
        else:
            raise Exception
    
    diff_save = f'{comparison_dir}/{y_key}-{x_key}.json'
    logger.cyan(f'{y_key}-{x_key}')
    if not file_exists(diff_save):
        x, y = load(x_key), load(y_key)
        entry_match_list_diff = DictionaryEntryMatchList()
        pbar = tqdm(total=len(y), unit='item(s)', leave=False)
        pbar.set_description(f'Calculating {y_key}-{x_key}')
        for item in y:
            if not x.entries.contains_same_entry_as(item.entry, strict=False):
                entry_match_list_diff.append(item)
            pbar.update()
        pbar.close()
        entry_match_list_diff.save_to_path(diff_save, overwrite=True)
    else:
        entry_match_list_diff = DictionaryEntryMatchList.load_from_path(diff_save)
    logger.purple(f'\tlen(entry_match_list_diff): {len(entry_match_list_diff)}')

    with open(f'{comparison_dir}/{y_key}-{x_key}.txt', 'w') as f:
        f.write(entry_match_list_diff.custom_str(indent=0, num_line_breaks=3))
        # lines = entry_match_list_diff.custom_str(indent=0, num_line_breaks=2).split('\n')
        # pbar = tqdm(total=len(lines), unit='line(s)', leave=False)
        # pbar.set_description(f'Writing {y_key}-{x_key}')
        # for line in lines:
        #     f.write(line)
        #     pbar.update()
        # pbar.close()

# TODO: Needs debugging.