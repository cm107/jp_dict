from src.conf.paths import PathConf
from src.lib.history_parsing.word_match_saver import SoupWordMatchSaver

# TODO: Create SoupWordMatchSaver and SearchWordMatchSaver

worker = SoupWordMatchSaver(
    progress_save_path=f"{PathConf.jisho_soup_root_dir}/progress.pth",
    word_matches_save_path=f"{PathConf.word_matches_save_dir}/soup_test0.pkl"
)
worker.run()