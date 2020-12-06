from jp_dict.parsing.kotobank.kotobank_structs import KotobankResultList

results = KotobankResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/kotobank_combined.json')
print(len(results))
raise NotImplementedError