import inspect
from common_utils.path_utils import get_filename
from common_utils.adv_file_utils import get_filepaths_in_dir, get_dirpaths_in_dir
from common_utils.check_utils import check_value

def get_kana_maps(text: str, furigana_parts: list, okurigana_parts: list) -> list:
    kana_maps = []
    for character in text:
        if len(okurigana_parts) == 0 or character != okurigana_parts[0]:
            if len(furigana_parts) > 0:
                kana_map = {'written_form': character, 'reading': furigana_parts[0]}
                furigana_parts = furigana_parts[1:]
            else:
                kana_map = {'written_form': character, 'reading': ''}
            kana_maps.append(kana_map)
        else: # len(okurigana_parts) > 0 and character == okurigana_parts[0]
            kana_map = {'written_form': character, 'reading': okurigana_parts[0]}
            okurigana_parts = okurigana_parts[1:]
            kana_maps.append(kana_map)
    return kana_maps

def unique(a):
    """ return the list with duplicate elements removed """
    return list(set(a))

def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))

def a_not_in_b(a, b):
    return list(set(a) - set(b))

def reverse_union(a, b):
    return a_not_in_b(union(a, b), intersect(a, b))

def recursively_get_all_matches_under_dirpath(dirpath: str, target_name: str, target_type: str) -> list:
    """
    TODO: Add this method to common_utils package.

    target_type
    'directory' or 'd': Recursively search for directory names that match target_name
    'file' or 'f': Recursively search for file names that match target_name
    """
    target_type = target_type.lower()
    check_value(item=target_type, valid_value_list=['directory', 'd', 'file', 'f'])
    matches = []
    dirpath_queue = [dirpath]
    done_dirpaths = []
    while len(dirpath_queue) > 0:
        for current_dir in dirpath_queue:
            dirpaths = get_dirpaths_in_dir(current_dir)
            dirpath_queue.extend(dirpaths)
            if target_type in ['directory', 'd']:
                for path in dirpaths:
                    if get_filename(path) == target_name:
                        matches.append(path)
            elif target_type in ['file', 'f']:
                filepaths = get_filepaths_in_dir(current_dir)
                for path in filepaths:
                    if get_filename(path) == target_name:
                        matches.append(path)
            else:
                raise Exception
            done_dirpaths.append(current_dir)
        for done_dirpath in done_dirpaths:
            del dirpath_queue[dirpath_queue.index(done_dirpath)]
        done_dirpaths = []
    return matches

def get_indent_str(indent: int) -> str:
    """
    TODO: Add this method to common_utils package.
    """
    return ' ' * indent

def get_method_name() -> str:
    """
    TODO: Add this method to common_utils package.
    """
    return inspect.getframeinfo(inspect.currentframe().f_back).function

def get_method_name_through_wrapper() -> str:
    """
    TODO: Add this method to common_utils package.
    """
    return inspect.getframeinfo(inspect.currentframe().f_back.f_back).code_context[0].replace(' ', '').replace('self.', '').replace('()\n', '')