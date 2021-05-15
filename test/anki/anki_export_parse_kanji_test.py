from jp_dict.parsing.anki.export_txt_parser import parse_kanji_anki_export

root_dir = '/home/clayton/workspace/prj/data_keep/data/study/anki'

nihongoshark_kanji_list = parse_kanji_anki_export(
    path=f'{root_dir}/nihongoshark_kanji.txt',
    field_idx=4
)
anime_kanji_list = parse_kanji_anki_export(
    path=f'{root_dir}/anime_kanji.txt',
    field_idx=0
)

# print(nihongoshark_kanji_list)
print(anime_kanji_list)