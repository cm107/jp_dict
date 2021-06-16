from jp_dict.anki.connect import AnkiConnect
from jp_dict.anki.note_structs import BasicFields

anki_connect = AnkiConnect()
anki_connect.delete_deck(deck=anki_connect.get_deck_names(exclude_default=True))
anki_connect.clear_unused_tags()
anki_connect.create_deck('test0')
print(f'anki_connect.get_deck_names(): {anki_connect.get_deck_names()}')
deck2id = anki_connect.get_deck_names_and_ids()
note_id = anki_connect.add_basic_simple_note(
    deck_name='test0',
    front='basic test - front',
    back='basic test - back'
)
print(f'note_id: {note_id}')
note_ids = anki_connect.add_notes_from_basic_dict_list(
    deck_name='test0',
    basic_dict_list=[
        {
            'Front': 'Front A',
            'Back': 'Back A'
        },
        {
            'Front': 'Front B',
            'Back': 'Back B'
        },
        {
            'Front': 'Front C',
            'Back': 'Back C'
        },
    ]
)
anki_connect.add_basic_simple_note(deck_name='test0', front='extra front', back='extra back')
print(f'note_ids: {note_ids}')
anki_connect.update_note_fields(note_id=note_ids[-1], fields=BasicFields(front='Front D', back='Back D'))

print(anki_connect.find_notes('-front:"basic_test*"'))
anki_connect.add_tag(
    note_ids=anki_connect.find_notes('front:basic_test*'),
    tag='primary'
)
anki_connect.add_tag(
    note_ids=anki_connect.find_notes('-front:"basic_test*"'),
    tag='secondary'
)
print(f'anki_connect.get_tags(): {anki_connect.get_tags()}')
notes_result = anki_connect.get_notes_info(anki_connect.find_notes('tag:secondary'))
print(f'notes_result: {notes_result}')