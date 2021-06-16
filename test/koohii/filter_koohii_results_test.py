from jp_dict.parsing.koohii import KoohiiResultList
from jp_dict.parsing.anki.export_txt_parser import parse_kanji_anki_export

results = KoohiiResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/koohii_combined.json')

root_dir = '/home/clayton/workspace/prj/data_keep/data/study/anki'
nihongoshark_kanji_list = parse_kanji_anki_export(
    path=f'{root_dir}/nihongoshark_kanji.txt',
    field_idx=4
)
anime_kanji_list = parse_kanji_anki_export(
    path=f'{root_dir}/anime_kanji.txt',
    field_idx=0
)
misc_kanji_list = ['々']
combined_kanji_list = nihongoshark_kanji_list + anime_kanji_list + misc_kanji_list

combined_kanji_list_save_path = f'{root_dir}/learned_kanji_combined.txt'
f = open(combined_kanji_list_save_path, 'w')
for i, kanji in enumerate(combined_kanji_list):
    if i == 0:
        f.write(kanji)
    else:
        f.write(f'\n{kanji}')
f.close()

filtered_results = results.filter_out_kanji(combined_kanji_list)
filtered_results.save_to_path('filtered_results.json', overwrite=True)
print(f'len(filtered_results): {len(filtered_results)}')