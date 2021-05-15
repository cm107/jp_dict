import os
from jp_dict.parsing.koohii import KoohiiParser, KoohiiResultList
from jp_dict.parsing.combined.combined_structs import CombinedResultList

results = CombinedResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/filter_sorted_results.json')
kanji_dict = results.get_all_writing_kanji(include_hit_count=True)
print(f'kanji_dict: {kanji_dict}')
print(f'len(kanji_dict): {len(kanji_dict)}')

parser = KoohiiParser(username='jpdict_scraper', password='password', showWindow=False)
parser.parse_and_save(
    search_kanji_list=kanji_dict.keys(), hit_count_list=[info_dict['hit_count'] for info_dict in kanji_dict.values()],
    used_in_list=[info_dict['used_in'] for info_dict in kanji_dict.values()],
    save_dir='kanji_save', combined_save_path='combined.json'
)
koohii_results = KoohiiResultList.load_from_path('combined.json')
print(koohii_results)