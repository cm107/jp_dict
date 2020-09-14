from common_utils.path_utils import get_all_files_of_extension, get_rootname_from_path
from src.refactored.kotobank.digital_daijisen import ParsedItemListHandler
from logger import logger

dump_dir = 'digital_daijisen_dump'
dump_paths = get_all_files_of_extension(dump_dir, extension='json')

relevant_count = 0
include_list = ['Hinshi', 'DefinitionNumber', 'Gaiji']
for dump_path in dump_paths:
    item_list_handler = ParsedItemListHandler.load_from_path(dump_path)
    
    if not item_list_handler.contains_class_names(include_list):
        continue

    search_word = get_rootname_from_path(dump_path)
    logger.yellow(f'search_word: {search_word}')

    for item_list in item_list_handler:
        # if item_list.contains_class_names(include_list):
        logger.cyan(item_list.class_name_list)
        print(item_list.preview_str())
        item_group_list = item_list.group_items()
        logger.purple(item_group_list.plain_str)

print(f'relevant_count: {relevant_count}')