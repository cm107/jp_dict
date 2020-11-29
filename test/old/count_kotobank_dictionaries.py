from src.refactored.kotobank.kotobank_structs import KotobankResultList

# デジタル大辞泉の解説 +4408 (original 4408) Implemented
# 精選版 日本国語大辞典の解説 +147 (original 3095) TODO
# 大辞林 第三版の解説 +93 (original 3982) TODO
# 日本大百科全書(ニッポニカ)の解説 + 43
# デジタル大辞泉プラスの解説 +28 (Don't really need it.)
# ブリタニカ国際大百科事典 小項目事典の解説 +21

results = KotobankResultList.load_from_dir('kotobank_dump')

priority_dict = results.get_dictionary_priority_dict()
jsonable_dict = {}
for i, (dictionary_name, info_dict) in enumerate(priority_dict.items()):
    jsonable_dict[i] = {
        'dictionary_name': dictionary_name,
        'details': info_dict
    }

import json
json.dump(jsonable_dict, open('dictionary_priority.json', 'w'), indent=2, ensure_ascii=False)