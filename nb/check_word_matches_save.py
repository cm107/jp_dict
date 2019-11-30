import pickle
from src.conf.paths import PathConf
from logger import logger

word_matches_save_path = f"{PathConf.word_matches_save_dir}/soup_test.pkl"
checkpoint = pickle.load(open(word_matches_save_path, 'rb'))
results = checkpoint['results']

for i, result in enumerate(results):
    search_word = result['search_word']
    matching_results = result['matching_results']
    logger.yellow(f"{i}: {search_word}")
    logger.cyan(matching_results)