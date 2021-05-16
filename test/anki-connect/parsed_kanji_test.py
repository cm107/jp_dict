from jp_dict.anki.connect import AnkiConnect
from jp_dict.anki.note_structs import NoteAddParamList
from jp_dict.parsing.koohii import KoohiiResultList

results = KoohiiResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/koohii_filtered.json')
# results = results[:100]

anki_connect = AnkiConnect()
anki_connect.delete_deck(deck=anki_connect.get_deck_names(exclude_default=True))
anki_connect.clear_unused_tags()

if 'parsed_kanji' not in anki_connect.get_model_names():
    anki_connect.create_parsed_kanji_model()
else:
    anki_connect.update_parsed_kanji_templates_and_styling()

anki_connect.create_deck(deck='parsed_kanji_test')
anki_connect.add_note_sequence(
    NoteAddParamList.parsed_kanji(
        deck_name='parsed_kanji_test',
        fields_list=results.to_kanji_fields()
    )
)
anki_connect.gui_card_browse(query='deck:parsed_kanji_test')