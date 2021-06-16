from jp_dict.parsing.kotobank.kotobank_structs import KotobankResultList
from logger import logger

results = KotobankResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/kotobank_combined.json').nonempty_results
print(f'len(results): {len(results)}\n\n')
print(results.custom_str(num_breaks=3))
# for result in results:
#     print(result.custom_str() + '\n')
#     # logger.cyan(result.main_title)
#     # print(result.main_alias_name)