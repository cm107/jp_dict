from src.conf.paths import PathConf
from src.util.loaders import load_word_matches
from logger import logger

word_matches_save_path = f"{PathConf.word_matches_save_dir}/test.pkl"
matching_results_dict = load_word_matches(word_matches_save_path)

for i, key, matching_results in zip(
    range(len(matching_results_dict.keys())),
    matching_results_dict.keys(),
    matching_results_dict.values()
):
    logger.yellow(f"{i}: {key}")
    logger.cyan(matching_results)