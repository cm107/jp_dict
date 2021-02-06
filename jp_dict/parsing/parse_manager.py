from __future__ import annotations
import urllib
from typing import List
from tqdm import tqdm
import json
from common_utils.base.basic import BasicLoadableObject
from common_utils.file_utils import dir_exists, file_exists, make_dir_if_not_exists, \
    delete_all_files_in_dir, delete_file_if_exists, delete_dir_if_exists
from common_utils.path_utils import recursively_get_all_matches_under_dirpath, \
    get_all_files_of_extension, get_rootname_from_path
from logger import logger

from .browser_history import BrowserHistoryHandler, BrowserHistory, \
    CommonBrowserHistoryItemGroupList
from .jisho.jisho_structs import JishoSearchHtmlParser, JishoSearchQuery
from .jisho.jisho_matches import SearchWordMatchesHandler, \
    DictionaryEntryList, SearchWordMatches, \
    DictionaryEntryMatch, DictionaryEntryMatchList
from .kotobank.kotobank_structs import KotobankWordHtmlParser, \
    KotobankResult, KotobankResultList

class ParserManagerMetaData(BasicLoadableObject['ParserManagerMetaData']):
    def __init__(
        self, browser_history_paths: List[str]=None, requires_jisho_grouping: bool=False,
        requires_jisho_matching: bool=False, requires_jisho_match_pruning: bool=False,
        requires_postmatching_redo: bool=False,
        requires_kotobank_combine: bool=False
    ):
        self.browser_history_paths = browser_history_paths if browser_history_paths is not None else []
        self.requires_jisho_grouping = requires_jisho_grouping
        self.requires_jisho_matching = requires_jisho_matching
        self.requires_jisho_match_pruning = requires_jisho_match_pruning
        self.requires_postmatching_redo = requires_postmatching_redo
        self.requires_kotobank_combine = requires_kotobank_combine

class KotobankParseConfig(BasicLoadableObject['KotobankParseConfig']):
    def __init__(
        self,
        priority_targets: List[str]=['search_word', 'repr_writing'],
        backup_targets: List[str]=['repr_reading', 'other_form_writing']
    ):
        super().__init__()
        for target in priority_targets:
            assert target in self.possible_targets()
        for target in backup_targets:
            assert target in self.possible_targets()
        self.priority_targets = priority_targets
        self.backup_targets = backup_targets

    @classmethod
    def possible_targets(cls) -> List[str]:
        return [
            'search_word',
            'repr_writing', 'repr_reading',
            'other_form_writing', 'other_form_reading'
        ]

class ParserManager(BasicLoadableObject['ParserManager']):
    def __init__(
        self, browser_history_dir: str, combined_history_path: str, jisho_grouped_history_path: str,
        jisho_parse_dump_dir: str, jisho_matches_path: str, jisho_pruned_entries_path: str,
        kotobank_parse_dump_dir: str,
        kotobank_temp_map_dir: str,
        combined_kotobank_dump_path: str,
        manager_save_path: str,
        kotobank_parse_config: KotobankParseConfig=None
    ):
        assert dir_exists(browser_history_dir), f"Couldn't find browser history folder: {browser_history_dir}"
        self.browser_history_dir = browser_history_dir
        self.combined_history_path = combined_history_path
        self.jisho_grouped_history_path = jisho_grouped_history_path
        self.jisho_parse_dump_dir = jisho_parse_dump_dir
        self.jisho_matches_path = jisho_matches_path
        self.jisho_pruned_entries_path = jisho_pruned_entries_path
        self.kotobank_parse_dump_dir = kotobank_parse_dump_dir
        self.kotobank_temp_map_dir = kotobank_temp_map_dir
        self.combined_kotobank_dump_path = combined_kotobank_dump_path
        self.manager_save_path = manager_save_path

        self.kotobank_parse_config = kotobank_parse_config if kotobank_parse_config is not None else KotobankParseConfig()

        self._metadata = ParserManagerMetaData()

    def to_dict(self) -> dict:
        return {
            'browser_history_dir': self.browser_history_dir,
            'combined_history_path': self.combined_history_path,
            'jisho_grouped_history_path': self.jisho_grouped_history_path,
            'jisho_parse_dump_dir': self.jisho_parse_dump_dir,
            'jisho_matches_path': self.jisho_matches_path,
            'jisho_pruned_entries_path': self.jisho_pruned_entries_path,
            'kotobank_parse_dump_dir': self.kotobank_parse_dump_dir,
            'kotobank_temp_map_dir': self.kotobank_temp_map_dir,
            'combined_kotobank_dump_path': self.combined_kotobank_dump_path,
            'manager_save_path': self.manager_save_path,
            'kotobank_parse_config': self.kotobank_parse_config.to_dict(),
            'metadata': self._metadata.to_dict()
        }
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> ParserManager:
        manager = ParserManager(
            browser_history_dir=item_dict['browser_history_dir'],
            combined_history_path=item_dict['combined_history_path'],
            jisho_grouped_history_path=item_dict['jisho_grouped_history_path'],
            jisho_parse_dump_dir=item_dict['jisho_parse_dump_dir'],
            jisho_matches_path=item_dict['jisho_matches_path'],
            jisho_pruned_entries_path=item_dict['jisho_pruned_entries_path'],
            kotobank_parse_dump_dir=item_dict['kotobank_parse_dump_dir'],
            kotobank_temp_map_dir=item_dict['kotobank_temp_map_dir'],
            combined_kotobank_dump_path=item_dict['combined_kotobank_dump_path'],
            kotobank_parse_config=item_dict['kotobank_parse_config'] if 'kotobank_parse_config' in item_dict else None,
            manager_save_path=item_dict['manager_save_path']
        )
        manager._metadata = ParserManagerMetaData.from_dict(item_dict['metadata'])
        return manager

    @property
    def browser_history_paths(self) -> List[str]:
        return self._metadata.browser_history_paths

    def combine_history(self, force: bool=False, verbose: bool=False, show_pbar: bool=True):
        browser_history_paths = recursively_get_all_matches_under_dirpath(
            dirpath=self.browser_history_dir,
            target_name='BrowserHistory.json',
            target_type='file'
        )
        browser_history_paths.sort()
        if self._metadata.browser_history_paths != browser_history_paths or not file_exists(self.combined_history_path) or force:
            handler = BrowserHistoryHandler.load_from_path_list(browser_history_paths)
            combined_history = BrowserHistory.combine(handler.browser_history_list, show_pbar=show_pbar)
            combined_history.browser_history_item_list.sort(attr_name='time_usec', reverse=False)
            combined_history.save_to_path(self.combined_history_path, overwrite=True)
            if verbose:
                logger.cyan('Saved Combined History')
            self._metadata.requires_jisho_grouping = True
            self._metadata.browser_history_paths = browser_history_paths
            self.save_to_path(self.manager_save_path, overwrite=True)
    
    def group_jisho_history(self, force: bool=False, verbose: bool=False):
        assert file_exists(self.combined_history_path), f"Couldn't find combined history at: {self.combined_history_path}"
        if self._metadata.requires_jisho_grouping or force or not file_exists(self.jisho_grouped_history_path):
            browser_history = BrowserHistory.load_from_path(self.combined_history_path)
            group_list = browser_history.browser_history_item_list.search_by_url_base_and_group_by_url('https://jisho.org/search/')
            group_list.sort(attr_name='item_count', reverse=True)
            group_list.save_to_path(self.jisho_grouped_history_path, overwrite=True)
            self._metadata.requires_jisho_grouping = False
            if verbose:
                logger.cyan('Saved Jisho Grouped History')
            self.save_to_path(self.manager_save_path, overwrite=True)
    
    def parse_jisho(self, force: bool=False, verbose: bool=False, show_pbar: bool=True):
        assert file_exists(self.jisho_grouped_history_path), f"Couldn't find Jisho Grouped History at: {self.jisho_grouped_history_path}"
        make_dir_if_not_exists(self.jisho_parse_dump_dir)
        existing_dump_paths = get_all_files_of_extension(self.jisho_parse_dump_dir, extension='json')
        dumped_search_word_list = [get_rootname_from_path(existing_dump_path) for existing_dump_path in existing_dump_paths]
        if force:
            dumped_search_word_list = []

        group_list = CommonBrowserHistoryItemGroupList.load_from_path(self.jisho_grouped_history_path)
        search_word_list = []
        url_list = []

        if verbose:
            logger.cyan(f'Parsing Jisho Data')
        pbar = tqdm(total=len(group_list), unit='word(s)') if show_pbar else None
        for group in group_list:
            encoded_search_word = group.url.replace('https://jisho.org/search/', '')
            decoded_search_word = urllib.parse.unquote(encoded_search_word)
            if pbar is not None:
                pbar.set_description(decoded_search_word)
            if decoded_search_word not in search_word_list:
                search_word_list.append(decoded_search_word)
                url_list.append(group.url)
            else:
                idx = search_word_list.index(decoded_search_word)
                existing_url = url_list[idx]
                raise Exception(
                    f"""
                    Found two unique urls for the same search word.
                    search_word: {decoded_search_word}
                    existing_url: {existing_url}
                    new_url: {group.url}
                    """
                )
            skip = False
            for invalid_str in ['#kanji', '#sentences', '#names']:
                if invalid_str in decoded_search_word:
                    skip = True
                    break
            if skip or decoded_search_word in dumped_search_word_list:
                if pbar is not None:
                    pbar.update()
                continue
            parser = JishoSearchHtmlParser(url=group.url)
            search_query = parser.parse(history_group_id=group.id)
            dump_path = f'{self.jisho_parse_dump_dir}/{decoded_search_word}.json'
            search_query.save_to_path(dump_path, overwrite=False)
            dumped_search_word_list.append(decoded_search_word)
            if not self._metadata.requires_jisho_matching:
                self._metadata.requires_jisho_matching = True
                self.save_to_path(self.manager_save_path, overwrite=True)
            if pbar is not None:
                pbar.update()
        if pbar is not None:
            pbar.close()
        if verbose:
            logger.cyan('Finished Parsing Jisho Data')
    
    def accumulate_jisho_matches(self, force: bool=False, verbose: bool=False, show_pbar: bool=True):
        assert dir_exists(self.jisho_parse_dump_dir), f"Couldn't find Jisho Parse Dump Directory: {self.jisho_parse_dump_dir}"
        if self._metadata.requires_jisho_matching or force or not file_exists(self.jisho_matches_path):
            dump_paths = get_all_files_of_extension(self.jisho_parse_dump_dir, extension='json')
            sw_matches_handler = SearchWordMatchesHandler()

            pbar = tqdm(total=len(dump_paths), unit='dump(s)') if show_pbar else None
            if pbar is not None:
                pbar.set_description('Searching For Matches')
            for dump_path in dump_paths:
                exact_matches = DictionaryEntryList()
                search_word = get_rootname_from_path(dump_path)
                query = JishoSearchQuery.load_from_path(dump_path)
                writing_match_idx_list = []
                reading_match_idx_list = []
                all_matches = query.exact_matches + query.nonexact_matches
                for i in range(len(all_matches)):
                    if all_matches[i].word_representation.writing == search_word:
                        writing_match_idx_list.append(i)
                    if all_matches[i].word_representation.reading == search_word:
                        reading_match_idx_list.append(i)
                if len(writing_match_idx_list) > 0:
                    for idx in writing_match_idx_list:
                        exact_matches.append(all_matches[idx])
                elif len(reading_match_idx_list) > 0:
                    for idx in reading_match_idx_list:
                        exact_matches.append(all_matches[idx])
                else:
                    pass
                sw_matches = SearchWordMatches(search_word=search_word, matches=exact_matches, history_group_id=query.history_group_id)
                sw_matches_handler.append(sw_matches)
                if pbar is not None:
                    pbar.update()
            if pbar is not None:
                pbar.close()
            sw_matches_handler.save_to_path(self.jisho_matches_path, overwrite=True)
            self._metadata.requires_postmatching_redo = True
            if verbose:
                logger.cyan(f'Finished Accumulating Jisho Matches')
            self._metadata.requires_jisho_matching = False
            if not self._metadata.requires_jisho_match_pruning:
                self._metadata.requires_jisho_match_pruning = True
            self.save_to_path(self.manager_save_path, overwrite=True)
    
    def prune_jisho_entry_matches(self, force: bool=False, verbose: bool=False, show_pbar: bool=True):
        if self._metadata.requires_jisho_match_pruning or not file_exists(self.jisho_pruned_entries_path) or force:
            assert file_exists(self.jisho_matches_path), f"Couldn't find Jisho matches path: {self.jisho_matches_path}"
            sw_matches_handler = SearchWordMatchesHandler.load_from_path(self.jisho_matches_path)
            entry_match_list = DictionaryEntryMatchList()
            if verbose:
                logger.cyan('Pruning Unique Jisho Entries')
            entry_match_list.add_pruned_matches(handler=sw_matches_handler.unique, mode=0, show_pbar=show_pbar, leave_pbar=True)
            if verbose:
                logger.cyan('Pruning Non-Unique Jisho Entries')
            entry_match_list.add_pruned_matches(handler=sw_matches_handler.non_unique, mode=1, show_pbar=show_pbar, leave_pbar=True)
            if verbose:
                logger.cyan('Finished Pruning Jisho Entries')
            entry_match_list.save_to_path(self.jisho_pruned_entries_path, overwrite=True)
            if self._metadata.requires_jisho_match_pruning:
                self._metadata.requires_jisho_match_pruning = False
                self.save_to_path(self.manager_save_path, overwrite=True)

    def parse_kotobank(self, force: bool=False, verbose: bool=False, show_pbar: bool=True):
        # TODO: Refactor this method so that it uses DictionaryEntryMatchList instead of SearchWordMatchesHandler.
        # TODO: Figure out a good way to keep track of indexes when parsing kotobank.
        #       KotobankResult needs to be indexed, and this index needs to be traceable to DictionaryEntryMatch.
        #       I guess the index can be based on len(searched_words), which is the same as the number of dump files in the
        #       dump directory.
        #       Since I need to allow for keyboard inturrupts when parsing, perhaps the best solution would be to
        #       create a separate dump directory for saving index mapping information, e.g. {'jisho': 24, 'kotobank': [17, 18, 19]}.
        #       But then what do about the filename of the index mapping file? Hmm...
        #       I don't know. Maybe I could name the index mapping file based on DictionaryEntryMatch's id.
        #       Since kotobank needs to parse search_word, writing, and other_forms, multiple kotobank dumps need to be linked
        #       to the same jisho dump.
        #       The ultimate goal will be to combine both jisho parsed data and kotobank parsed data into the same dump file.

        assert file_exists(self.jisho_matches_path), f"Couldn't find Jisho matches path: {self.jisho_matches_path}"
        search_word_matches_handler = SearchWordMatchesHandler.load_from_path(self.jisho_matches_path)
        make_dir_if_not_exists(self.kotobank_parse_dump_dir)
        searched_words = [get_rootname_from_path(path) for path in get_all_files_of_extension(self.kotobank_parse_dump_dir, extension='json')]
        if force:
            searched_words = []
            delete_all_files_in_dir(self.kotobank_parse_dump_dir, ask_permission=False)
            self._metadata.requires_postmatching_redo = False
            self.save_to_path(self.manager_save_path, overwrite=True)
        elif self._metadata.requires_postmatching_redo:
            matched_searched_words = search_word_matches_handler.search_words
            for i in list(range(len(searched_words)))[::-1]:
                if searched_words[i] not in matched_searched_words:
                    delete_file_if_exists(f'{self.kotobank_parse_dump_dir}/{searched_words[i]}.json')
                    del searched_words[i]
            self._metadata.requires_postmatching_redo = False
            self.save_to_path(self.manager_save_path, overwrite=True)

        pbar = tqdm(total=len(search_word_matches_handler), unit='searches') if show_pbar else None
        for search_word_matches in search_word_matches_handler:
            if pbar is not None:
                pbar.set_description(search_word_matches.search_word)
            if search_word_matches.search_word in searched_words:
                if pbar is not None:
                    pbar.update()
                continue
            parser = KotobankWordHtmlParser.from_search_word(search_word_matches.search_word)
            result = parser.parse()
            result.save_to_path(f'{self.kotobank_parse_dump_dir}/{search_word_matches.search_word}.json')
            searched_words.append(search_word_matches.search_word)
            if not self._metadata.requires_kotobank_combine:
                self._metadata.requires_kotobank_combine = True
                self.save_to_path(self.manager_save_path, overwrite=True)
                
            if pbar is not None:
                pbar.update()
        if pbar is not None:
            pbar.close()
        if verbose:
            logger.cyan(f'Finished Parsing Kotobank Data')

    def _process_kotobank_query(self, search_query: str) -> bool:
        dump_path = f'{self.kotobank_parse_dump_dir}/{search_query}.json'
        if not file_exists(dump_path):
            parser = KotobankWordHtmlParser.from_search_word(search_query)
            result = parser.parse()
            result.save_to_path(dump_path, overwrite=True)
        else:
            result = KotobankResult.load_from_path(dump_path)
        success = not result.is_empty
        return success

    def _process_kotobank_target(self, entry_match: DictionaryEntryMatch, target: str) -> List[str]:
        successful_search_queries = []
        if target == 'search_word':
            for search_word in entry_match.search_words:
                success = self._process_kotobank_query(search_word)
                if success:
                    successful_search_queries.append(search_word)
        elif target == 'repr_writing':
            search_query = entry_match.entry.word_representation.writing
            if search_query is not None:
                success = self._process_kotobank_query(search_query)
                if success:
                    successful_search_queries.append(search_query)
        elif target == 'repr_reading':
            search_query = entry_match.entry.word_representation.reading
            if search_query is not None:
                success = self._process_kotobank_query(search_query)
                if success:
                    successful_search_queries.append(search_query)
        elif target == 'other_form_writing':
            if entry_match.entry.meaning_section.other_forms is not None:
                for other_form in entry_match.entry.meaning_section.other_forms:
                    success = self._process_kotobank_query(other_form.writing)
                    if success:
                        successful_search_queries.append(other_form.writing)
        elif target == 'other_form_reading':
            if entry_match.entry.meaning_section.other_forms is not None:
                for other_form in entry_match.entry.meaning_section.other_forms:
                    success = self._process_kotobank_query(other_form.reading)
                    if success:
                        successful_search_queries.append(other_form.reading)
        else:
            raise ValueError(f'Invalid target: {target}')
        return list(set(successful_search_queries))

    def parse_kotobank0(self, force: bool=False, verbose: bool=False, show_pbar: bool=True):
        if force or self._metadata.requires_postmatching_redo:
            if force:
                delete_all_files_in_dir(self.kotobank_parse_dump_dir)
                delete_all_files_in_dir(self.kotobank_temp_map_dir)
            
            assert file_exists(self.jisho_pruned_entries_path), f"Couldn't find pruned Jisho matches path: {self.jisho_pruned_entries_path}"
            entry_match_list = DictionaryEntryMatchList.load_from_path(self.jisho_pruned_entries_path)

            make_dir_if_not_exists(self.kotobank_temp_map_dir)
            finished_entry_ids = [
                int(get_rootname_from_path(path))
                for path in get_all_files_of_extension(self.kotobank_temp_map_dir, extension='json')
            ]

            pbar = tqdm(total=len(entry_match_list), unit='entries', leave=True) if show_pbar else None
            if pbar is not None:
                pbar.set_description('Parsing Kotobank Results From Jisho Entries')
            for entry_match in entry_match_list:
                if entry_match.id in finished_entry_ids:
                    if pbar is not None:
                        pbar.update()
                    continue

                priority_target_found = False
                backup_target_found = False
                successful_search_queries = []
                for target in self.kotobank_parse_config.priority_targets:
                    successful_search_queries0 = self._process_kotobank_target(entry_match=entry_match, target=target)
                    if len(successful_search_queries0) > 0:
                        successful_search_queries.extend(successful_search_queries0)
                        if not priority_target_found:
                            priority_target_found = True

                if not priority_target_found:
                    for target in self.kotobank_parse_config.backup_targets:
                        successful_search_queries0 = self._process_kotobank_target(entry_match=entry_match, target=target)
                        if len(successful_search_queries0) > 0:
                            successful_search_queries.extend(successful_search_queries0)
                            if not backup_target_found:
                                backup_target_found = True
                                break
                        
                successful_search_queries = list(set(successful_search_queries))
                nonempty_kotobank_result_found = priority_target_found or backup_target_found
                json.dump(
                    {'successful_search_queries': successful_search_queries},
                    open(f'{self.kotobank_temp_map_dir}/{entry_match.id}.json', 'w'),
                    ensure_ascii=False
                )
                if pbar is not None:
                    pbar.update()
            if pbar is not None:
                pbar.close()
            
            pbar = tqdm(total=len(entry_match_list), unit='entries', leave=True) if show_pbar else None
            if pbar is not None:
                pbar.set_description('Linking Kotobank Results To Jisho Entries')
            for entry_match in entry_match_list:
                temp_dict = json.load(open(f'{self.kotobank_temp_map_dir}/{entry_match.id}.json'), 'r')
                entry_match.linked_kotobank_queries = temp_dict['successful_search_queries']
                if pbar is not None:
                    pbar.update()
            entry_match_list.save_to_path(self.jisho_pruned_entries_path, overwrite=True)
            delete_dir_if_exists(self.kotobank_temp_map_dir)
            if pbar is not None:
                pbar.close()
            self._metadata.requires_postmatching_redo = False
            self._metadata.requires_kotobank_combine = True
            self.save_to_path(self.manager_save_path, overwrite=True)

    def combine_kotobank_results(self, force: bool=False, verbose: bool=False, show_pbar: bool=True):
        if self._metadata.requires_kotobank_combine or force or not file_exists(self.combined_kotobank_dump_path):
            kotobank_result_list = KotobankResultList.load_from_dir(self.kotobank_parse_dump_dir, show_pbar=show_pbar)
            kotobank_result_list.save_to_path(self.combined_kotobank_dump_path, overwrite=True)
            self._metadata.requires_kotobank_combine = False
            self.save_to_path(self.manager_save_path, overwrite=True)
            if verbose:
                logger.cyan(f'Finished Combining Kotobank Data')

    def run(
        self,
        force_combine_history: bool=False, ignore_combine_history: bool=False,
        force_group_jisho_history: bool=False, ignore_group_jisho_history: bool=False,
        force_parse_jisho: bool=False, ignore_parse_jisho: bool=False,
        force_accumulate_jisho_matches: bool=False, ignore_accumulate_jisho_matches: bool=False,
        force_prune_jisho_entry_matches: bool=False, ignore_prune_jisho_entry_matches: bool=False,
        force_parse_kotobank: bool=False, ignore_parse_kotobank: bool=False,
        force_combine_kotobank: bool=False, ignore_combine_kotobank: bool=False,
        verbose: bool=False, show_pbar: bool=True
    ):
        if not ignore_combine_history or force_combine_history:
            self.combine_history(force=force_combine_history, verbose=verbose, show_pbar=show_pbar)
        if not ignore_group_jisho_history or force_group_jisho_history:
            self.group_jisho_history(force=force_group_jisho_history, verbose=verbose)
        if not ignore_parse_jisho or force_parse_jisho:
            self.parse_jisho(force=force_parse_jisho, verbose=verbose, show_pbar=show_pbar)
        if not ignore_accumulate_jisho_matches or force_accumulate_jisho_matches:
            self.accumulate_jisho_matches(force=force_accumulate_jisho_matches, verbose=verbose, show_pbar=show_pbar)
        if not ignore_prune_jisho_entry_matches or force_prune_jisho_entry_matches:
            self.prune_jisho_entry_matches(force=force_prune_jisho_entry_matches, verbose=verbose, show_pbar=show_pbar)
        if not ignore_parse_kotobank or force_parse_kotobank:
            self.parse_kotobank0(force=force_parse_kotobank, verbose=verbose, show_pbar=show_pbar)
        if not ignore_combine_kotobank or force_combine_kotobank:
            self.combine_kotobank_results(force=force_combine_kotobank, verbose=verbose, show_pbar=show_pbar)