from ...submodules.logger.logger_handler import logger
from ..vocab_entry import VocabularyEntry
from ..jap_vocab import JapaneseVocab
from ..concept import ConceptLabels
from ..word_results import WordResult
from ..jap_vocab import OtherForm

def get_match_data(word: WordResult) -> (JapaneseVocab, ConceptLabels, VocabularyEntry):
    return word.jap_vocab, word.concept_labels, word.vocab_entry

def word_result_buffer(word: WordResult) -> WordResult:
    return word

def other_form_buffer(other_form: OtherForm) -> OtherForm:
    return other_form

class WordMatchFilter:
    @classmethod
    def filter_by_match_count(self, matching_results: list, target: int, ineq: str='=='):
        result = []
        for matching_result in matching_results:
            search_word = matching_result['search_word']
            matches = matching_result['matching_results']
            if ineq == '==':
                if len(matches) == target:
                    result.append(matching_result)
            elif ineq == '>':
                if len(matches) > target:
                    result.append(matching_result)
            elif ineq == '<':
                if len(matches) < target:
                    result.append(matching_result)
            elif ineq == '>=':
                if len(matches) >= target:
                    result.append(matching_result)
            elif ineq == '<=':
                if len(matches) <= target:
                    result.append(matching_result)
            else:
                logger.error(f"Invalid ineq: {ineq}")
                raise Exception
        return result

    @classmethod
    def filter_by_concept_labels_exist(self, matching_results: list):
        result = []
        for matching_result in matching_results:
            search_word = matching_result['search_word']
            matches = matching_result['matching_results']
            relevant_words = []
            for word in matches:
                jap_vocab, concept_labels, vocab_entry = get_match_data(word)
                if concept_labels is not None:
                    relevant_words.append(word)
            if len(relevant_words) > 0:
                filtered_matching_result = {'search_word': search_word, 'matching_results': relevant_words}
                result.append(filtered_matching_result)
        return result

    @classmethod
    def filter_by_common_words(self, matching_results: list, target: bool=True):
        result = []
        for matching_result in matching_results:
            search_word = matching_result['search_word']
            matches = matching_result['matching_results']
            relevant_words = []
            for word in matches:
                jap_vocab, concept_labels, vocab_entry = get_match_data(word)
                if concept_labels is None and target == True:
                    continue
                elif concept_labels is None and target == False:
                    relevant_words.append(word)
                elif concept_labels.is_common_word == target:
                    relevant_words.append(word)
            if len(relevant_words) > 0:
                filtered_matching_result = {'search_word': search_word, 'matching_results': relevant_words}
                result.append(filtered_matching_result)
        return result

    @classmethod
    def filter_by_jlpt_level(self, matching_results: list, target: int, ineq: str):
        """
        Valid jlpt targets: 1, 2, 3, 4, 5
        Non-jlpt target: -1
        """
        result = []
        for matching_result in matching_results:
            relevant_words = []
            search_word = matching_result['search_word']
            matches = matching_result['matching_results']
            for word in matches:
                jap_vocab, concept_labels, vocab_entry = get_match_data(word)
                if concept_labels is None and target != -1:
                    continue
                elif concept_labels is None and target == -1 and ineq == '==':
                    relevant_words.append(word)
                    continue
                level = concept_labels.jlpt_level
                if level is None and target != -1:
                    continue
                elif level is None and target == -1 and ineq == '==':
                    relevant_words.append(word)
                    continue

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
                filtered_matching_result = {'search_word': search_word, 'matching_results': relevant_words}
                result.append(filtered_matching_result)
        return result

    @classmethod
    def filter_by_wanikani_level(self, matching_results: list, target: int, ineq: str):
        result = []
        for matching_result in matching_results:
            relevant_words = []
            search_word = matching_result['search_word']
            matches = matching_result['matching_results']
            for word in matches:
                jap_vocab, concept_labels, vocab_entry = get_match_data(word)
                if concept_labels is None and target != -1:
                    continue
                elif concept_labels is None and target == -1 and ineq == '==':
                    relevant_words.append(word)
                    continue
                level = concept_labels.wanikani_level
                if level is None and target != -1:
                    continue
                elif level is None and target == -1 and ineq == '==':
                    relevant_words.append(word)
                    continue

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
                filtered_matching_result = {'search_word': search_word, 'matching_results': relevant_words}
                result.append(filtered_matching_result)
        return result

class LearnedFilter:
    @classmethod
    def get_unlearned(self, matching_results: list, learned_list: list):
        result = []
        for matching_result in matching_results:
            relevant_words = []
            search_word = matching_result['search_word']
            matches = matching_result['matching_results']
            if search_word not in learned_list:
                for word in matches:
                    word = word_result_buffer(word)
                    if word.jap_vocab.writing not in learned_list and word.jap_vocab.reading not in learned_list:
                        if word.vocab_entry.other_forms is not None:
                            for other_form in word.vocab_entry.other_forms.other_form_list:
                                other_form = other_form_buffer(other_form)
                                if other_form.kanji_writing not in learned_list and other_form.kana_writing not in learned_list:
                                    relevant_words.append(word)
                                    break
                        else:
                            relevant_words.append(word)
            if len(relevant_words) > 0:
                filtered_matching_result = {'search_word': search_word, 'matching_results': relevant_words}
                result.append(filtered_matching_result)
        return result

class WordMatchSorter:
    @classmethod
    def sort_by_common_words(self, matching_results: list, mode: str='common_first'):
        """
        mode options: 'common_first', 'uncommon_first'
        """
        result = []
        common_results = WordMatchFilter.filter_by_common_words(matching_results, target=True)
        uncommon_results = WordMatchFilter.filter_by_common_words(matching_results, target=False)
        if mode == 'common_first':
            result.extend(common_results)
            result.extend(uncommon_results)
        elif mode == 'uncommon_first':
            result.extend(uncommon_results)
            result.extend(common_results)
        else:
            logger.error(f"Invalid mode: {mode}")
            raise Exception
        return result

    @classmethod
    def sort_by_jlpt_level(self, matching_results: list, mode: str='ascending', non_jlpt: str='second'):
        """
        mode options: 'ascending', 'descending'
        non_jlpt options: 'first', 'second'
        """
        result = []
        jlpt_results_list = []
        level = -1
        while True:
            level += 1
            jlpt_results_list.append(WordMatchFilter.filter_by_jlpt_level(matching_results, target=level, ineq='=='))
            higher_level_results = WordMatchFilter.filter_by_jlpt_level(matching_results, target=level, ineq='>')
            if len(higher_level_results) == 0:
                break

        non_jlpt_results = WordMatchFilter.filter_by_jlpt_level(matching_results, target=-1, ineq='==')
        jlpt_results = []
        if mode == 'ascending':
            pass
        elif mode == 'descending':
            jlpt_results_list.reverse()
        else:
            logger.error(f"Invalid mode: {mode}")
            raise Exception
        for jlpt_results_item in jlpt_results_list:
            jlpt_results.extend(jlpt_results_item)
        
        if non_jlpt == 'first':
            result.extend(non_jlpt_results)
            result.extend(jlpt_results)
        elif non_jlpt == 'second':
            result.extend(jlpt_results)
            result.extend(non_jlpt_results)
        else:
            logger.error(f"Invalid value for non_jlpt: {non_jlpt}")
            raise Exception

        return result

    @classmethod
    def sort_by_wanikani_level(self, matching_results: list, mode: str='ascending', non_wanikani: str='second'):
        """
        mode options: 'ascending', 'descending'
        non_wanikani options: 'first', 'second'
        """
        result = []
        wanikani_results_list = []
        level = -1
        while True:
            level += 1
            current_level_results = WordMatchFilter.filter_by_wanikani_level(matching_results, target=level, ineq='==')
            wanikani_results_list.append(current_level_results)
            higher_level_results = WordMatchFilter.filter_by_wanikani_level(matching_results, target=level, ineq='>')
            if len(higher_level_results) == 0:
                break

        non_wanikani_results = WordMatchFilter.filter_by_wanikani_level(matching_results, target=-1, ineq='==')

        wanikani_results = []
        if mode == 'ascending':
            pass
        elif mode == 'descending':
            wanikani_results_list.reverse()
        else:
            logger.error(f"Invalid mode: {mode}")
            raise Exception
        for wanikani_results_item in wanikani_results_list:
            wanikani_results.extend(wanikani_results_item)
        if non_wanikani == 'first':
            result.extend(non_wanikani_results)
            result.extend(wanikani_results)
        elif non_wanikani == 'second':
            result.extend(wanikani_results)
            result.extend(non_wanikani_results)
        else:
            logger.error(f"Invalid value for non_wanikani: {non_wanikani}")
            raise Exception

        return result