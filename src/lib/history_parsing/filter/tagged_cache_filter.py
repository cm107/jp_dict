from logger import logger
from common_utils.check_utils import check_value
from ....util.time_utils import get_days_elapsed_from_time_usec, get_years_elapsed_from_time_usec
from ...word_results import WordResult
from .core import TaggedCache
from ...jap_vocab import OtherForm

class TaggedCacheFilter:
    @classmethod
    def _filter_by_bool_tag(self, attr_name: str, tagged_cache_list: list, target: str, skip_empty_results: bool=False) -> list:
        check_value(target, valid_value_list=['true', 'false', 'none'])
        result = []
        for tagged_cache in tagged_cache_list:
            if skip_empty_results and len(tagged_cache.word_results) == 0:
                continue
            attr = getattr(tagged_cache, attr_name, 'dne')
            if attr == 'dne':
                logger.error(f"tagged_cache has no attribute: {attr_name}")
                raise Exception
            if callable(attr):
                bool_tag = attr()
            else:
                bool_tag = attr

            if bool_tag is None and target == 'none':
                result.append(tagged_cache)
            elif bool_tag and target == 'true':
                result.append(tagged_cache)
            elif not bool_tag and target == 'false':
                result.append(tagged_cache)
        return result

    @classmethod
    def _filter_by_jp_char_tag(self, attr_name: str, tagged_cache_list: list, target: str, skip_empty_results: bool=False) -> list:
        check_value(target, valid_value_list=['all', 'partial', 'none'])
        result = []
        for tagged_cache in tagged_cache_list:
            if skip_empty_results and len(tagged_cache.word_results) == 0:
                continue
            if tagged_cache.is_not_processed_for_japanese_chars_yet():
                logger.error(f"tagged_cache not labeled:\n{tagged_cache}")
                raise Exception
            
            attr = getattr(tagged_cache, attr_name, 'dne')
            if attr == 'dne':
                logger.error(f"tagged_cache has no attribute: {attr_name}")
                raise Exception
            if attr == target:
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_wildcard_tag(self, tagged_cache_list: list, target: str, skip_empty_results: bool=False) -> list:
        return self._filter_by_bool_tag(
            attr_name='contains_wildcard',
            tagged_cache_list=tagged_cache_list, target=target, skip_empty_results=skip_empty_results
        )

    @classmethod
    def filter_by_eng_chars_tag(self, tagged_cache_list: list, target: str, skip_empty_results: bool=False) -> list:
        return self._filter_by_bool_tag(
            attr_name='contains_eng_chars',
            tagged_cache_list=tagged_cache_list, target=target, skip_empty_results=skip_empty_results
        )

    @classmethod
    def filter_by_typo_chars_tag(self, tagged_cache_list: list, target: str, skip_empty_results: bool=False) -> list:
        return self._filter_by_bool_tag(
            attr_name='contains_typo_chars',
            tagged_cache_list=tagged_cache_list, target=target, skip_empty_results=skip_empty_results
        )

    @classmethod
    def filter_by_space_chars_tag(self, tagged_cache_list: list, target: str, skip_empty_results: bool=False) -> list:
        return self._filter_by_bool_tag(
            attr_name='contains_space',
            tagged_cache_list=tagged_cache_list, target=target, skip_empty_results=skip_empty_results
        )

    @classmethod
    def filter_by_garbage_chars_tag_group(self, tagged_cache_list: list, target: str, skip_empty_results: bool=False) -> list:
        return self._filter_by_bool_tag(
            attr_name='is_garbage_word',
            tagged_cache_list=tagged_cache_list, target=target, skip_empty_results=skip_empty_results
        )

    @classmethod
    def filter_by_hiragana_tag(self, tagged_cache_list: list, target: str, skip_empty_results: bool=False) -> list:
        return self._filter_by_jp_char_tag(
            attr_name='hiragana_tag',
            tagged_cache_list=tagged_cache_list, target=target, skip_empty_results=skip_empty_results
        )

    @classmethod
    def filter_by_katakana_tag(self, tagged_cache_list: list, target: str, skip_empty_results: bool=False) -> list:
        return self._filter_by_jp_char_tag(
            attr_name='katakana_tag',
            tagged_cache_list=tagged_cache_list, target=target, skip_empty_results=skip_empty_results
        )

    @classmethod
    def filter_by_kanji_tag(self, tagged_cache_list: list, target: str, skip_empty_results: bool=False) -> list:
        return self._filter_by_jp_char_tag(
            attr_name='kanji_tag',
            tagged_cache_list=tagged_cache_list, target=target, skip_empty_results=skip_empty_results
        )

    @classmethod
    def filter_by_hit_count(self, tagged_cache_list: list, target: int, ineq: str, skip_empty_results: bool=False) -> list:
        check_value(ineq, valid_value_list=['==', '>', '<', '>=', '<='])
        result = []
        for tagged_cache in tagged_cache_list:
            if tagged_cache.hit_count is None and target != -1:
                continue
            elif tagged_cache.hit_count is None and target == -1 and ineq == '==':
                result.append(tagged_cache)
                continue
            if skip_empty_results and len(tagged_cache.word_results) == 0:
                continue
            if ineq == '==':
                if tagged_cache.hit_count is not None and tagged_cache.hit_count == target:
                    result.append(tagged_cache)
            elif ineq == '>':
                if tagged_cache.hit_count is not None and tagged_cache.hit_count > target:
                    result.append(tagged_cache)
            elif ineq == '<':
                if tagged_cache.hit_count is not None and tagged_cache.hit_count < target:
                    result.append(tagged_cache)
            elif ineq == '>=':
                if tagged_cache.hit_count is not None and tagged_cache.hit_count >= target:
                    result.append(tagged_cache)
            elif ineq == '<=':
                if tagged_cache.hit_count is not None and tagged_cache.hit_count <= target:
                    result.append(tagged_cache)
            else:
                logger.error(f"Invalid ineq: {ineq}")
                raise Exception
        return result

    @classmethod
    def filter_by_times_usec(self, tagged_cache_list: list, target: float, ineq: str, ref_mode: str='newest', target_unit: str='day', skip_empty_results: bool=False) -> list:
        """
        ref_mode
            'newest': Filter by newest time_usec value
            'oldest': Filter by oldest time_usec value
        """
        check_value(ineq, valid_value_list=['==', '>', '<', '>=', '<='])
        check_value(ref_mode, valid_value_list=['oldest', 'newest'])
        check_value(target_unit, valid_value_list=['day', 'days', 'd', 'year', 'years', 'y', 'usec'])
        result = []
        for tagged_cache in tagged_cache_list:
            if tagged_cache.hit_count is None and target != -1:
                continue
            elif tagged_cache.hit_count is None and target == -1 and ineq == '==':
                result.append(tagged_cache)
                continue
            if skip_empty_results and len(tagged_cache.word_results) == 0:
                continue
            if len(tagged_cache.times_usec) == 0:
                logger.error(f"Tried to filter by times_usec, but encountered empty times_usec.")
                logger.error(f"tagged_cache: {tagged_cache}")
                raise Exception
            if ref_mode == 'oldest':
                target_time_usec = min(tagged_cache.times_usec)
            elif ref_mode == 'newest':
                target_time_usec = max(tagged_cache.times_usec)
            else:
                raise Exception
            if target_unit == 'usec':
                target_time = target_time_usec
            elif target_unit in ['day', 'days', 'd']:
                target_time = get_days_elapsed_from_time_usec(target_time_usec)
            elif target_unit in ['year', 'years', 'y']:
                target_time = get_years_elapsed_from_time_usec(target_time_usec)
            else:
                raise Exception
            if ineq == '==':
                if target_time is not None and target_time == target:
                    result.append(tagged_cache)
            elif ineq == '>':
                if target_time is not None and target_time > target:
                    result.append(tagged_cache)
            elif ineq == '<':
                if target_time is not None and target_time < target:
                    result.append(tagged_cache)
            elif ineq == '>=':
                if target_time is not None and target_time >= target:
                    result.append(tagged_cache)
            elif ineq == '<=':
                if target_time is not None and target_time <= target:
                    result.append(tagged_cache)
            else:
                logger.error(f"Invalid ineq: {ineq}")
                raise Exception
        return result

    @classmethod
    def filter_by_len_word_results(self, tagged_cache_list: list, target: int, ineq: str, skip_empty_results: bool=False) -> list:
        check_value(ineq, valid_value_list=['==', '>', '<', '>=', '<='])
        result = []
        for tagged_cache in tagged_cache_list:
            if tagged_cache.word_results is None and target != -1:
                continue
            elif tagged_cache.word_results is None and target == -1 and ineq == '==':
                result.append(tagged_cache)
                continue
            if skip_empty_results and len(tagged_cache.word_results) == 0:
                continue
            if ineq == '==':
                if len(tagged_cache.word_results) == target:
                    result.append(tagged_cache)
            elif ineq == '>':
                if len(tagged_cache.word_results) > target:
                    result.append(tagged_cache)
            elif ineq == '<':
                if len(tagged_cache.word_results) < target:
                    result.append(tagged_cache)
            elif ineq == '>=':
                if len(tagged_cache.word_results) >= target:
                    result.append(tagged_cache)
            elif ineq == '<=':
                if len(tagged_cache.word_results) <= target:
                    result.append(tagged_cache)
            else:
                logger.error(f"Invalid ineq: {ineq}")
                raise Exception
        return result

    @classmethod
    def filter_by_concept_labels_exist(self, tagged_cache_list: list, target: bool, exclude_empty_results: bool=True):
        check_value(item=target, valid_value_list=[True, False])
        result = []
        working_tagged_cache_list = tagged_cache_list.copy()
        for i, tagged_cache in enumerate(working_tagged_cache_list):
            tagged_cache = TaggedCache.buffer(tagged_cache)
            if tagged_cache.word_results is None or len(tagged_cache.word_results) == 0:
                continue
            relevant_word_results = []
            for j, word_result in enumerate(tagged_cache.word_results):
                word_result = WordResult.buffer(word_result)
                if target == True:
                    if word_result.concept_labels is not None:
                        relevant_word_results.append(word_result)
                elif target == False:
                    if word_result.concept_labels is None:
                        relevant_word_results.append(word_result)
                else:
                    raise Exception
            if len(relevant_word_results) == 0 and exclude_empty_results:
                continue
            else:
                tagged_cache.word_results = relevant_word_results
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_common_words(self, tagged_cache_list: list, target: bool, exclude_empty_results: bool=True):
        check_value(item=target, valid_value_list=[True, False])
        result = []
        working_tagged_cache_list = tagged_cache_list.copy()
        for tagged_cache in working_tagged_cache_list:
            tagged_cache = TaggedCache.buffer(tagged_cache)
            if tagged_cache.word_results is None or len(tagged_cache.word_results) == 0:
                continue
            relevant_word_results = []
            for word_result in tagged_cache.word_results:
                word_result = WordResult.buffer(word_result)
                if target == True:
                    if word_result.concept_labels is not None:
                        if word_result.concept_labels.is_common_word:
                            relevant_word_results.append(word_result)
                elif target == False:
                    if word_result.concept_labels is not None:
                        if not word_result.concept_labels.is_common_word:
                            relevant_word_results.append(word_result)
                    elif word_result.concept_labels is None:
                        relevant_word_results.append(word_result)
                else:
                    raise Exception
            if len(relevant_word_results) == 0 and exclude_empty_results:
                continue
            else:
                tagged_cache.word_results = relevant_word_results
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_jlpt_level(self, tagged_cache_list: list, target: int, ineq: str, exclude_empty_results: bool=True):
        """
        Valid jlpt targets: 1, 2, 3, 4, 5
        Non-jlpt targets: -1
        """
        check_value(target, valid_value_list=[-1, 1, 2, 3, 4, 5])
        check_value(ineq, valid_value_list=['==', '>', '<', '>=', '<='])
        result = []
        for tagged_cache in tagged_cache_list:
            tagged_cache = TaggedCache.buffer(tagged_cache)
            if tagged_cache.word_results is None or len(tagged_cache.word_results) == 0:
                continue
            relevant_word_results = []
            for word_result in tagged_cache.word_results:
                word_result = WordResult.buffer(word_result)
                if target == -1 and (ineq == '==' or ineq == '>=' or ineq == '<='):
                    if word_result.concept_labels is None or word_result.concept_labels.jlpt_level is None:
                        relevant_word_results.append(word_result)
                if word_result.concept_labels is not None and word_result.concept_labels.jlpt_level is not None:
                    jlpt_level = word_result.concept_labels.jlpt_level
                    if ineq == '==' and jlpt_level == target:
                        relevant_word_results.append(word_result)
                    elif ineq == '>' and jlpt_level > target:
                        relevant_word_results.append(word_result)
                    elif ineq == '<' and jlpt_level < target:
                        relevant_word_results.append(word_result)
                    elif ineq == '>=' and jlpt_level >= target:
                        relevant_word_results.append(word_result)
                    elif ineq == '<=' and jlpt_level <= target:
                        relevant_word_results.append(word_result)
            if len(relevant_word_results) == 0 and exclude_empty_results:
                continue
            else:
                tagged_cache.word_results = relevant_word_results # TODO: Need to verify that this is okay. Try for tagged_cache in tagged_cache_list.copy()?
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_wanikani_level(self, tagged_cache_list: list, target: int, ineq: str, exclude_empty_results: bool=True):
        """
        Valid wanikani targets: >=1
        Non-wanikani targets: -1
        """
        check_value(ineq, valid_value_list=['==', '>', '<', '>=', '<='])
        result = []
        for tagged_cache in tagged_cache_list:
            tagged_cache = TaggedCache.buffer(tagged_cache)
            if tagged_cache.word_results is None or len(tagged_cache.word_results) == 0:
                continue
            relevant_word_results = []
            for word_result in tagged_cache.word_results:
                word_result = WordResult.buffer(word_result)
                if target == -1 and (ineq == '==' or ineq == '>=' or ineq == '<='):
                    if word_result.concept_labels is None or word_result.concept_labels.wanikani_level is None:
                        relevant_word_results.append(word_result)
                if word_result.concept_labels is not None and word_result.concept_labels.wanikani_level is not None:
                    wanikani_level = word_result.concept_labels.wanikani_level
                    if ineq == '==' and wanikani_level == target:
                        relevant_word_results.append(word_result)
                    elif ineq == '>' and wanikani_level > target:
                        relevant_word_results.append(word_result)
                    elif ineq == '<' and wanikani_level < target:
                        relevant_word_results.append(word_result)
                    elif ineq == '>=' and wanikani_level >= target:
                        relevant_word_results.append(word_result)
                    elif ineq == '<=' and wanikani_level <= target:
                        relevant_word_results.append(word_result)
            if len(relevant_word_results) == 0 and exclude_empty_results:
                continue
            else:
                tagged_cache.word_results = relevant_word_results
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_learned(
        self, tagged_cache_list: list, learned_list: list, target: str,
        match_search_word: str='off', match_jap_vocab: str='off', match_other_form: str='off',
        match_operator: str='or', exclude_empty_results: bool=True
    ):
        """
        TODO: Fix bugs
        """
        check_value(target, valid_value_list=['learned', 'not_learned'])
        check_value(match_search_word, valid_value_list=['off', 'writing'])
        check_value(match_jap_vocab, valid_value_list=['off', 'writing', 'reading', 'both'])
        check_value(match_other_form, valid_value_list=['off', 'writing', 'reading', 'both'])
        check_value(match_operator, valid_value_list=['or', 'and'])
        
        match_search_word_is_on = True if match_search_word != 'off' else False
        match_jap_vocab_is_on = True if match_jap_vocab != 'off' else False
        match_other_form_is_on = True if match_other_form != 'off' else False
        search_is_off = not match_jap_vocab_is_on or not match_other_form_is_on

        result = []
        for tagged_cache in tagged_cache_list:
            tagged_cache = TaggedCache.buffer(tagged_cache)
            if tagged_cache.word_results is None or len(tagged_cache.word_results) == 0:
                continue
            relevant_word_results = []
            is_search_word_matched = None
            if match_search_word_is_on:
                search_word = tagged_cache.search_word
                if match_search_word == 'writing':
                    if search_word in learned_list:
                        is_search_word_matched = True if target == 'learned' else False if target == 'not_learned' else None
                    else:
                        is_search_word_matched = False if target == 'learned' else True if target == 'not_learned' else None

            search_is_redundant = match_search_word_is_on and is_search_word_matched and match_operator == 'or'

            if search_is_redundant:
                relevant_word_results = tagged_cache.word_results.copy()
            elif not search_is_off:
                for word_result in tagged_cache.word_results:
                    word_result = WordResult.buffer(word_result)
                    if match_jap_vocab_is_on:
                        is_jap_vocab_writing_matched = None
                        if target == 'learned':
                            is_jap_vocab_writing_matched = True \
                                if word_result.jap_vocab.writing is not None and \
                                    word_result.jap_vocab.writing in learned_list else False
                            is_jap_vocab_reading_matched = True \
                                if word_result.jap_vocab.reading is not None and \
                                    word_result.jap_vocab.reading in learned_list else False
                        elif target == 'not_learned':
                            is_jap_vocab_writing_matched = True \
                                if word_result.jap_vocab.writing is not None and \
                                    word_result.jap_vocab.writing not in learned_list else False
                            is_jap_vocab_reading_matched = True \
                                if word_result.jap_vocab.reading is not None and \
                                    word_result.jap_vocab.reading not in learned_list else False
                        else:
                            raise Exception
                        if match_jap_vocab == 'writing':
                            is_jap_vocab_matched = True if is_jap_vocab_writing_matched else False
                        elif match_jap_vocab == 'reading':
                            is_jap_vocab_matched = True if is_jap_vocab_reading_matched else False
                        elif match_jap_vocab == 'both':
                            is_jap_vocab_matched = True if is_jap_vocab_writing_matched and is_jap_vocab_reading_matched else False
                        else:
                            raise Exception
                    if match_other_form_is_on:
                        is_other_form_writing_matched = False
                        is_other_form_reading_matched = False
                        if word_result.vocab_entry.other_forms is not None:
                            for other_form in word_result.vocab_entry.other_forms.other_form_list:
                                other_form = OtherForm.buffer(other_form)
                                if target == 'learned':
                                    is_other_form_writing_matched = True if other_form.kanji_writing in learned_list else is_other_form_writing_matched
                                    if is_other_form_writing_matched and match_other_form == 'writing':
                                        break
                                    is_other_form_reading_matched = True if other_form.kana_writing in learned_list else is_other_form_reading_matched
                                    if is_other_form_reading_matched and match_other_form == 'reading':
                                        break
                                    if is_other_form_writing_matched and is_other_form_reading_matched and match_other_form == 'both':
                                        break
                                else:
                                    is_other_form_writing_matched = True if other_form.kanji_writing not in learned_list else is_other_form_writing_matched
                                    if is_other_form_writing_matched and match_other_form == 'writing':
                                        break
                                    is_other_form_reading_matched = True if other_form.kana_writing not in learned_list else is_other_form_reading_matched
                                    if is_other_form_reading_matched and match_other_form == 'reading':
                                        break
                                    if is_other_form_writing_matched and is_other_form_reading_matched and match_other_form == 'both':
                                        break
                            if match_other_form == 'writing':
                                is_other_form_matched = True if is_other_form_writing_matched else False
                            elif match_other_form == 'reading':
                                is_other_form_matched = True if is_other_form_reading_matched else False
                            elif match_other_form == 'both':
                                is_other_form_matched = True if is_other_form_writing_matched and is_other_form_reading_matched else False
                            else:
                                raise Exception
                        else:
                            is_other_form_matched = False
                    is_word_result_matched = None
                    if match_search_word_is_on:
                        is_word_result_matched = is_search_word_matched
                    if match_jap_vocab_is_on:
                        if is_word_result_matched is None:
                            is_word_result_matched = is_jap_vocab_matched
                        else:
                            if match_operator == 'or':
                                is_word_result_matched = is_word_result_matched or is_jap_vocab_matched
                            elif match_operator == 'and':
                                is_word_result_matched = is_word_result_matched and is_jap_vocab_matched
                            else:
                                raise Exception
                    if match_other_form_is_on:
                        if is_word_result_matched is None:
                            is_word_result_matched = is_other_form_matched
                        else:
                            if match_operator == 'or':
                                is_word_result_matched = is_word_result_matched or is_other_form_matched
                            elif match_operator == 'and':
                                is_word_result_matched = is_word_result_matched and is_other_form_matched
                            else:
                                raise Exception
                    
                    if is_word_result_matched is not None and is_word_result_matched == True:
                        relevant_word_results.append(word_result)
            if len(relevant_word_results) == 0 and exclude_empty_results:
                continue
            else:
                tagged_cache.word_results = relevant_word_results
                result.append(tagged_cache)

        return result