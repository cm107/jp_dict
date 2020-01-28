import operator
from logger import logger
from common_utils.check_utils import check_value_from_list, check_value
from ..filter.tagged_cache_filter import TaggedCacheFilter
from ..filter.core import TaggedCache

class TaggedCacheSorter:
    @classmethod
    def _sort_by_tag0(cls, filter_method: classmethod, tagged_cache_list: list, target_order: list, valid_target_list: list) -> list:
        check_value_from_list(target_order, valid_value_list=valid_target_list)
        result = []
        for target in target_order:
            filter_result = filter_method(
                tagged_cache_list=tagged_cache_list,
                target=target,
                skip_empty_results=True
            )
            result.extend(filter_result)
        return result

    @classmethod
    def _sort_by_tag1(cls, filter_method: classmethod, tagged_cache_list: list, target_order: list, valid_target_list: list) -> list:
        check_value_from_list(target_order, valid_value_list=valid_target_list)
        result = []
        for target in target_order:
            filter_result = filter_method(
                tagged_cache_list=tagged_cache_list,
                target=target,
                exclude_empty_results=True
            )
            result.extend(filter_result)
        return result

    @classmethod
    def _sort_by_bool3_tag(cls, filter_method: classmethod, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_tag0(
            filter_method=filter_method,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order,
            valid_target_list=['true', 'false', 'none']
        )

    @classmethod
    def _sort_by_bool2_tag(cls, filter_method: classmethod, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_tag1(
            filter_method=filter_method,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order,
            valid_target_list=[True, False]
        )

    @classmethod
    def _sort_by_jp_char_tag(cls, filter_method: classmethod, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_tag0(
            filter_method=filter_method,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order,
            valid_target_list=['all', 'partial', 'none']
        )

    @classmethod
    def sort_by_wildcard_tag(cls, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_bool3_tag(
            filter_method=TaggedCacheFilter.filter_by_wildcard_tag,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order
        )

    @classmethod
    def sort_by_eng_chars_tag(cls, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_bool3_tag(
            filter_method=TaggedCacheFilter.filter_by_eng_chars_tag,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order
        )

    @classmethod
    def sort_by_typo_chars_tag(cls, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_bool3_tag(
            filter_method=TaggedCacheFilter.filter_by_typo_chars_tag,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order
        )

    @classmethod
    def sort_by_space_chars_tag(cls, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_bool3_tag(
            filter_method=TaggedCacheFilter.filter_by_space_chars_tag,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order
        )

    @classmethod
    def sort_by_garbage_chars_tag_group(cls, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_bool3_tag(
            filter_method=TaggedCacheFilter.filter_by_garbage_chars_tag_group,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order
        )

    @classmethod
    def sort_by_hiragana_tag(cls, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_jp_char_tag(
            filter_method=TaggedCacheFilter.filter_by_hiragana_tag,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order
        )

    @classmethod
    def sort_by_katakana_tag(cls, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_jp_char_tag(
            filter_method=TaggedCacheFilter.filter_by_katakana_tag,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order
        )

    @classmethod
    def sort_by_kanji_tag(cls, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_jp_char_tag(
            filter_method=TaggedCacheFilter.filter_by_kanji_tag,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order
        )

    @classmethod
    def sort_by_hit_count(cls, tagged_cache_list: list, mode: str='ascending') -> list:
        check_value(mode, valid_value_list=['ascending', 'descending'])
        result = []
        hit_count_results_list = []
        hit_count = 0
        while True:
            hit_count += 1
            hit_count_results_list.append(TaggedCacheFilter.filter_by_hit_count(
                    tagged_cache_list=tagged_cache_list, target=hit_count, ineq='==',
                    skip_empty_results=True
            ))
            higher_hit_count_results = TaggedCacheFilter.filter_by_hit_count(
                tagged_cache_list=tagged_cache_list, target=hit_count, ineq='>',
                skip_empty_results=True
            )
            if len(higher_hit_count_results) == 0:
                break
        if mode == 'ascending':
            pass
        elif mode == 'descending':
            hit_count_results_list.reverse()
        else:
            raise Exception
        for hit_count_item in hit_count_results_list:
            result.extend(hit_count_item)
        return result

    @classmethod
    def sort_by_times_usec(cls, tagged_cache_list: list, ref_mode: str='newest', mode: str='ascending') -> list:
        """
        ref_mode
            'newest': Sort by newest time_usec value
            'oldest': Sort by oldest time_usec value
        mode
            'ascending': Sort from lowest to highest
            'descending': Sort from highest to lowest
        """
        check_value(ref_mode, valid_value_list=['newest', 'oldest'])
        results = tagged_cache_list.copy()
        attr_name = 'newest_time_usec' if ref_mode == 'newest' else 'oldest_time_usec' if ref_mode == 'oldest' else None
        reverse = False if mode == 'ascending' else True if mode == 'descending' else None
        if attr_name is None or reverse is None:
            raise Exception

        results.sort(key=operator.attrgetter(attr_name), reverse=reverse)
        return results

    @classmethod
    def sort_by_len_word_results(cls, tagged_cache_list: list, mode: str='ascending') -> list:
        check_value(mode, valid_value_list=['ascending', 'descending'])
        result = []
        len_word_results_list = []
        len_word = 0
        while True:
            len_word += 1
            len_word_results_list.append(TaggedCacheFilter.filter_by_len_word_results(
                    tagged_cache_list=tagged_cache_list, target=len_word, ineq='==',
                    skip_empty_results=True
            ))
            higher_len_word_results = TaggedCacheFilter.filter_by_len_word_results(
                tagged_cache_list=tagged_cache_list, target=len_word, ineq='>',
                skip_empty_results=True
            )
            if len(higher_len_word_results) == 0:
                break
        if mode == 'ascending':
            pass
        elif mode == 'descending':
            len_word_results_list.reverse()
        else:
            raise Exception
        for len_word_item in len_word_results_list:
            result.extend(len_word_item)
        return result

    @classmethod
    def sort_by_concept_labels_exist(cls, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_bool2_tag(
            filter_method=TaggedCacheFilter.filter_by_concept_labels_exist,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order
        )

    @classmethod
    def sort_by_common_words(cls, tagged_cache_list: list, target_order: list) -> list:
        return cls._sort_by_bool2_tag(
            filter_method=TaggedCacheFilter.filter_by_common_words,
            tagged_cache_list=tagged_cache_list,
            target_order=target_order
        )

    @classmethod
    def sort_by_jlpt_level(cls, tagged_cache_list: list, mode: str='ascending', non_jlpt: str='second') -> list:
        """
        mode options: 'ascending', 'descending'
        non_jlpt options: 'first', 'second'
        """
        check_value(mode, valid_value_list=['ascending', 'descending'])
        check_value(non_jlpt, valid_value_list=['first', 'second'])
        result = []
        jlpt_results_list = []
        level = 0
        while True:
            level += 1
            jlpt_results_list.append(TaggedCacheFilter.filter_by_jlpt_level(
                tagged_cache_list=tagged_cache_list, target=level, ineq='==',
                exclude_empty_results=True
            ))
            higher_level_results = TaggedCacheFilter.filter_by_jlpt_level(
                tagged_cache_list=tagged_cache_list, target=level, ineq='>',
                exclude_empty_results=True
            )
            if len(higher_level_results) == 0:
                break
        non_jlpt_results = TaggedCacheFilter.filter_by_jlpt_level(
            tagged_cache_list=tagged_cache_list, target=-1, ineq='==',
            exclude_empty_results=True
        )
        jlpt_results = []

        if mode == 'ascending':
            pass
        elif mode == 'descending':
            jlpt_results_list.reverse()
        else:
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
    def sort_by_wanikani_level(self, tagged_cache_list: list, mode: str='ascending', non_wanikani: str='second') -> list:
        """
        mode options: 'ascending', 'descending'
        non_wanikani options: 'first', 'second'
        """
        result = []
        wanikani_results_list = []
        level = -1
        while True:
            level += 1
            current_level_results = TaggedCacheFilter.filter_by_wanikani_level(
                tagged_cache_list=tagged_cache_list, target=level, ineq='==',
                exclude_empty_results=True
            )
            wanikani_results_list.append(current_level_results)
            higher_level_results = TaggedCacheFilter.filter_by_wanikani_level(
                tagged_cache_list=tagged_cache_list, target=level, ineq='>',
                exclude_empty_results=True
            )
            if len(higher_level_results) == 0:
                break

        non_wanikani_results = TaggedCacheFilter.filter_by_wanikani_level(
            tagged_cache_list=tagged_cache_list, target=-1, ineq='==',
            exclude_empty_results=True
        )

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

class DefaultTaggedCacheSorter:
    @classmethod
    def _sort_by_tag(
        cls, sort_method: classmethod, tagged_cache_list: list,
        forward_order: list, reverse_order: list,
        reverse: bool=False
    ) -> list:
        if not reverse:
            return sort_method(
                tagged_cache_list=tagged_cache_list,
                target_order=forward_order
            )
        else:
            return sort_method(
                tagged_cache_list=tagged_cache_list,
                target_order=reverse_order
            )

    @classmethod
    def _sort_by_bool3_tag(cls, sort_method: classmethod, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: 'true', 'false', 'none'
        reverse order: 'false', 'true', 'none'
        """
        return cls._sort_by_tag(
            sort_method=sort_method, tagged_cache_list=tagged_cache_list,
            forward_order=['true', 'false', 'none'],
            reverse_order=['false', 'true', 'none'],
            reverse=reverse
        )

    @classmethod
    def _sort_by_bool2_tag(cls, sort_method: classmethod, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: True, False
        reverse order: False, True
        """
        return cls._sort_by_tag(
            sort_method=sort_method, tagged_cache_list=tagged_cache_list,
            forward_order=[True, False],
            reverse_order=[False, True],
            reverse=reverse
        )

    @classmethod
    def _sort_by_jp_char_tag(cls, sort_method: classmethod, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: 'all', 'partial', 'none'
        reverse order: 'none', 'partial', 'all'
        """
        return cls._sort_by_tag(
            sort_method=sort_method, tagged_cache_list=tagged_cache_list,
            forward_order=['all', 'partial', 'none'],
            reverse_order=['none', 'partial', 'all'],
            reverse=reverse
        )

    @classmethod
    def sort_by_wildcard_tag(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: 'true', 'false', 'none'
        reverse order: 'false', 'true', 'none'
        """
        return cls._sort_by_bool3_tag(
            sort_method=TaggedCacheSorter.sort_by_wildcard_tag,
            tagged_cache_list=tagged_cache_list,
            reverse=reverse
        )

    @classmethod
    def sort_by_eng_chars_tag(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: 'true', 'false', 'none'
        reverse order: 'false', 'true', 'none'
        """
        return cls._sort_by_bool3_tag(
            sort_method=TaggedCacheSorter.sort_by_eng_chars_tag,
            tagged_cache_list=tagged_cache_list,
            reverse=reverse
        )

    @classmethod
    def sort_by_typo_chars_tag(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: 'true', 'false', 'none'
        reverse order: 'false', 'true', 'none'
        """
        return cls._sort_by_bool3_tag(
            sort_method=TaggedCacheSorter.sort_by_typo_chars_tag,
            tagged_cache_list=tagged_cache_list,
            reverse=reverse
        )

    @classmethod
    def sort_by_space_chars_tag(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: 'true', 'false', 'none'
        reverse order: 'false', 'true', 'none'
        """
        return cls._sort_by_bool3_tag(
            sort_method=TaggedCacheSorter.sort_by_space_chars_tag,
            tagged_cache_list=tagged_cache_list,
            reverse=reverse
        )

    @classmethod
    def sort_by_garbage_chars_tag_group(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: 'true', 'false', 'none'
        reverse order: 'false', 'true', 'none'
        """
        return cls._sort_by_bool3_tag(
            sort_method=TaggedCacheSorter.sort_by_garbage_chars_tag_group,
            tagged_cache_list=tagged_cache_list,
            reverse=reverse
        )

    @classmethod
    def sort_by_hiragana_tag(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: 'all', 'partial', 'none'
        reverse order: 'none', 'partial', 'all'
        """
        return cls._sort_by_jp_char_tag(
            sort_method=TaggedCacheSorter.sort_by_hiragana_tag,
            tagged_cache_list=tagged_cache_list,
            reverse=reverse
        )
    
    @classmethod
    def sort_by_katakana_tag(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: 'all', 'partial', 'none'
        reverse order: 'none', 'partial', 'all'
        """
        return cls._sort_by_jp_char_tag(
            sort_method=TaggedCacheSorter.sort_by_katakana_tag,
            tagged_cache_list=tagged_cache_list,
            reverse=reverse
        )

    @classmethod
    def sort_by_kanji_tag(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: 'all', 'partial', 'none'
        reverse order: 'none', 'partial', 'all'
        """
        return cls._sort_by_jp_char_tag(
            sort_method=TaggedCacheSorter.sort_by_kanji_tag,
            tagged_cache_list=tagged_cache_list,
            reverse=reverse
        )

    @classmethod
    def sort_by_hit_count(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: descending order
        reverse order: ascending order
        """
        if not reverse:
            return TaggedCacheSorter.sort_by_hit_count(
                tagged_cache_list=tagged_cache_list, mode='descending'
            )
        else:
            return TaggedCacheSorter.sort_by_hit_count(
                tagged_cache_list=tagged_cache_list, mode='ascending'
            )

    @classmethod
    def sort_by_times_usec(cls, tagged_cache_list: list, ref_mode: str='newest', reverse: bool=False) -> list:
        """
        ref_mode
            'newest': Sort by newest time_usec value
            'oldest': Sort by oldest time_usec value

        forward order: descending order
        reverse order: ascending order
        """
        if not reverse:
            return TaggedCacheSorter.sort_by_times_usec(
                tagged_cache_list=tagged_cache_list, ref_mode=ref_mode, mode='descending'
            )
        else:
            return TaggedCacheSorter.sort_by_times_usec(
                tagged_cache_list=tagged_cache_list, ref_mode=ref_mode, mode='ascending'
            )

    @classmethod
    def filter_by_len_word_results(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: ascending order
        reverse order: descending order
        """
        if not reverse:
            return TaggedCacheSorter.sort_by_len_word_results(
                tagged_cache_list=tagged_cache_list, mode='ascending'
            )
        else:
            return TaggedCacheSorter.sort_by_len_word_results(
                tagged_cache_list=tagged_cache_list, mode='descending'
            )

    @classmethod
    def sort_by_concept_labels_exist(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        return cls._sort_by_bool2_tag(
            sort_method=TaggedCacheSorter.sort_by_concept_labels_exist,
            tagged_cache_list=tagged_cache_list, reverse=reverse
        )

    @classmethod
    def sort_by_common_words(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        return cls._sort_by_bool2_tag(
            sort_method=TaggedCacheSorter.sort_by_common_words,
            tagged_cache_list=tagged_cache_list, reverse=reverse
        )

    @classmethod
    def sort_by_jlpt_level(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: descending jlpt, non-jlpt
        backward order: non-jlpt, ascending jlpt
        """
        if not reverse:
            return TaggedCacheSorter.sort_by_jlpt_level(
                tagged_cache_list=tagged_cache_list, mode='descending', non_jlpt='second'
            )
        else:
            return TaggedCacheSorter.sort_by_jlpt_level(
                tagged_cache_list=tagged_cache_list, mode='ascending', non_jlpt='first'
            )

    @classmethod
    def sort_by_wanikani_level(cls, tagged_cache_list: list, reverse: bool=False) -> list:
        """
        forward order: ascending wanikani, non-wanikani
        backward order: non-wanikani, descending wanikani
        """
        if not reverse:
            return TaggedCacheSorter.sort_by_wanikani_level(
                tagged_cache_list=tagged_cache_list, mode='ascending', non_wanikani='second'
            )
        else:
            return TaggedCacheSorter.sort_by_wanikani_level(
                tagged_cache_list=tagged_cache_list, mode='descending', non_wanikani='first'
            )

class SorterCompose:
    @classmethod
    def sort0(cls, tagged_cache_list: list, learned_list: list=None) -> list:
        logger.yellow(f"Flag0 len(tagged_cache_list): {len(tagged_cache_list)}")
        results = TaggedCacheFilter.filter_by_len_word_results(tagged_cache_list=tagged_cache_list, target=1, ineq='==', skip_empty_results=True)
        logger.yellow(f"Flag1 len(results): {len(results)}")
        if learned_list is not None:
            results = TaggedCacheFilter.filter_by_learned(
                tagged_cache_list=results, learned_list=learned_list, target='learned',
                match_search_word='writing', match_jap_vocab='either', match_other_form='writing',
                match_operator='nor', exclude_empty_results=True
            )
        logger.yellow(f"Flag2 len(results): {len(results)}")
        results = TaggedCacheFilter.filter_by_duplicates(tagged_cache_list=results, target='unique', strictness=1, exclude_empty_results=True)
        logger.yellow(f"Flag3 len(results): {len(results)}")
        results = DefaultTaggedCacheSorter.sort_by_times_usec(tagged_cache_list=results, ref_mode='oldest', reverse=True)
        results = DefaultTaggedCacheSorter.sort_by_common_words(tagged_cache_list=results, reverse=False)
        results = DefaultTaggedCacheSorter.sort_by_wanikani_level(tagged_cache_list=results, reverse=False)
        results = DefaultTaggedCacheSorter.sort_by_jlpt_level(tagged_cache_list=results, reverse=False)
        results = DefaultTaggedCacheSorter.sort_by_hit_count(tagged_cache_list=results, reverse=False)
        logger.yellow(f"Flag4 len(results): {len(results)}")
        return results