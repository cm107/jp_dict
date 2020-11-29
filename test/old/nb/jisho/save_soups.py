from src.util.utils import recursively_get_all_matches_under_dirpath
from src.lib.history_parsing.soup_saver import SoupSaver

browser_history_folder = "/home/clayton/workspace/study/jp_dict/data/browser_history"
matches = recursively_get_all_matches_under_dirpath(
    dirpath=browser_history_folder,
    target_name='BrowserHistory.json',
    target_type='file'
)
matches.sort()

soup_saver = SoupSaver(
    history_json_path_list=matches,
    soup_root_dir="/home/clayton/workspace/study/jp_dict/data/jisho_soup"
)
soup_saver.run()
