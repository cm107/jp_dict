from common_utils.file_utils import make_dir_if_not_exists, file_exists
from jp_dict.parsing.parse_manager import ParserManager

parse_data_dir = '/home/clayton/workspace/prj/data_keep/data/study/parse_data'
make_dir_if_not_exists(parse_data_dir)
manager_save_path = f'{parse_data_dir}/manager.json'

if not file_exists(manager_save_path):
    manager = ParserManager(
        browser_history_dir='/home/clayton/workspace/prj/data_keep/data/study/jp_dict_data/browser_history',
        combined_history_path=f'{parse_data_dir}/combined_history.json',
        jisho_grouped_history_path=f'{parse_data_dir}/jisho_grouped_history.json',
        jisho_parse_dump_dir=f'{parse_data_dir}/jisho_parse_dump',
        jisho_matches_path=f'{parse_data_dir}/jisho_matches.json',
        jisho_pruned_entries_path=f'{parse_data_dir}/pruned_jisho_entries.json',
        kotobank_parse_dump_dir=f'{parse_data_dir}/kotobank_parse_dump',
        kotobank_temp_map_dir=f'{parse_data_dir}/kotobank_temp_map',
        combined_kotobank_dump_path=f'{parse_data_dir}/kotobank_combined.json',
        jisho_kotobank_combined_dump_path=f'{parse_data_dir}/jisho_kotobank_combined_results.json',
        anki_export_dir_for_filter='/home/clayton/workspace/prj/data_keep/data/study/anki',
        filter_sorted_results_dump_path=f'{parse_data_dir}/filter_sorted_results.json',
        koohii_parse_dump_dir=f'{parse_data_dir}/koohii_parse_dump',
        koohii_combined_dump_path=f'{parse_data_dir}/koohii_combined.json',
        manager_save_path=manager_save_path
    )
else:
    manager = ParserManager.load_from_path(manager_save_path)
manager.run(verbose=True, show_pbar=True)

# TODO: After expanding on kotobank parser, some additional html cases need to be accounted for.
