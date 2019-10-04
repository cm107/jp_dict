from src.conf.paths import PathConf
from src.util.loaders import load_word_matches
from src.lib.vocab_entry import VocabularyEntry
from src.lib.jap_vocab import JapaneseVocab
from src.lib.concept import ConceptLabels
from src.lib.word_results import WordResult
from src.submodules.logger.logger_handler import logger

word_matches_save_path = f"{PathConf.word_matches_save_dir}/test.pkl"
matching_results_dict = load_word_matches(word_matches_save_path)

multiple_match_count = 0

# jap_vocab: JapaneseVocab, concept_labels: ConceptLabels, vocab_entry: VocabularyEntry
def get_match_data(word: WordResult) -> (JapaneseVocab, ConceptLabels, VocabularyEntry):
    return word.jap_vocab, word.concept_labels, word.vocab_entry

from src.lib.history_parsing.word_match_filter import WordMatchFilter
matching_results_dict = WordMatchFilter.filter_by_match_count(matching_results_dict, target=1, ineq='>')
matching_results_dict = WordMatchFilter.filter_by_jlpt_level(matching_results_dict, target=5, ineq='<=')
matching_results_dict = WordMatchFilter.filter_by_common_words(matching_results_dict, target=True)

logger.cyan(f"len(matching_results_dict): {len(matching_results_dict)}")
for i, key, matching_results in zip(range(len(matching_results_dict)), matching_results_dict.keys(), matching_results_dict.values()):
    logger.yellow(f"============{i}: {key}============")
    for i, word in zip(range(len(matching_results)), matching_results):
        if i > 0:
            logger.purple(f"--------------------------")
        logger.blue(word)

