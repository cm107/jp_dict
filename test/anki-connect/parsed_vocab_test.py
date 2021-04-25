from jp_dict.anki.connect import AnkiConnect
from jp_dict.anki.note_structs import NoteAddParamList
from jp_dict.parsing.combined.combined_structs import CombinedResultList

results = CombinedResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/jisho_kotobank_combined_results.json')

anki_connect = AnkiConnect()
anki_connect.delete_deck(deck=anki_connect.get_deck_names(exclude_default=True))
anki_connect.clear_unused_tags()

if 'parsed_vocab' not in anki_connect.get_model_names():
    anki_connect.create_parsed_vocab_model()
anki_connect.create_deck(deck='parsed_vocab_test')
anki_connect.add_note_sequence(
    NoteAddParamList.parsed_vocab(
        deck_name='parsed_vocab_test',
        fields_list=results.to_vocabulary_fields_list()
    )
)