import pickle
from src.conf.paths import PathConf
from logger import logger
from src.lib.history_parsing.filter.core import TaggedCache

word_matches_save_path = f"{PathConf.word_matches_save_dir}/soup_test0.pkl"
checkpoint = pickle.load(open(word_matches_save_path, 'rb'))
tagged_cache_list = checkpoint['tagged_cache_list']

from src.lib.history_parsing.filter.tagged_cache_filter import TaggedCacheFilter
from src.lib.history_parsing.sorter.tagged_cache_sorter import DefaultTaggedCacheSorter, SorterCompose
from src.util.time_utils import get_days_elapsed_from_time_usec

results = tagged_cache_list.copy()

# results = TaggedCacheFilter.filter_by_len_word_results(tagged_cache_list=results, target=1, ineq='==', skip_empty_results=True)
# results = DefaultTaggedCacheSorter.sort_by_times_usec(tagged_cache_list=results, ref_mode='oldest', reverse=True)
# results = DefaultTaggedCacheSorter.sort_by_common_words(tagged_cache_list=results, reverse=False)
# results = DefaultTaggedCacheSorter.sort_by_wanikani_level(tagged_cache_list=results, reverse=False)
# results = DefaultTaggedCacheSorter.sort_by_jlpt_level(tagged_cache_list=results, reverse=False)
# results = DefaultTaggedCacheSorter.sort_by_hit_count(tagged_cache_list=results, reverse=False)

results = SorterCompose.sort0(results)

# TODO: Need to make accomodations for WordMatchFilter and WordMatchSorter next.

for i, tagged_cache in enumerate(results):
    tagged_cache = TaggedCache.buffer(tagged_cache)
    logger.yellow(f"{i}: {tagged_cache.search_word} ({tagged_cache.hit_count} hits), {get_days_elapsed_from_time_usec(tagged_cache.oldest_time_usec)} days ago")
    logger.cyan(tagged_cache.word_results)

