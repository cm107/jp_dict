#%%
from logger import logger
from common_utils.path_utils import get_script_dir, rel_to_abs_path
from common_utils.adv_file_utils import delete_all_files_of_extension
from src.conf.paths import PathConf
from src.util.loaders import load_search_word_cache_handler
from src.lib.history_parsing.search_word_cache_filter import SearchWordCacheFilter

script_dir = rel_to_abs_path(get_script_dir())
dump_dir = f"{script_dir}/filter_test_dump"
delete_all_files_of_extension(dir_path=dump_dir, extension='txt')
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
    no_eng_chars=True,
    no_typo_chars=True
)
relevant_count = len(words)
f = open(f"{dump_dir}/relevant.txt", "w+")
logger.cyan(f"Relevant word count: {len(words)}/{len(tagged_word_cache_list)}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.green(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%
words = word_filter.get_wildcard_results()
f = open(f"{dump_dir}/wildcard.txt", "w+")
logger.cyan(f"Wildcard word count: {len(words)}/{len(tagged_word_cache_list)}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%
words = word_filter.get_eng_char_results()
f = open(f"{dump_dir}/eng_char.txt", "w+")
logger.cyan(f"English Character word count: {len(words)}/{len(tagged_word_cache_list)}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%
words = word_filter.get_typo_char_results()
f = open(f"{dump_dir}/typo.txt", "w+")
logger.cyan(f"Typo Character word count: {len(words)}/{len(tagged_word_cache_list)}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%
words = word_filter.get_garbage_char_results()
f = open(f"{dump_dir}/garbage.txt", "w+")
logger.cyan(f"Garbage Character word count: {len(words)}/{len(tagged_word_cache_list)}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%
words = word_filter.get_hiragana_tag_results(tag='partial')
f = open(f"{dump_dir}/hiragana_partial.txt", "w+")
logger.cyan(f"Partial Hiragana word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%
words = word_filter.get_hiragana_tag_results(tag='all')
f = open(f"{dump_dir}/hiragana_all.txt", "w+")
logger.cyan(f"All Hiragana word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%
words = word_filter.get_katakana_tag_results(tag='partial')
f = open(f"{dump_dir}/katakana_partial.txt", "w+")
logger.cyan(f"Partial Katakana word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%
words = word_filter.get_katakana_tag_results(tag='all')
f = open(f"{dump_dir}/katakana_all.txt", "w+")
logger.cyan(f"All Katakana word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%
words = word_filter.get_kanji_tag_results(tag='partial')
f = open(f"{dump_dir}/kanji_partial.txt", "w+")
logger.cyan(f"Partial Kanji word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%
words = word_filter.get_kanji_tag_results(tag='all')
f = open(f"{dump_dir}/kanji_all.txt", "w+")
logger.cyan(f"All Kanji word count: {len(words)}/{relevant_count}")
#%%
for i, word in zip(range(len(words)), words):
    logger.yellow(f"------------{i}------------")
    logger.blue(word)
    f.write(f"------------{i}------------\n")
    f.write(f"{word}\n")
f.close()
#%%