from __future__ import annotations
from logger import logger
from common_utils.path_utils import recursively_get_all_matches_under_dirpath
from src.refactored.browser_history import BrowserHistoryHandler

browser_history_folder = "/home/clayton/workspace/study/jp_dict/data/browser_history"
browser_history_paths = recursively_get_all_matches_under_dirpath(
    dirpath=browser_history_folder,
    target_name='BrowserHistory.json',
    target_type='file'
)
browser_history_paths.sort()
handler = BrowserHistoryHandler.load_from_path_list(browser_history_paths)
browser_history = handler[-1]

for item in browser_history.browser_history_item_list:
    logger.purple(f'title: {item.title}')