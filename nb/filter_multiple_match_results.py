from src.conf.paths import PathConf
from src.util.loaders import load_word_matches
from src.submodules.logger.logger_handler import logger
from src.lib.history_parsing.word_match_filter import WordMatchFilter, WordMatchSorter

word_matches_save_path = f"{PathConf.word_matches_save_dir}/test.pkl"
matching_results = load_word_matches(word_matches_save_path)

# logger.purple(f"len(matching_results): {len(matching_results)}")
filtered_results = WordMatchFilter.filter_by_match_count(matching_results, target=1, ineq='==')
# logger.purple(f"len(filtered_results): {len(filtered_results)}")
filtered_results = WordMatchSorter.sort_by_wanikani_level(filtered_results, mode='ascending', non_wanikani='second')
# logger.purple(f"len(filtered_results): {len(filtered_results)}")
filtered_results = WordMatchSorter.sort_by_jlpt_level(filtered_results, mode='descending', non_jlpt='second')
# logger.purple(f"len(filtered_results): {len(filtered_results)}")
filtered_results = WordMatchSorter.sort_by_common_words(filtered_results, mode='common_first')
# logger.purple(f"len(filtered_results): {len(filtered_results)}")

logger.cyan(f"len(filtered_results): {len(filtered_results)}")
for i, matching_result in zip(range(len(filtered_results)), filtered_results):
    search_word = matching_result['search_word']
    matches = matching_result['matching_results']
    logger.yellow(f"============{i}: {search_word}============")
    for i, word in zip(range(len(matches)), matches):
        if i > 0:
            logger.purple(f"--------------------------")
        logger.blue(word)

