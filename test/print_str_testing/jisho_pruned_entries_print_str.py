from jp_dict.parsing.jisho.jisho_matches import DictionaryEntryMatchList

kotobank_dump_dir = '/home/clayton/workspace/prj/data_keep/data/study/parse_data/kotobank_parse_dump'
pruned_jisho_entries_path = '/home/clayton/workspace/prj/data_keep/data/study/parse_data/pruned_jisho_entries.json'
pruned_jisho_entries = DictionaryEntryMatchList.load_from_path(pruned_jisho_entries_path)
# pruned_jisho_entries = DictionaryEntryMatchList([entry for entry in pruned_jisho_entries if len(entry.linked_kotobank_queries) > 1])

print(len(pruned_jisho_entries))
print(pruned_jisho_entries.custom_str())