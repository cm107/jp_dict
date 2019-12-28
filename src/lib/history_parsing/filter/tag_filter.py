from logger import logger
from common_utils.check_utils import check_value
from ....util.time_utils import get_days_elapsed_from_time_usec, get_years_elapsed_from_time_usec

class TagFilter:
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