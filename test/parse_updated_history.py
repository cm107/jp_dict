from common_utils.file_utils import make_dir_if_not_exists, file_exists
from src.refactored.parse_manager import ParserManager

parse_data_dir = 'parse_data'
make_dir_if_not_exists(parse_data_dir)
manager_save_path = f'{parse_data_dir}/manager.json'

if not file_exists(manager_save_path):
    manager = ParserManager(
        browser_history_dir='/home/clayton/workspace/study/jp_dict/data/browser_history',
        combined_history_path=f'{parse_data_dir}/combined_history.json',
        jisho_grouped_history_path=f'{parse_data_dir}/jisho_grouped_history.json',
        jisho_parse_dump_dir=f'{parse_data_dir}/jisho_parse_dump',
        jisho_matches_path=f'{parse_data_dir}/jisho_matches.json',
        kotobank_parse_dump_dir=f'{parse_data_dir}/kotobank_parse_dump',
        manager_save_path=manager_save_path
    )
else:
    manager = ParserManager.load_from_path(manager_save_path)
manager.run(verbose=True, show_pbar=True)