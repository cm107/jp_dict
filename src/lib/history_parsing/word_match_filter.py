from ...submodules.logger.logger_handler import logger
from ..vocab_entry import VocabularyEntry
from ..jap_vocab import JapaneseVocab
from ..concept import ConceptLabels
from ..word_results import WordResult

def get_match_data(word: WordResult) -> (JapaneseVocab, ConceptLabels, VocabularyEntry):
    return word.jap_vocab, word.concept_labels, word.vocab_entry

class WordMatchFilter:
    @classmethod
    def filter_by_match_count(self, matching_results_dict: dict, target: int, ineq: str='=='):
        result = {}
        for key, matching_results in matching_results_dict.items():
            if ineq == '==':
                if len(matching_results) == target:
                    result[key] = matching_results
            elif ineq == '>':
                if len(matching_results) > target:
                    result[key] = matching_results
            elif ineq == '<':
                if len(matching_results) < target:
                    result[key] = matching_results
            elif ineq == '>=':
                if len(matching_results) >= target:
                    result[key] = matching_results
            elif ineq == '<=':
                if len(matching_results) <= target:
                    result[key] = matching_results
            else:
                logger.error(f"Invalid ineq: {ineq}")
                raise Exception
        return result

    @classmethod
    def filter_by_concept_labels_exist(self, matching_results_dict: dict):
        result = {}
        for key, matching_results in matching_results_dict.items():
            relevant_words = []
            for word in matching_results:
                jap_vocab, concept_labels, vocab_entry = get_match_data(word)
                if concept_labels is not None:
                    relevant_words.append(word)
            if len(relevant_words) > 0:
                result[key] = relevant_words
        return result

    @classmethod
    def filter_by_common_words(self, matching_results_dict: dict, target: bool=True):
        result = {}
        for key, matching_results in matching_results_dict.items():
            relevant_words = []
            for word in matching_results:
                jap_vocab, concept_labels, vocab_entry = get_match_data(word)
                if concept_labels is None:
                    continue
                if concept_labels.is_common_word == target:
                    relevant_words.append(word)
            if len(relevant_words) > 0:
                result[key] = relevant_words
        return result

    @classmethod
    def filter_by_jlpt_level(self, matching_results_dict: dict, target: int, ineq: str):
        result = {}
        for key, matching_results in matching_results_dict.items():
            relevant_words = []
            for word in matching_results:
                jap_vocab, concept_labels, vocab_entry = get_match_data(word)
                if concept_labels is None:
                    continue
                level = concept_labels.jlpt_level
                if ineq == '==':
                    if level is not None and level == target:
                        relevant_words.append(word)
                elif ineq == '>':
                    if level is not None and level > target:
                        relevant_words.append(word)
                elif ineq == '<':
                    if level is not None and level < target:
                        relevant_words.append(word)
                elif ineq == '>=':
                    if level is not None and level >= target:
                        relevant_words.append(word)
                elif ineq == '<=':
                    if level is not None and level <= target:
                        relevant_words.append(word)
                else:
                    logger.error(f"Invalid ineq: {ineq}")
                    raise Exception
            if len(relevant_words) > 0:
                result[key] = relevant_words
        return result

    @classmethod
    def filter_by_wanikani_level(self, matching_results_dict: dict, target: int, ineq: str):
        result = {}
        for key, matching_results in matching_results_dict.items():
            relevant_words = []
            for word in matching_results:
                jap_vocab, concept_labels, vocab_entry = get_match_data(word)
                if concept_labels is None:
                    continue
                level = concept_labels.wanikani_level
                if ineq == '==':
                    if level is not None and level == target:
                        relevant_words.append(word)
                elif ineq == '>':
                    if level is not None and level > target:
                        relevant_words.append(word)
                elif ineq == '<':
                    if level is not None and level < target:
                        relevant_words.append(word)
                elif ineq == '>=':
                    if level is not None and level >= target:
                        relevant_words.append(word)
                elif ineq == '<=':
                    if level is not None and level <= target:
                        relevant_words.append(word)
                else:
                    logger.error(f"Invalid ineq: {ineq}")
                    raise Exception
            if len(relevant_words) > 0:
                result[key] = relevant_words
        return result