from __future__ import annotations
from dataclasses import dataclass
import glob
import json
import os

from tqdm import tqdm

from .error import CLIError
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from .meta import MetaDirectory
from .serializable_obj import SerializableObject
from .meta_module import MetaDirectoryModule

@dataclass
class HistoryEntry(SerializableObject):
    favicon_url: str = None
    page_transition: str = None
    title: str = None
    url: str = None
    client_id: str = None
    time_usec: int = None

class HistoryModule(MetaDirectoryModule):
    def __init__(self, meta: MetaDirectory):
        super().__init__(meta)
        self.srcDir: str = None
    
    def convert_to_dict(self, item_dict: dict):
        pass

    @classmethod
    def extract_prepostinit(cls, item_dict: dict) -> tuple[dict, dict]:
        return {}, item_dict

    def set_loadHistoryDir_cmd(self, value: str):
        if not os.path.isdir(value):
            raise CLIError(f"History directory not found: {value}")

        self.srcDir = value
        self._meta.save()
    
    def get_loadHistoryDir_cmd(self):
        print(self.srcDir)

    @staticmethod
    def _get_history_paths(dirPath: str) -> list[str]:
        result: list[str] = []
        for path in glob.glob(f"{dirPath}/*"):
            if os.path.isfile(path):
                filename = os.path.basename(path)
                if filename in ['BrowserHistory.json', 'History.json']:
                    result.append(path)
            elif os.path.isdir(path):
                result.extend(HistoryModule._get_history_paths(path))
            else:
                pass
        return result

    def get_history_paths(self) -> list[str]:
        if self.srcDir is None:
            raise CLIError("Need to set source directory first.")
        return self._get_history_paths(self.srcDir)
    
    def list_history_paths_cmd(self):
        for path in self.get_history_paths():
            print(path)
    
    def count_history_paths_cmd(self):
        print(len(self.get_history_paths()))
    
    @staticmethod
    def calc_combined_history(
        paths: list[str], showPbar: bool=False
    ) -> list[dict]:
        combinedTimeEntryMap: dict[int, dict] = dict()
        if showPbar:
            paths = tqdm(paths, desc='Combining Histories', leave=True)
        for path in paths:
            data = json.load(open(path, 'r'))
            entries: list[dict] = data['Browser History'][::-1]
            if not showPbar:
                while len(entries) > 0:
                    entry = entries.pop()
                    combinedTimeEntryMap[entry['time_usec']] = entry
            else:
                pbar = tqdm(total=len(entries), leave=False)
                while len(entries) > 0:
                    entry = entries.pop()
                    combinedTimeEntryMap[entry['time_usec']] = entry
                    pbar.update()
                pbar.close()
        combinedEntries: list[dict] = list(combinedTimeEntryMap.values())
        combinedEntries.sort(key=lambda obj: obj['time_usec'])
        return combinedEntries

    def combine_history(self, savePath: str):
        combinedEntries = HistoryModule.calc_combined_history(
            paths=self.get_history_paths(),
            showPbar=True
        )
        json.dump(
            combinedEntries,
            open(savePath, 'w'),
            ensure_ascii=False,
            indent=2
        )

    def combine_history_cmd(self):
        self.combine_history(self._meta.combinedHistoryPath)
        print("Combined browser history")

    def count_entries_cmd(self, getFn: str | None=None):
        if not os.path.isfile(self._meta.combinedHistoryPath):
            raise CLIError("Need to combine histories first.")
        entries = json.load(open(self._meta.combinedHistoryPath, 'r'))
        if getFn is not None:
            if type(getFn) is not list:
                getFn = [getFn]
            for _getFn in getFn:
                _getFn: Callable[[dict], bool] = eval(_getFn)
                entries = [
                    entry for entry in entries
                    if _getFn(entry)
                ]
        print(len(entries))

    def print_entries_cmd(
        self,
        valueFn: str | list[str] | None=None,
        getFn: str | None=None,
        sortFn: str | None=None, reverse: bool=False,
        head: int | None=None,
        tail: int | None=None,
    ):
        if not os.path.isfile(self._meta.combinedHistoryPath):
            raise CLIError("Need to combine histories first.")
        entries = json.load(open(self._meta.combinedHistoryPath, 'r'))
        if getFn is not None:
            if type(getFn) is not list:
                getFn = [getFn]
            for _getFn in getFn:
                if _getFn.startswith('lambda value:'):
                    _valueFn = eval(valueFn)
                    _getFn0 = eval(_getFn)
                    _getFn: Callable[[dict], bool] = lambda entry: _getFn0(_valueFn(entry))
                else:
                    _getFn: Callable[[dict], bool] = eval(_getFn)
                entries = [
                    entry for entry in entries
                    if _getFn(entry)
                ]
        if sortFn is not None:
            sortFn = eval(sortFn)
            entries.sort(key=sortFn, reverse=reverse)
        if valueFn is not None:
            valueFn = eval(valueFn)
        else:
            valueFn = lambda entry: entry
        if head is not None:
            entries = entries[:head]
        if tail is not None:
            entries = entries[-tail:]
        for entry in entries:
            print(valueFn(entry))
