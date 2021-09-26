from jp_dict.parsing.combined.combined_structs import CombinedResultList

path = "/home/clayton/workspace/prj/data_keep/data/study/parse_data/jisho_kotobank_combined_results.json"
results = CombinedResultList.load_from_path(path)
rel_count = len([result for result in results if result.search_word_hit_count >= 3])
total_count = len(results)
print(f"{rel_count}/{total_count} ({rel_count/total_count})")