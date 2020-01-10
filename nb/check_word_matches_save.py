import pickle
from src.conf.paths import PathConf
from logger import logger
from src.lib.history_parsing.filter.core import TaggedCache

word_matches_save_path = f"{PathConf.word_matches_save_dir}/soup_test0.pkl"
checkpoint = pickle.load(open(word_matches_save_path, 'rb'))
tagged_cache_list = checkpoint['tagged_cache_list']

jlpt_all_notes_save_path = f"{PathConf.anki_dir}/jlpt_all_save.pkl"
jlpt_all_vocab_list = pickle.load(open(jlpt_all_notes_save_path, 'rb'))
anime_vocab_notes_save_path = f"{PathConf.anki_dir}/anime_vocab_save.pkl"
anime_vocab_vocab_list = pickle.load(open(anime_vocab_notes_save_path, 'rb'))
learned_list = jlpt_all_vocab_list + anime_vocab_vocab_list

from src.lib.history_parsing.filter.tagged_cache_filter import TaggedCacheFilter
from src.lib.history_parsing.sorter.tagged_cache_sorter import DefaultTaggedCacheSorter, SorterCompose
from src.util.time_utils import get_days_elapsed_from_time_usec

# TODO: Find and remove duplicates.

results = tagged_cache_list.copy()

results = SorterCompose.sort0(tagged_cache_list=results, learned_list=learned_list)

for i, tagged_cache in enumerate(results):
    tagged_cache = TaggedCache.buffer(tagged_cache)
    logger.yellow(f"{i}: {tagged_cache.search_word} ({tagged_cache.hit_count} hits), {get_days_elapsed_from_time_usec(tagged_cache.oldest_time_usec)} days ago")
    logger.cyan(tagged_cache.word_results)

