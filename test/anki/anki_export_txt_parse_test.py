from jp_dict.parsing.anki.export_txt_parser import AnkiExportTextData

root_dir = '/home/clayton/workspace/prj/data_keep/data/study/anki'
jlpt_vocab_path = f'{root_dir}/jlpt_vocab.txt'
anime_vocab_path = f'{root_dir}/anime_vocab.txt'

jlpt_vocab_data = AnkiExportTextData.parse_from_txt(jlpt_vocab_path)
print(f'len(jlpt_vocab_data): {len(jlpt_vocab_data)}')
# print(jlpt_vocab_data)

anime_vocab_data = AnkiExportTextData.parse_from_txt(anime_vocab_path)
print(f'len(anime_vocab_data): {len(anime_vocab_data)}')

print(jlpt_vocab_data.contains(writing='作る', reading='つくる'))
# print(anime_vocab_data)