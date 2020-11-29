from src.refactored.jisho_structs import JishoSearchQuery, MeaningGroupHandler
from common_utils.path_utils import get_all_files_of_extension, get_rootname_from_path
from logger import logger
from tqdm import tqdm

jisho_parse_dump_dir = 'jisho_parse_dump'
dump_paths = get_all_files_of_extension(jisho_parse_dump_dir, extension='json')

relevant_groups = MeaningGroupHandler()
pbar = tqdm(total=len(dump_paths), unit='dump(s)')
pbar.set_description('Searching For Unknown Tags')
for dump_path in dump_paths:
    search_word = get_rootname_from_path(dump_path)
    query = JishoSearchQuery.load_from_path(dump_path)
    matches = query.exact_matches + query.nonexact_matches
    for match in matches:
        for group in match.meaning_section.meaning_groups:
            if group.meaning_tags.is_suffix:
                logger.purple(match.custom_str())
            if group.meaning_tags.contains_unknown_tag and group not in relevant_groups:
                relevant_groups.append(group)
    pbar.update()

unknown_tag_list = []
for group in relevant_groups:
    for tag in group.meaning_tags.unknown_tag_parts:
        if tag not in unknown_tag_list:
            unknown_tag_list.append(tag)

logger.yellow(f'Number of Unknown Tags: {len(unknown_tag_list)}')
for tag in unknown_tag_list:
    logger.purple(tag.meaning_tag_text)