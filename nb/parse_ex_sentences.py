import pickle
from src.conf.paths import PathConf
from src.util.loaders import load_word_matches
from src.lib.history_parsing.word_match_filter import default_filter

# jlpt_all_notes_save_path = f"{PathConf.anki_dir}/jlpt_all_save.pkl"
# jlpt_all_vocab_list = pickle.load(open(jlpt_all_notes_save_path, 'rb'))
# anime_vocab_notes_save_path = f"{PathConf.anki_dir}/anime_vocab_save.pkl"
# anime_vocab_vocab_list = pickle.load(open(anime_vocab_notes_save_path, 'rb'))

# word_matches_save_path = f"{PathConf.word_matches_save_dir}/test.pkl"
# matching_results = load_word_matches(word_matches_save_path)
# filtered_results = default_filter(matching_results=matching_results, learned_lists=[jlpt_all_vocab_list, anime_vocab_vocab_list])

import json
from logger import logger
from common_utils.adv_file_utils import get_dirpaths_in_dir
from common_utils.check_utils import check_file_exists
ex_sentence_dirpaths = get_dirpaths_in_dir(dir_path=PathConf.ex_sentences_dir)

for ex_sentence_dirpath in ex_sentence_dirpaths:
    logger.cyan(f"ex_sentence_dirpath: {ex_sentence_dirpath}")
    index_path = f"{ex_sentence_dirpath}/index.json"
    check_file_exists(index_path)
    index_dict = json.load(open(index_path, 'r'))
    index_dict = json.dumps(index_dict, indent=2, ensure_ascii=False)
    logger.purple(index_dict)