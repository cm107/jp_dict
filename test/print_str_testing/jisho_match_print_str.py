from jp_dict.parsing.jisho.jisho_matches import SearchWordMatchesHandler

# TODO: Add id to CommonBrowserHistoryItemGroup and reference this id in constructor for JishoSearchQuery.
# This is necessary for efficiently counting the number of searches for a given word.
# JishoSearchQuery corresponds to the CommonBrowserHistoryItemGroup id, so JishoSearchQuery doesn't need an id.
# However, SearchWordMatch does need an id, since it is used for deciding what kotobank words to parse.
# In the event that multiple CommonBrowserHistoryItemGroup result in the same SearchWordMatch, the hit count needs to be added together.
# For example, if じしょ has 3 hits and 辞書 has 2 hits, the SearchWordMatch should be able to trace back to both of these words so that
# a total hit count of 5 can be calculated.
# Note: Hit count will be an important variable used for sorting. (I don't want the sorting to be too complicated, but this part is necessary.)

parse_data_dir = '/home/clayton/workspace/prj/data_keep/data/study/parse_data'
jisho_matches_path = f'{parse_data_dir}/jisho_matches.json'
jisho_matches = SearchWordMatchesHandler.load_from_path(jisho_matches_path)

jisho_matches = SearchWordMatchesHandler([result for result in jisho_matches if len(result.matches) > 1])
print(f'len(jisho_matches): {len(jisho_matches)}')
for result in jisho_matches:
    print(f'result.search_word: {result.search_word}')
    print(f'len(result.matches): {len(result.matches)}')
    print(f'result.matches:\n{result.matches.custom_str(indent=0)}')