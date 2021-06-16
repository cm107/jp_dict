from tqdm import tqdm
from common_utils.file_utils import file_exists
from jp_dict.parsing.jisho.jisho_matches import DictionaryEntryMatchList
from jp_dict.parsing.kotobank.kotobank_structs import KotobankResult

parse_data_dir = '/home/clayton/workspace/prj/data_keep/data/study/parse_data'
kotobank_parse_dump_dir = f'{parse_data_dir}/kotobank_parse_dump'
entry_matches = DictionaryEntryMatchList.load_from_path(f'{parse_data_dir}/pruned_jisho_entries.json')
missing_kotobank_result_count = 0
relevant_entry_matches = DictionaryEntryMatchList()
pbar = tqdm(total=len(entry_matches), unit='entries', leave=True)
for entry_match in entry_matches:
    non_empty_count = 0
    has_other_forms = entry_match.entry.meaning_section.other_forms is not None and len(entry_match.entry.meaning_section.other_forms) > 0
    writing_repr = entry_match.entry.word_representation.writing
    has_unsearched_writing = not file_exists(f'{kotobank_parse_dump_dir}/{writing_repr}.json') and writing_repr is not None
    has_unsearched_other_form = False
    if has_other_forms:
        for other_form in entry_match.entry.meaning_section.other_forms:
            other_form_writing_repr = other_form.writing
            if not file_exists(f'{kotobank_parse_dump_dir}/{other_form_writing_repr}.json') and other_form_writing_repr is not None:
                has_unsearched_other_form = True
    # is_relevant = has_unsearched_writing or has_unsearched_other_form
    is_relevant = has_unsearched_writing
    for search_word in entry_match.search_words:
        kotobank_result_path = f'{kotobank_parse_dump_dir}/{search_word}.json'
        assert file_exists(kotobank_result_path)
        kotobank_result = KotobankResult.load_from_path(kotobank_result_path)
        if not kotobank_result.is_empty:
            non_empty_count += 1
    if non_empty_count == 0:
        missing_kotobank_result_count += 1
        if is_relevant:
            relevant_entry_matches.append(entry_match)
    pbar.update()
pbar.close()

for relevant_entry_match in relevant_entry_matches:
    writing_repr_str = relevant_entry_match.entry.word_representation.writing
    other_forms_str = str(relevant_entry_match.entry.meaning_section.other_forms)
    print(f'{relevant_entry_match.search_words}')
    print(f'\t->{writing_repr_str}')
    print(f'\t-> {other_forms_str}')
print(f'missing_kotobank_result_count: {missing_kotobank_result_count}')
print(f'relevant_proportion: {len(relevant_entry_matches)}/{missing_kotobank_result_count}')