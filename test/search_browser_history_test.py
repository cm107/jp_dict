from src.refactored.browser_history import BrowserHistory, CommonBrowserHistoryItemGroup
from logger import logger
import operator

browser_history = BrowserHistory.load_from_path('combined_history.json')
group_list = browser_history.browser_history_item_list.search_by_url_base_and_group_by_url('https://jisho.org/search/')
group_list.sort(key=operator.attrgetter('item_count'), reverse=True)
for i, group in enumerate(group_list):
    if type(group.title) is list:
        print(f"{i} -> Word: {[title for title in group.title]}, Hit Count: {group.item_count}")
    else:
        print(f"{i} -> Word: {group.title.replace(' - Jisho.org', '')}, Hit Count: {group.item_count}")
        pass
