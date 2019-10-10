from src.conf.paths import PathConf
from src.util.loaders import load_word_matches
from src.lib.vocab_entry import VocabularyEntry
from src.lib.jap_vocab import JapaneseVocab
from src.lib.concept import ConceptLabels
from src.lib.word_results import WordResult
from src.submodules.logger.logger_handler import logger

word_matches_save_path = f"{PathConf.word_matches_save_dir}/test.pkl"
matching_results = load_word_matches(word_matches_save_path)

multiple_match_count = 0

def get_match_data(word: WordResult) -> (JapaneseVocab, ConceptLabels, VocabularyEntry):
    return word.jap_vocab, word.concept_labels, word.vocab_entry

from src.lib.history_parsing.word_match_filter import WordMatchFilter, WordMatchSorter
# matching_results = WordMatchFilter.filter_by_jlpt_level(matching_results, target=5, ineq='<=')
# matching_results = WordMatchFilter.filter_by_common_words(matching_results, target=False)
# matching_results = WordMatchFilter.filter_by_match_count(matching_results, target=1, ineq='==')

common_matching_results = WordMatchFilter.filter_by_common_words(matching_results, target=True)
common_matching_results = WordMatchFilter.filter_by_match_count(common_matching_results, target=1, ineq='==')
common_matching_results = WordMatchSorter.sort_by_wanikani_level(common_matching_results, mode='ascending', non_wanikani='second')
common_matching_results = WordMatchSorter.sort_by_jlpt_level(common_matching_results, mode='descending', non_jlpt='second')
uncommon_matching_results = WordMatchFilter.filter_by_common_words(matching_results, target=False)
uncommon_matching_results = WordMatchFilter.filter_by_match_count(uncommon_matching_results, target=1, ineq='==')
uncommon_matching_results = WordMatchSorter.sort_by_wanikani_level(uncommon_matching_results, mode='ascending', non_wanikani='second')
uncommon_matching_results = WordMatchSorter.sort_by_jlpt_level(uncommon_matching_results, mode='descending', non_jlpt='second')

results = []
results.extend(common_matching_results)
results.extend(uncommon_matching_results)

logger.cyan(f"len(results): {len(results)}")
for i, matching_result in zip(range(len(results)), results):
    search_word = matching_result['search_word']
    matches = matching_result['matching_results']
    logger.yellow(f"============{i}: {search_word}============")
    for i, word in zip(range(len(matches)), matches):
        if i > 0:
            logger.purple(f"--------------------------")
        logger.blue(word)

