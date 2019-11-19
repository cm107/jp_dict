import pickle
from src.conf.paths import PathConf
from src.util.loaders import load_word_matches
from src.lib.history_parsing.word_match_filter import default_filter
from src.lib.sentence_parsing.sentence_parsing_core import print_sentence_results

jlpt_all_notes_save_path = f"{PathConf.anki_dir}/jlpt_all_save.pkl"
jlpt_all_vocab_list = pickle.load(open(jlpt_all_notes_save_path, 'rb'))
anime_vocab_notes_save_path = f"{PathConf.anki_dir}/anime_vocab_save.pkl"
anime_vocab_vocab_list = pickle.load(open(anime_vocab_notes_save_path, 'rb'))

word_matches_save_path = f"{PathConf.word_matches_save_dir}/test.pkl"
matching_results = load_word_matches(word_matches_save_path)
filtered_results = default_filter(matching_results=matching_results, learned_lists=[jlpt_all_vocab_list, anime_vocab_vocab_list])

print_sentence_results(filtered_results=filtered_results, ex_sentence_root_dir=PathConf.ex_sentences_dir, search_mode=1)