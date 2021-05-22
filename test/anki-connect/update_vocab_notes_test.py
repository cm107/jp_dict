from jp_dict.anki.connect import AnkiConnect
from jp_dict.parsing.combined.combined_structs import CombinedResultList

deck_name = 'parsed_vocab_test'
changelog_path = 'vocab_changes.json'
orig_results = CombinedResultList.load_from_path('/home/clayton/workspace/prj/data_keep/data/study/parse_data/filter_sorted_results.json')

anki_connect = AnkiConnect(changelog_path=changelog_path)
if deck_name in anki_connect.get_deck_names(exclude_default=True):
    anki_connect.delete_deck(deck=deck_name)
anki_connect.clear_unused_tags()

orig_results[0:100].add_or_update_anki(deck_name=deck_name, anki_connect=anki_connect)
orig_results[50:150].add_or_update_anki(deck_name=deck_name, open_browser=False, anki_connect=anki_connect)

# anki_connect.save_changelog()
anki_connect.changelog.write_to_txt('vocab_changes.txt')