#%%
from src.submodules.logger.logger_handler import logger
from src.conf.paths import PathConf
from src.util.loaders import load_search_word_cache_handler
from src.lib.history_parsing.search_word_cache_filter import SearchWordCacheFilter

search_word_cache_handler = load_search_word_cache_handler(PathConf.jisho_history_word_list_save_path)


#%%
word_filter = SearchWordCacheFilter(
    cache_list=search_word_cache_handler.cache_list,

)
word_filter.apply_tags()

tagged_word_cache_list = word_filter.tagged_word_cache_handler.tagged_word_cache_list



words = word_filter.get_eng_char_results()
#%%
words = word_filter.get_filtered_results(
    no_wildcards=True,
    no_eng_chars=True
)
relevant_count = len(words)
logger.cyan(f"Relevant word count: {len(words)}/{len(tagged_word_cache_list)}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.green(word)
#%%
words = word_filter.get_wildcard_results()
logger.cyan(f"Wildcard word count: {len(words)}/{len(tagged_word_cache_list)}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
#%%
words = word_filter.get_eng_char_results()
logger.cyan(f"English Character word count: {len(words)}/{len(tagged_word_cache_list)}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
#%%
words = word_filter.get_typo_char_results()
logger.cyan(f"Typo Character word count: {len(words)}/{len(tagged_word_cache_list)}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
#%%
words = word_filter.get_garbage_char_results()
logger.cyan(f"Garbage Character word count: {len(words)}/{len(tagged_word_cache_list)}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
#%%
words = word_filter.get_hiragana_tag_results(tag='partial')
logger.cyan(f"Partial Hiragana word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
#%%
words = word_filter.get_hiragana_tag_results(tag='all')
logger.cyan(f"All Hiragana word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
#%%
words = word_filter.get_katakana_tag_results(tag='partial')
logger.cyan(f"Partial Katakana word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
#%%
words = word_filter.get_katakana_tag_results(tag='all')
logger.cyan(f"All Katakana word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
#%%
words = word_filter.get_kanji_tag_results(tag='partial')
logger.cyan(f"Partial Kanji word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
#%%
words = word_filter.get_kanji_tag_results(tag='all')
logger.cyan(f"All Kanji word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
#%%