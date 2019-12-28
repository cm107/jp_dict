import pickle
from logger import logger

from ..conf.paths import PathConf
from ..lib.history_parsing.filter.tag_filter import TagFilter
from ..lib.history_parsing.filter.core import TaggedCache

class TagFilterTest:
    def __init__(self):
        word_matches_save_path = f"{PathConf.word_matches_save_dir}/soup_test0.pkl"
        checkpoint = pickle.load(open(word_matches_save_path, 'rb'))
        self.tagged_cache_list = checkpoint['tagged_cache_list']

    def filter_by_kanji_tag(self, target: str) -> list:
        return TagFilter.filter_by_kanji_tag(tagged_cache_list=self.tagged_cache_list, target=target, skip_empty_results=True)

    def filter_by_hiragana_tag(self, target: str) -> list:
        return TagFilter.filter_by_hiragana_tag(tagged_cache_list=self.tagged_cache_list, target=target, skip_empty_results=True)

    def filter_by_katakana_tag(self, target: str) -> list:
        return TagFilter.filter_by_katakana_tag(tagged_cache_list=self.tagged_cache_list, target=target, skip_empty_results=True)

    def filter_by_hit_count(self, target: int, ineq: str) -> list:
        return TagFilter.filter_by_hit_count(tagged_cache_list=self.tagged_cache_list, target=target, ineq=ineq, skip_empty_results=True)

    def filter_by_times_usec(self, target: float, ineq: str, ref_mode: str, target_unit: str) -> list:
        return TagFilter.filter_by_times_usec(tagged_cache_list=self.tagged_cache_list, target=target, ineq=ineq, ref_mode=ref_mode, target_unit=target_unit, skip_empty_results=True)

    def filter_by_len_word_results(self, target: int, ineq: str) -> list:
        return TagFilter.filter_by_len_word_results(tagged_cache_list=self.tagged_cache_list, target=target, ineq=ineq, skip_empty_results=True)

    def show_results(self, name: str, results: list, count_only: bool=False):
        logger.yellow(f"len({name}): {len(results)}")
        if not count_only:
            for i, tagged_cache in enumerate(results):
                tagged_cache = TaggedCache.buffer(tagged_cache)
                logger.cyan(f"{i}: {tagged_cache.search_word}")
                logger.green(tagged_cache.word_results)

    def test_kanji(self, target: str, count_only: bool=False):
        self.show_results(name=f'kanji_{target}', results=self.filter_by_kanji_tag(target=target), count_only=count_only)

    def test_hiragana(self, target: str, count_only: bool=False):
        self.show_results(name=f'hiragana_{target}', results=self.filter_by_hiragana_tag(target=target), count_only=count_only)

    def test_katakana(self, target: str, count_only: bool=False):
        self.show_results(name=f'katakana_{target}', results=self.filter_by_katakana_tag(target=target), count_only=count_only)

    def test_hit_count(self, target: int, ineq: str, count_only: bool=False):
        self.show_results(name=f'hit_count{ineq}{target}', results=self.filter_by_hit_count(target=target, ineq=ineq), count_only=count_only)

    def test_times_usec(self, target: float, ineq: str, ref_mode: str, target_unit: str, count_only: bool=False):
        self.show_results(
            name=f'{ref_mode}_timestamp{ineq}{target}{target_unit}',
            results=self.filter_by_times_usec(target=target, ineq=ineq, ref_mode=ref_mode, target_unit=target_unit),
            count_only=count_only
        )

    def test_len_word_results(self, target: int, ineq: str, count_only: bool=False):
        self.show_results(name=f"len(word_results){ineq}{target}", results=self.filter_by_len_word_results(target=target, ineq=ineq), count_only=count_only)

    def unit_test_kanji(
        self,
        target_list: list=['all', 'partial', 'none'],
        count_only: bool=True
    ):
        logger.info("Kanji Unit Test")
        for target in target_list:
            self.test_kanji(target=target, count_only=count_only)

    def unit_test_hiragana(
        self,
        target_list: list=['all', 'partial', 'none'],
        count_only: bool=True
    ):
        logger.info("Hiragana Unit Test")
        for target in target_list:
            self.test_hiragana(target=target, count_only=count_only)

    def unit_test_katakana(
        self,
        target_list: list=['all', 'partial', 'none'],
        count_only: bool=True
    ):
        logger.info("Katakana Unit Test")
        for target in target_list:
            self.test_katakana(target=target, count_only=count_only)

    def unit_test_hit_count(
        self,
        target_list: list=[-1, 0, 1, 2, 3],
        ineq_list: list=['==', '>', '<', '>=', '<='],
        count_only: bool=True
    ):
        logger.info("Hit Count Unit Test")
        for target in target_list:
            for ineq in ineq_list:
                self.test_hit_count(target=target, ineq=ineq, count_only=count_only)

    def unit_test_timestamp_usec(
        self,
        target_list: list=[-1, 0, 1234567],
        ineq_list: list=['==', '>', '<', '>=', '<='],
        ref_mode_list: list=['oldest', 'newest'],
        count_only: bool=True
    ):
        logger.info("Timestamp USEC Unit Test")
        for ref_mode in ref_mode_list:
            for target in target_list:
                for ineq in ineq_list:
                    self.test_times_usec(target=target, ineq=ineq, ref_mode=ref_mode, target_unit='usec', count_only=count_only)

    def unit_test_timestamp_days(
        self,
        target_list: list=[-1, 0, 30, 90, 270],
        ineq_list: list=['==', '>', '<', '>=', '<='],
        ref_mode_list: list=['oldest', 'newest'],
        count_only: bool=True
    ):
        logger.info("Timestamp Days Unit Test")
        for ref_mode in ref_mode_list:
            for target in target_list:
                for ineq in ineq_list:
                    self.test_times_usec(target=target, ineq=ineq, ref_mode=ref_mode, target_unit='days', count_only=count_only)

    def unit_test_timestamp_years(
        self,
        target_list: list=[-1, 0, 1, 2],
        ineq_list: list=['==', '>', '<', '>=', '<='],
        ref_mode_list: list=['oldest', 'newest'],
        count_only: bool=True
    ):
        logger.info("Timestamp Years Unit Test")
        for ref_mode in ref_mode_list:
            for target in target_list:
                for ineq in ineq_list:
                    self.test_times_usec(target=target, ineq=ineq, ref_mode=ref_mode, target_unit='years', count_only=count_only)

    def unit_test_timestamp(
        self,
        ineq_list: list=['==', '>', '<', '>=', '<='],
        ref_mode_list: list=['oldest', 'newest'],
        count_only: bool=True
    ):
        logger.info("Timestamp Unit Test")
        self.unit_test_timestamp_usec(ineq_list=ineq_list, ref_mode_list=ref_mode_list, count_only=count_only)
        self.unit_test_timestamp_days(ineq_list=ineq_list, ref_mode_list=ref_mode_list, count_only=count_only)
        self.unit_test_timestamp_years(ineq_list=ineq_list, ref_mode_list=ref_mode_list, count_only=count_only)

    def unit_test_len_word_results(
        self,
        target_list: list=[-1, 0, 1, 2, 3],
        ineq_list: list=['==', '>', '<', '>=', '<='],
        count_only: bool=True
    ):
        logger.info("len(word_results) Unit Test")
        for target in target_list:
            for ineq in ineq_list:
                self.test_len_word_results(target=target, ineq=ineq, count_only=count_only)

    def cumulative_unit_test(self):
        logger.info("Cumulative Unit Test")
        unit_test_method_list = [
            self.unit_test_kanji,
            self.unit_test_hiragana,
            self.unit_test_katakana,
            self.unit_test_hit_count,
            self.unit_test_timestamp,
            self.unit_test_len_word_results
        ]
        for unit_test_method in unit_test_method_list:
            unit_test_method()
