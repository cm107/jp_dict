import requests, time, cv2
from PIL import Image
from requests.models import Response

from ...submodules.logger.logger_handler import logger
from ...submodules.common_utils.path_utils import get_extension_from_path, \
    get_all_files_in_extension_list, get_rootname_from_path, \
    get_all_files_of_extension
from ...submodules.common_utils.file_utils import delete_file
from .cache import CacheHandler

class FaviconExtractor:
    def __init__(self, favicon_url_list: list, icon_dump_dir: str):
        self.favicon_url_list = favicon_url_list
        self.icon_dump_dir = icon_dump_dir
        self.extension_list = ['png', 'ico']
        self.cache_handler = CacheHandler()

    def download_icons(self):
        logger.info(f"Downloading Icons")
        for i, favicon_url in zip(range(len(self.favicon_url_list)), self.favicon_url_list):
            if favicon_url is not None:
                try:
                    file_extension = get_extension_from_path(favicon_url)
                except Exception as e:
                    logger.warning(f"{i}: Encountered {str(e)}. Skipping.")
                    continue
                
                if favicon_url.startswith('chrome-extension'):
                    continue
                
                if file_extension in self.extension_list:
                    is_new = self.cache_handler.process(item=favicon_url)
                    if is_new:
                        try:
                            response = requests.get(favicon_url, stream=True)
                        except Exception as e:
                            logger.warning(f"{i}: Encountered {str(e)} at {favicon_url}. Skipping.")
                            continue
        
                        rootname = str(i)
                        while len(rootname) < 6:
                            rootname = '0' + rootname
                        icon_dump_filename = f'{rootname}.{file_extension}'
                        icon_dump_path = f'{self.icon_dump_dir}/{icon_dump_filename}'
                        write_start_time = time.time()
                        with open(icon_dump_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        write_end_time = time.time()
                        elapsed_time = round(write_end_time - write_start_time, 3)
                        logger.good(f"{i}: {elapsed_time} s {icon_dump_filename}")
                else:
                    logger.warning(f"{i}: Encountered extension: {file_extension}. Skipping.")
        self.cache_handler.print_cache_summary()

    def convert_ico2png(self):
        logger.info(f"Converting ICO icons to PNG")
        pathlist = get_all_files_of_extension(
            dir_path=self.icon_dump_dir,
            extension='ico'
        )
        for path in pathlist:
            rootname = get_rootname_from_path(path)
            save_path = f"{self.icon_dump_dir}/{rootname}.png"
            try:
                img = Image.open(path)
            except Exception as e:
                logger.warning(f"Encountered {e}. Skipping")
            img.save(save_path, 'png')
            delete_file(path)
            old_filename = f"{rootname}.ico"
            new_filename = f"{rootname}.png"
            logger.info(f"Converted {old_filename} -> {new_filename}")

    def delete_duplicates(self):
        logger.info(f"Deleting Duplicate Icons")
        pathlist = get_all_files_in_extension_list(
            dir_path = self.icon_dump_dir,
            extension_list=self.extension_list
        )

        unique_list = []
        duplicate_list = []
        unreadable_list = []
        for path in pathlist:
            img = cv2.imread(path)
            if img is None:
                unreadable_list.append(path)
                logger.yellow("unreadable hit")
                continue
            if len(unique_list) == 0:
                unique_list.append(path)
                continue
            
            is_duplicate = False
            for unique_path in unique_list:
                unique_img = cv2.imread(unique_path)
                if img.shape != unique_img.shape:
                    continue
                img_diff = cv2.subtract(unique_img, img)
                b, g, r = cv2.split(img_diff)
                if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                    is_duplicate = True
                    break
            if is_duplicate:
                duplicate_list.append(path)
                logger.yellow("duplicate hit")
            else:
                unique_list.append(path)
                logger.green("unique hit")
        
        logger.cyan(f"=========Unique Paths: {len(unique_list)}=========")
        for unique_path in unique_list:
            logger.blue(unique_path)
        logger.cyan(f"=========Duplicate Paths: {len(duplicate_list)} =========")
        for duplicate_path in duplicate_list:
            logger.blue(duplicate_path)
        logger.cyan(f"=========Unreadable Paths: {len(unreadable_list)} =========")
        for unreadable_path in unreadable_list:
            logger.blue(unreadable_path)

        if len(duplicate_list) > 0:
            for duplicate_path in duplicate_list:
                delete_file(duplicate_path)
        if len(unreadable_list) > 0:
            for unreadable_path in unreadable_list:
                delete_file(unreadable_path)