import os
from datetime import datetime
from jp_dict.parsing.combined.combined_structs import CombinedResultList
from jp_dict.parsing.koohii import KoohiiResultList
from jp_dict.anki.connect import AnkiConnect

def anki_connect_session(func, parse_data_dir: str, changelog_dump_dir: str, clear_data_first: bool=False):
    def _sesson():
        if not os.path.isdir(changelog_dump_dir):
            os.mkdir(changelog_dump_dir)
        changelog_basename = datetime.now().strftime('%Y%m%d-%H%M%S%f')
        changelog_json_path = f'{changelog_dump_dir}/{changelog_basename}.json'
        changelog_txt_path = f'{changelog_dump_dir}/{changelog_basename}.txt'
        anki_connect = AnkiConnect(changelog_path=changelog_json_path)
        if clear_data_first:
            for deck_name in anki_connect.get_deck_names(exclude_default=True):
                anki_connect.delete_deck(deck=deck_name)
            anki_connect.clear_unused_tags()

        func(anki_connect=anki_connect, parse_data_dir=parse_data_dir)
        anki_connect.save_changelog()
        anki_connect.changelog.write_to_txt(changelog_txt_path)
    
    return _sesson

def update_all_data(anki_connect: AnkiConnect, parse_data_dir: str):
    vocab_results = CombinedResultList.load_from_path(f'{parse_data_dir}/filter_sorted_results.json')
    vocab_results.add_or_update_anki(
        deck_name='parsed_vocab', anki_connect=anki_connect,
        # update_daijisen=True, update_daijisen_plus=True,
        # update_seisenpan=True, update_ndz=True
    )
    kanji_results = KoohiiResultList.load_from_path(f'{parse_data_dir}/koohii_filtered.json')
    kanji_results.add_or_update_anki(deck_name='parsed_kanji', anki_connect=anki_connect)

changelog_dump_dir = 'changelog_dump'
# anki_connect_session(
#     func=update_all_data,
#     parse_data_dir='/home/clayton/workspace/prj/data_keep/data/study/parse_data0',
#     changelog_dump_dir=changelog_dump_dir,
#     clear_data_first=True
# )()
anki_connect_session(
    func=update_all_data,
    parse_data_dir='/home/clayton/workspace/prj/data_keep/data/study/parse_data',
    changelog_dump_dir=changelog_dump_dir
)()