import pickle
from src.conf.paths import PathConf
from logger import logger
from src.lib.history_parsing.filter.core import TaggedCache

word_matches_save_path = f"{PathConf.word_matches_save_dir}/soup_test0.pkl"
checkpoint = pickle.load(open(word_matches_save_path, 'rb'))
tagged_cache_list = checkpoint['tagged_cache_list']

from src.lib.history_parsing.filter.tag_filter import TagFilter
# kanji_all_tagged_cache_list = TagFilter.filter_by_kanji_tag(tagged_cache_list=tagged_cache_list, target='all', skip_empty_results=True)
# garbage_cache_list = TagFilter.filter_by_garbage_chars_tag_group(tagged_cache_list=tagged_cache_list, target='true', skip_empty_results=False)
# multiple_word_result_cache_list = TagFilter.filter_by_len_word_results(tagged_cache_list=tagged_cache_list, target=2, ineq='>=', skip_empty_results=True)
results = TagFilter.filter_by_len_word_results(tagged_cache_list=tagged_cache_list, target=1, ineq='==', skip_empty_results=True)

# TODO: Need to make accomodations for WordMatchFilter and WordMatchSorter next.

for i, tagged_cache in enumerate(results):
    tagged_cache = TaggedCache.buffer(tagged_cache)
    logger.yellow(f"{i}: {tagged_cache.search_word}")
    logger.cyan(tagged_cache.word_results)

