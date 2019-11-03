import pickle
from src.conf.paths import PathConf
from logger import logger
from common_utils.path_utils import get_all_files_of_extension

soup_paths = get_all_files_of_extension(dir_path=PathConf.jisho_soups_dir, extension='pth')
soup_paths.sort()

for i, soup_path in enumerate(soup_paths):
    logger.info(f"{i}: {soup_path}")
    soup = pickle.load(open(soup_path, 'rb'))
    search_word = soup.title.text.split('-')[0][:-1]
    logger.purple(f"search_word: {search_word}")