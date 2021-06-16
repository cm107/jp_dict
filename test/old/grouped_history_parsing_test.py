from typing import List
from src.refactored.browser_history import CommonBrowserHistoryItemGroupList

group_list = CommonBrowserHistoryItemGroupList.load_from_path('jisho_grouped_history.json')

def get_search_word_from_title(title: str) -> str:
    if type(title) is list:
        relevant_title = None
        for title_candidate in title:
            if ' - Jisho.org' in title_candidate:
                relevant_title = title_candidate
                break
        assert relevant_title is not None
        search_word = relevant_title.replace(' - Jisho.org', '')
    else:
        search_word = title.replace(' - Jisho.org', '')
    return search_word

for group in group_list:
    search_word = get_search_word_from_title(group.title)
    print(f'group.url: {group.url}')
    print(f'Search Word: {search_word}')