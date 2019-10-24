import pickle
from src.conf.paths import PathConf
from src.util.loaders import load_word_matches
from logger import logger
from src.lib.history_parsing.word_match_filter import WordMatchFilter, WordMatchSorter, LearnedFilter
from src.lib.word_results import WordResult
from src.lib.jap_vocab import OtherForm

jlpt_all_notes_save_path = f"{PathConf.anki_dir}/jlpt_all_save.pkl"
jlpt_all_vocab_list = pickle.load(open(jlpt_all_notes_save_path, 'rb'))
anime_vocab_notes_save_path = f"{PathConf.anki_dir}/anime_vocab_save.pkl"
anime_vocab_vocab_list = pickle.load(open(anime_vocab_notes_save_path, 'rb'))

word_matches_save_path = f"{PathConf.word_matches_save_dir}/test.pkl"
matching_results = load_word_matches(word_matches_save_path)

filtered_results = WordMatchFilter.filter_by_match_count(matching_results, target=1, ineq='==')
filtered_results = WordMatchSorter.sort_by_wanikani_level(filtered_results, mode='ascending', non_wanikani='second')
filtered_results = WordMatchSorter.sort_by_jlpt_level(filtered_results, mode='descending', non_jlpt='second')
filtered_results = WordMatchSorter.sort_by_common_words(filtered_results, mode='common_first')
filtered_results = LearnedFilter.get_unlearned(filtered_results, learned_list=jlpt_all_vocab_list)
filtered_results = LearnedFilter.get_unlearned(filtered_results, learned_list=anime_vocab_vocab_list)

logger.cyan(f"len(filtered_results): {len(filtered_results)}")
for i, matching_result in zip(range(len(filtered_results)), filtered_results):
    search_word = matching_result['search_word']
    matches = matching_result['matching_results']
    logger.yellow(f"============{i}: {search_word}============")
    for i, word in zip(range(len(matches)), matches):
        if i > 0:
            logger.purple(f"--------------------------")
        logger.blue(word)

logger.link_log_dir(PathConf.logs_dir)