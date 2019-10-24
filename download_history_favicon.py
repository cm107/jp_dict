"""
Script for downloading all favicon icons from chrome browser history.

Usage:
    download_history_favicon.py (--history_json_path PATH) [--icon_dump_dir PATH]
    download_history_favicon.py (-h | --help)

Options:
    --history_json_path Path to the Chrome history json file that was exported from Chrome.
    --icon_dump_dir Path to the directory where you would like to download all of
                    the favicon icon images to.
    -h --help   Show this message and exit
"""

from docopt import docopt
args = docopt(__doc__, version='Alpha 1.0')
print(args)

from logger import logger
from common_utils.path_utils import rel_to_abs_path
from common_utils.file_utils import init_dir, file_exists
from src.tools.history_parsing.favicon_downloader import FaviconDownloader
from src.conf.paths import PathConf

history_json_path = args['--history_json_path']
history_json_path = rel_to_abs_path(history_json_path) if history_json_path is not None \
    else None
if not file_exists(history_json_path):
    logger.error(f"File not found: {history_json_path}")
    raise Exception

icon_dump_dir = args['--icon_dump_dir']
icon_dump_dir = rel_to_abs_path(icon_dump_dir) if icon_dump_dir is not None \
    else PathConf.favicon_dir
init_dir(dir_path=icon_dump_dir, ask_permission=False)

favicon_downloader = FaviconDownloader(
    history_json_path=history_json_path,
    icon_dump_dir=icon_dump_dir
)
favicon_downloader.run()

logger.link_log_dir(log_dir=f"{PathConf.root_dir}/logs")