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

resolved_results = []
unresolved_results = []

for i, key, matching_results in zip(
    range(len(matching_results_dict.keys())),
    matching_results_dict.keys(),
    matching_results_dict.values()
):
    if len(matching_results) > 1:
        logger.yellow(f"{i}: {key}")
        # logger.purple(f"matching_results:\n{matching_results}")
        multiple_match_count += 1
        logger.purple(f"Multiple Match Count: {multiple_match_count}")
        logger.cyan(matching_results)
        concept_hits = []
        concept_non_hits = []
        for word in matching_results:
            logger.purple(f"word:\n{word}")
            jap_vocab, concept_labels, vocab_entry = get_match_data(word)
            if concept_labels is not None:
                logger.blue(f"is_common_word: {concept_labels.is_common_word}")
                logger.blue(f"jlpt_level: {concept_labels.jlpt_level}")
                logger.blue(f"wanikani_level: {concept_labels.wanikani_level}")
                concept_hits.append(word)
            else:
                logger.blue(f"No concept labels.")
                concept_non_hits.append(word)
        concept_results = {'hits': concept_hits, 'non_hits': concept_non_hits}
        if len(concept_hits) == 1:
            resolved_results.append(concept_results)
        else:
            unresolved_results.append(concept_results)

# logger.yellow(f"Resolved Results:")
# for i, concept_results in zip(range(len(resolved_results)), resolved_results):
#     logger.cyan(i)
#     logger.blue(concept_results)

# logger.yellow(f"Unresolved Results:")
# for i, concept_results in zip(range(len(unresolved_results)), unresolved_results):
#     logger.cyan(i)
#     logger.blue(concept_results)

logger.yellow(f"len(resolved_results): {len(resolved_results)}")
logger.yellow(f"len(unresolved_results): {len(unresolved_results)}")