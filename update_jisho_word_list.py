"""
Script for updating jisho word list, where the word list is saved as a pkl file.

Usage:
    update_jisho_word_list.py (--history_json_path PATH) [--save_file_path PATH]
    update_jisho_word_list.py (--history_json_dir PATH) [--save_file_path PATH]
    update_jisho_word_list.py (-h | --help)

Options:
    --history_json_path Path to the Chrome history json file that was exported from Chrome.
    --history_json_dir Path to the Chrome history directory that contains all of the
                       json files that you exported from Chrome.
    --save_file_path Path to where you would like to save your word list.
    -h --help   Show this message and exit
"""

from docopt import docopt
args = docopt(__doc__, version='Alpha 1.0')
print(args)

from logger import logger
from common_utils.file_utils import file_exists, dir_exists
from common_utils.path_utils import rel_to_abs_path
from common_utils.adv_file_utils import get_dirpaths_in_dir
from src.conf.paths import PathConf
from src.tools.word_list_updater import WordListUpdater

history_json_path = args['--history_json_path']
history_json_path = rel_to_abs_path(history_json_path) if history_json_path is not None \
    else None
if history_json_path is not None and not file_exists(history_json_path):
    logger.error(f"File not found: {history_json_path}")
    raise Exception

history_json_dir = args['--history_json_dir']
history_json_dir = rel_to_abs_path(history_json_dir) if history_json_dir is not None \
    else None
if history_json_dir is not None and not dir_exists(history_json_dir):
    logger.error(f"Directory not found: {history_json_dir}")
    raise Exception

save_file_path = args['--save_file_path']
save_file_path = rel_to_abs_path(save_file_path) if save_file_path is not None \
    else PathConf.jisho_history_word_list_save_path

if history_json_path is not None:
    logger.info(f"Processing: {history_json_path}")
    word_list_updater = WordListUpdater(
        history_json_path=history_json_path,
        save_file_path=save_file_path
    )
    word_list_updater.run()
elif history_json_dir is not None:
    history_folder_dirs = get_dirpaths_in_dir(dir_path=history_json_dir)
    for history_folder_dir in history_folder_dirs:
        history_json_path = f"{history_folder_dir}/Chrome/BrowserHistory.json"
        if not file_exists(history_json_path):
            logger.error(f"File not found: {history_json_path}")
            raise Exception
        logger.info(f"Processing: {history_json_path}")
        word_list_updater = WordListUpdater(
            history_json_path=history_json_path,
            save_file_path=save_file_path
        )
        word_list_updater.run()
else:
    logger.error(f"Oops! Something went wrong at parameter parsing.")
    raise Exception