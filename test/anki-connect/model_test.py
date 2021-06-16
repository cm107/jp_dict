from jp_dict.anki.connect import AnkiConnect
from jp_dict.anki.note_structs import NoteAddParamList, JapaneseStandardFieldsList, JapaneseStandardFields

anki_connect = AnkiConnect()
anki_connect.delete_deck(deck=anki_connect.get_deck_names(exclude_default=True))
anki_connect.clear_unused_tags()

# import sys
# sys.exit()

print(anki_connect.create_jp_standard_model())
print(f'anki_connect.get_model_names(): {anki_connect.get_model_names()}')

print('Field Names')
for model_name in anki_connect.get_model_names():
    field_names = anki_connect.get_model_field_names(model_name=model_name)
    print(f'{model_name}: {field_names}')

print('Fields On Templates')
for model_name in anki_connect.get_model_names():
    field_names = anki_connect.get_model_field_names_on_templates(model_name=model_name)
    print(f'{model_name}: {field_names}')

anki_connect.create_deck(deck='jp_standard_test')

anki_connect.add_notes(
    NoteAddParamList.jp_standard(
        deck_name='jp_standard_test',
        fields_list=JapaneseStandardFieldsList([
            JapaneseStandardFields(
                word='日本語',
                reading='にほんご',
                meaning='Japanese'
            ),
            JapaneseStandardFields(
                word='車',
                reading='くるま',
                meaning='car'
            )
        ])
    )
)