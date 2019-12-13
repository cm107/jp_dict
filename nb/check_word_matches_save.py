import pickle
from src.conf.paths import PathConf
from logger import logger
from src.lib.history_parsing.filter.core import TaggedCache

word_matches_save_path = f"{PathConf.word_matches_save_dir}/soup_test0.pkl"
checkpoint = pickle.load(open(word_matches_save_path, 'rb'))
tagged_cache_list = checkpoint['tagged_cache_list']

from src.lib.history_parsing.filter.tag_filter import TagFilter
kanji_all_tagged_cache_list = TagFilter.filter_by_kanji_tag(tagged_cache_list=tagged_cache_list, target='all', skip_empty_results=True)
kanji_partial_tagged_cache_list = TagFilter.filter_by_kanji_tag(tagged_cache_list=tagged_cache_list, target='partial', skip_empty_results=True)
kanji_none_tagged_cache_list = TagFilter.filter_by_kanji_tag(tagged_cache_list=tagged_cache_list, target='none', skip_empty_results=True)

hiragana_all_tagged_cache_list = TagFilter.filter_by_hiragana_tag(tagged_cache_list=tagged_cache_list, target='all', skip_empty_results=True)
hiragana_partial_tagged_cache_list = TagFilter.filter_by_hiragana_tag(tagged_cache_list=tagged_cache_list, target='partial', skip_empty_results=True)
hiragana_none_tagged_cache_list = TagFilter.filter_by_hiragana_tag(tagged_cache_list=tagged_cache_list, target='none', skip_empty_results=True)

katakana_all_tagged_cache_list = TagFilter.filter_by_katakana_tag(tagged_cache_list=tagged_cache_list, target='all', skip_empty_results=True)
katakana_partial_tagged_cache_list = TagFilter.filter_by_katakana_tag(tagged_cache_list=tagged_cache_list, target='partial', skip_empty_results=True)
katakana_none_tagged_cache_list = TagFilter.filter_by_katakana_tag(tagged_cache_list=tagged_cache_list, target='none', skip_empty_results=True)

logger.purple(f"len(kanji_all_tagged_cache_list): {len(kanji_all_tagged_cache_list)}")
logger.purple(f"len(kanji_partial_tagged_cache_list): {len(kanji_partial_tagged_cache_list)}")
logger.purple(f"len(kanji_none_tagged_cache_list): {len(kanji_none_tagged_cache_list)}")

logger.purple(f"len(hiragana_all_tagged_cache_list): {len(hiragana_all_tagged_cache_list)}")
logger.purple(f"len(hiragana_partial_tagged_cache_list): {len(hiragana_partial_tagged_cache_list)}")
logger.purple(f"len(hiragana_none_tagged_cache_list): {len(hiragana_none_tagged_cache_list)}")

logger.purple(f"len(katakana_all_tagged_cache_list): {len(katakana_all_tagged_cache_list)}")
logger.purple(f"len(katakana_partial_tagged_cache_list): {len(katakana_partial_tagged_cache_list)}")
logger.purple(f"len(katakana_none_tagged_cache_list): {len(katakana_none_tagged_cache_list)}")

# for i, tagged_cache in enumerate(kanji_all_tagged_cache_list):
#     tagged_cache = TaggedCache.buffer(tagged_cache)
#     logger.yellow(f"{i}: {tagged_cache.search_word}")
#     logger.cyan(tagged_cache.word_results)