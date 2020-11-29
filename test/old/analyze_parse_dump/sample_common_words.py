from src.refactored.jisho_structs import JishoSearchQuery, DictionaryEntryList
from common_utils.file_utils import make_dir_if_not_exists, file_exists
from common_utils.path_utils import get_all_files_of_extension, get_rootname_from_path
from logger import logger
from tqdm import tqdm

sample_dir = 'samples'
common_sample_save = f'{sample_dir}/common_sample.json'

if not file_exists(common_sample_save):
    jisho_parse_dump_dir = 'jisho_parse_dump'
    dump_paths = get_all_files_of_extension(jisho_parse_dump_dir, extension='json')[:100]
    matches = DictionaryEntryList()
    pbar = tqdm(total=len(dump_paths), unit='dump(s)')
    pbar.set_description('Getting Common Matches')
    for dump_path in dump_paths:
        for match in JishoSearchQuery.load_from_path(dump_path).matches:
            if match.concept_labels.is_common and match not in matches:
                matches.append(match)
        pbar.update()
    make_dir_if_not_exists(sample_dir)
    matches.save_to_path(common_sample_save)
else:
    matches = DictionaryEntryList.load_from_path(common_sample_save)

logger.yellow(f'len(matches): {len(matches)}')
for match in matches:
    logger.cyan(match.word_representation.simple_repr)