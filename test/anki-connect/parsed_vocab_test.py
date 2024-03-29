from jp_dict.anki.connect import AnkiConnect
from jp_dict.anki.note_structs import NoteAddParamList
from jp_dict.parsing.combined.combined_structs import CombinedResultList

deck_name = 'parsed_vocab_test'
results = CombinedResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/filter_sorted_results.json')
results = results[:100]
# print(results.custom_str())
# import sys
# sys.exit()

anki_connect = AnkiConnect()
# print(anki_connect.get_model_templates(model_name='parsed_vocab'))
# import sys
# sys.exit()
if deck_name in anki_connect.get_deck_names(exclude_default=True):
    anki_connect.delete_deck(deck=deck_name)
anki_connect.clear_unused_tags()

if 'parsed_vocab' not in anki_connect.get_model_names():
    anki_connect.create_parsed_vocab_model()
else:
    anki_connect.update_parsed_vocab_templates_and_styling()

anki_connect.create_deck(deck=deck_name)
anki_connect.add_note_sequence(
    NoteAddParamList.parsed_vocab(
        deck_name=deck_name,
        fields_list=results.to_vocabulary_fields_list()
    )
)
anki_connect.gui_card_browse(query=f'deck:{deck_name}')