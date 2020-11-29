from common_utils.file_utils import make_dir_if_not_exists, file_exists
from src.refactored.jisho_matches import SearchWordMatchesHandler
from common_utils.path_utils import get_all_files_of_extension, get_rootname_from_path
from tqdm import tqdm
from src.refactored.kotobank.kotobank_structs import KotobankWordHtmlParser, KotobankResultList
import json
from logger import logger

priority_dict = json.load(open('dictionary_priority.json', 'r'))
target_dictionary_name = "日本大百科全書(ニッポニカ)の解説"
results = KotobankResultList.load_from_dir('kotobank_dump')
relevant_results = [result for result in results if target_dictionary_name in result.dictionary_names]

progress_save = 'progress.json'
if file_exists(progress_save):
    progress_dict = json.load(open(progress_save, 'r'))
else:
    progress_dict = {'progress': 0}

pbar = tqdm(total=len(relevant_results), unit='searches')
for i, relevant_result in enumerate(relevant_results):
    if i <= progress_dict['progress']:
        pbar.update()
        continue
    pbar.set_description(relevant_result.search_word)
    parser = KotobankWordHtmlParser.from_search_word(relevant_result.search_word)
    result = parser.parse()
    result.save_to_path(f'kotobank_dump/{relevant_result.search_word}.json', overwrite=True)

    progress_dict['progress'] = progress_dict['progress'] + 1
    json.dump(progress_dict, open(progress_save, 'w'))
    pbar.update()

# parser = KotobankWordHtmlParser.from_search_word('殊勝')
# result = parser.parse()