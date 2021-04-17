from jp_dict.parsing.combined.combined_structs import CombinedResultList
from jp_dict.util.time_utils import get_days_elapsed_from_time_usec, get_utc_time_from_time_usec, \
    utc2localzone

results = CombinedResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/jisho_kotobank_combined_results.json')

# results.sort(attr_name='search_word_hit_count', reverse=True)
# results.sort(attr_name='first_search_localtime')
# results.sort(attr_name='last_search_localtime', reverse=True)
results.recommended_sort(show_pbar=True, leave_pbar=True)

print(f'len(results): {len(results)}')
results = results.filter_out_anki_export('/home/clayton/workspace/prj/data_keep/data/study/anki/jlpt_vocab.txt')
print(f'len(results): {len(results)}')
results = results.filter_out_anki_export('/home/clayton/workspace/prj/data_keep/data/study/anki/anime_vocab.txt')
print(f'len(results): {len(results)}')

results.save_to_path('filtered_results.json', overwrite=True)

# for result in results:
#     print_str = f'word: {result.jisho_result.entry.word_representation.simple_repr}'
#     print_str += f"\n\tresult.search_word_hit_count: {result.search_word_hit_count}"
#     print_str += f"\n\tresult.is_common_word: {result.is_common_word}"
#     print_str += f"\n\tresult.jlpt_level: {result.jlpt_level}"
#     print_str += f"\n\tresult.wanikani_level: {result.wanikani_level}"
#     print(print_str)

#     for search_word, localtime_list in result.localtime_info.items():
#         localtime_list[0].isoformat()
#         print_str = f"{search_word}:"
#         print_str += f"\n\t{[localtime.strftime('%Y/%m/%d %H:%M:%S') for localtime in localtime_list]}"
#         print(print_str)