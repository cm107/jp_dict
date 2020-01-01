from logger import logger
from ..lib.history_parsing.filter.tag_filter import TagFilter
from ..lib.history_parsing.cache import Cache
from ..lib.history_parsing.filter.core import TaggedCache
from ..lib.history_parsing.filter.soup_cache_filter import TaggedSoupCache
from ..util.utils import get_indent_str

raise NotImplementedError

class LearnFilterTest:
    def __init__(self):
        self.tagged_cache_list = self.construct_tagged_cache_list()
        self.learned_list = self.construct_learned_list()

    def construct_tagged_cache_list(self) -> list:
        cache = Cache(item=item)
        tagged_cache = TaggedSoupCache(cache=cache)
        raise NotImplementedError

    def construct_learned_list(self) -> list:
        unique_list = [f"unique{i}" for i in range(100)]
        overlap_list = [f"overlap{i}" for i in range(200)]
        return unique_list + overlap_list

    def filter_by_learned(self, target: str, match_search_word: str, match_jap_vocab: str, match_other_form: str, match_operator: str, exclude_empty_results=True) -> list:
        return TagFilter.filter_by_learned(
            tagged_cache_list=self.tagged_cache_list, learned_list=self.learned_list, target=target,
            match_search_word=match_search_word, match_jap_vocab=match_jap_vocab, match_other_form=match_other_form,
            match_operator=match_operator, exclude_empty_results=True
        )

    def show_results(self, name: str, results: list, count_only: bool=False, indent: int=0):
        logger.yellow(f"{get_indent_str(indent)}len({name}): {len(results)}")
        if not count_only:
            for i, tagged_cache in enumerate(results):
                tagged_cache = TaggedCache.buffer(tagged_cache)
                logger.cyan(f"{get_indent_str(indent)}{i}: {tagged_cache.search_word}")
                logger.green(tagged_cache.word_results)

    def test_learned(
        self,
        target: str,
        match_search_word: str, match_jap_vocab: str, match_other_form: str, match_operator: str,
        count_only: bool=False, indent: int=0
    ):
        self.show_results(
            name=f"{target}(sw={match_search_word},jv={match_jap_vocab},of={match_other_form},op={match_operator})",
            results=self.filter_by_learned(
                target=target,
                match_search_word=match_search_word,
                match_jap_vocab=match_jap_vocab,
                match_other_form=match_other_form,
                match_operator=match_operator
            ),
            count_only=count_only, indent=indent
        )

    def unit_test_learned(
        self,
        target_list: list=['learned', 'not_learned'],
        match_search_word_list: list=['off', 'writing'],
        match_jap_vocab_list: list=['off', 'writing', 'reading', 'both'],
        match_other_form_list: list=['off', 'writing', 'reading', 'both'],
        match_operator_list: list=['or', 'and'],
        count_only: bool=True, title_indent: int=0, contents_indent: int=0
    ):
        logger.info(f"{get_indent_str(title_indent)}Learned Unit Test")
        for target in target_list:
            for match_search_word in match_search_word_list:
                for match_jap_vocab in match_jap_vocab_list:
                    for match_other_form in match_other_form_list:
                        for match_operator in match_operator_list:
                            self.test_learned(
                                target=target,
                                match_search_word=match_search_word,
                                match_jap_vocab=match_jap_vocab,
                                match_other_form=match_other_form,
                                match_operator=match_operator,
                                count_only=count_only, indent=contents_indent
                        )