from jp_dict.parsing.koohii import KoohiiResultList
from jp_dict.anki.connect import AnkiConnect

orig_results = KoohiiResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/koohii_filtered.json')
# results = orig_results[:100]

anki_connect = AnkiConnect()
anki_connect.delete_deck(deck=anki_connect.get_deck_names(exclude_default=True))
anki_connect.clear_unused_tags()

# if 'parsed_kanji' not in anki_connect.get_model_names():
#     anki_connect.create_parsed_kanji_model()
# else:
#     anki_connect.update_parsed_kanji_templates_and_styling()

# # anki_connect.create_deck(deck='parsed_kanji_test')
# anki_connect.add_or_update_parsed_kanji_notes(
#     deck_name='parsed_kanji_test',
#     fields_list=results.to_kanji_fields()
# )
# results += orig_results[100:200]
# for result in results:
#     result.hit_count += 100
# anki_connect.add_or_update_parsed_kanji_notes(
#     deck_name='parsed_kanji_test',
#     fields_list=results.to_kanji_fields()
# )
# anki_connect.gui_card_browse(query='deck:parsed_kanji_test')

orig_results[0:100].add_or_update_anki(deck_name='new_kanji_deck')
orig_results[50:150].add_or_update_anki(deck_name='new_kanji_deck', open_browser=True)