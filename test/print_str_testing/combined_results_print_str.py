from jp_dict.parsing.combined.combined_structs import CombinedResultList

combined_results = CombinedResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/jisho_kotobank_combined_results.json')
print(combined_results.simple_repr)