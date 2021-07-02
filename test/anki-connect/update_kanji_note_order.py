from jp_dict.parsing.koohii import KoohiiResultList
from jp_dict.anki.connect import AnkiConnect

deck_name = 'parsed_kanji'
changelog_path = 'parsed_kanji_order_change.json'
results = KoohiiResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/koohii_filtered.json')

anki_connect = AnkiConnect(changelog_path=changelog_path)

results.add_or_update_anki(deck_name=deck_name, anki_connect=anki_connect)

# anki_connect.save_changelog()
anki_connect.changelog.write_to_txt('changelog_dump/parsed_kanji_order_change.txt')