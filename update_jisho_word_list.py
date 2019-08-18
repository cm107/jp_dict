"""
Script for updating jisho word list, where the word list is saved as a pkl file.

Usage:
    update_jisho_word_list.py (--history_json_path PATH) [--save_file_path PATH]
    update_jisho_word_list.py (-h | --help)

Options:
    --history_json_path Path to the Chrome history json file that was exported from Chrome.
    --save_file_path Path to where you would like to save your word list.
    -h --help   Show this message and exit
"""

from docopt import docopt
args = docopt(__doc__, version='Alpha 1.0')
print(args)

from src.submodules.logger.logger_handler import logger
from src.submodules.common_utils.file_utils import file_exists
from src.submodules.logger.log_writer import log_writer
from src.submodules.common_utils.path_utils import rel_to_abs_path
from src.conf.paths import PathConf
from src.tools.word_list_updater import WordListUpdater

history_json_path = args['--history_json_path']
history_json_path = rel_to_abs_path(history_json_path) if history_json_path is not None \
    else None
if not file_exists(history_json_path):
    logger.error(f"File not found: {history_json_path}")
    raise Exception

save_file_path = args['--save_file_path']
save_file_path = rel_to_abs_path(save_file_path) if save_file_path is not None \
    else PathConf.jisho_history_word_list_save_path

word_list_updater = WordListUpdater(
    history_json_path=history_json_path,
    save_file_path=save_file_path
)
word_list_updater.run()

log_writer.write_all_logs()