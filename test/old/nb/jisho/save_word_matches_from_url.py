from src.conf.paths import PathConf
from src.lib.history_parsing.word_match_saver import SearchWordMatchSaver

worker = SearchWordMatchSaver(
    cache_save_path=f"{PathConf.jisho_history_word_list_save_path}",
    word_matches_save_path=f"{PathConf.word_matches_save_dir}/test.pkl"
)
worker.run(use_bar=True)