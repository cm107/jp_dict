import os
from jp_dict.parsing.koohii import KoohiiParser, KoohiiResultList
from jp_dict.parsing.combined.combined_structs import CombinedResultList
from jp_dict.parsing.combined.kanji_info import WritingKanjiInfoList

if not os.path.isfile('temp.json'):
    results = CombinedResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/filter_sorted_results.json')
    kanji_info_list = results.get_all_writing_kanji(include_hit_count=True)
    kanji_info_list.save_to_path('temp.json')
else:
    kanji_info_list = WritingKanjiInfoList.load_from_path('temp.json')

# print(f'kanji_info_list: {kanji_info_list}')
# print(f'len(kanji_info_list): {len(kanji_info_list)}')

parser = KoohiiParser(username='jpdict_scraper', password='password', showWindow=True)
parser.parse_and_save(
    kanji_info_list=[kanji_info_list[1]],
    save_dir='kanji_save', combined_save_path='combined.json'
)
koohii_results = KoohiiResultList.load_from_path('combined.json')
print(koohii_results)