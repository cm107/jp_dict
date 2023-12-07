from __future__ import annotations
import json
from typing import Callable
import glob
import os
import urllib.parse
from tqdm import tqdm

class HistoryUrl:
    def __init__(self, url: str, utctimes: list[float]):
        self.url = url
        self.utctimes = utctimes

    def to_dict(self) -> dict:
        return self.__dict__
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> HistoryUrl:
        return HistoryUrl(*item_dict)

    @staticmethod
    def save(obj: HistoryUrl | list[HistoryUrl], path: str):
        if type(obj) is HistoryUrl:
            json.dump(obj.to_dict(), open(path, 'w'), ensure_ascii=False)
        elif type(obj) is list:
            json.dump([_obj.to_dict() for _obj in obj], open(path, 'w'), ensure_ascii=False)
        else:
            raise TypeError
    
    @staticmethod
    def load(path: str) -> HistoryUrl | list[HistoryUrl]:
        if not os.path.isfile(path):
            raise FileNotFoundError
        data = json.load(open(path, 'r'))
        if type(data) is list:
            return [HistoryUrl.from_dict(_data) for _data in data]
        elif type(data) is dict:
            return HistoryUrl.from_dict(data)
        else:
            raise TypeError

class HistoryUrlSection:
    def __init__(
        self, condition: Callable[[str], bool],
        entries: list[HistoryUrl]=None
    ):
        self.condition = condition
        self.entries: list[HistoryUrl] = entries \
            if entries is not None else []

    def process(self, url: str, utctime: float) -> bool:
        if self.condition(url):
            found = False
            for entry in self.entries:
                if entry.url == url:
                    if utctime not in entry.utctimes:
                        entry.utctimes.append(utctime)
                    found = True
                    break
            if not found:
                self.entries.append(HistoryUrl(url, [utctime]))
            return True
        return False

class HistoryUrlSectionGroup(dict[str, HistoryUrlSection]):
    def __init__(
        self,
        condition: Callable[[str], bool],
        *args,
        newSectionCallback: Callable[[HistoryUrlSectionGroup, str, float], bool]=None,
        **kwargs
    ):
        self.condition = condition
        self.newSectionCallback = newSectionCallback
        super().__init__(*args, **kwargs)
    
    def process(self, url: str, utctime: float) -> bool:
        if self.condition(url):
            for sectionName, section in self.items():
                # isMatch = section.process(url, utctime)
                isMatch = section.process(url, utctime)
                if isMatch:
                    # print(f"Group: {sectionName} match -> {url}")
                    return True
            if self.newSectionCallback is not None:
                return self.newSectionCallback(self, url, utctime)
        return False

class JishoSearchUrlUtil:
    """
    Utility for working with URLs that begin with:
        https://jisho.org/search/
    """
    @staticmethod
    def is_valid(url: str) -> bool:
        return url.startswith('https://jisho.org/search/')
    
    @staticmethod
    def get_search_word(url: str) -> str:
        return url.replace('https://jisho.org/search/', '')

    @staticmethod
    def get_search_word_character_count(url: str) -> int:
        return len(JishoSearchUrlUtil.get_search_word(url))

    @staticmethod
    def get_history_url_section_group() -> HistoryUrlSectionGroup:
        # def get_key(url: str):
        #     searchWord = JishoSearchUrlUtil.get_search_word(url)
        #     charCount = len(searchWord)
        #     return charCount

        def get_key(url: str):
            searchWord = JishoSearchUrlUtil.get_search_word(url)
            startChar = searchWord[0]
            return startChar.encode('utf-8')[0]

        # def get_key(url: str):
        #     searchWord = JishoSearchUrlUtil.get_search_word(url)
        #     startChar = searchWord[0]
        #     return tuple(startChar.encode('utf-8')[:2])

        def update(group: HistoryUrlSectionGroup, url: str, utctime: float):
            key = get_key(url)
            group[f'searchWord-{key}'] = HistoryUrlSection(
                lambda _url: get_key(_url) == key,
                entries=[HistoryUrl(url, [utctime])]
            )

        return HistoryUrlSectionGroup(
            condition=JishoSearchUrlUtil.is_valid,
            newSectionCallback=update
        )

Section = HistoryUrlSection | HistoryUrlSectionGroup

class HistoryUrlManager:
    def __init__(self):
        self.sections: dict[str, Section] = {
            "jisho": JishoSearchUrlUtil.get_history_url_section_group(),
            "other": HistoryUrlSection(lambda url: False)
        }
    
    def process(self, url: str, utctime: float) -> bool:
        for sectionName, section in self.sections.items():
            isMatch = section.process(url, utctime)
            if isMatch:
                # print(f"Manager: {sectionName} match -> {url}")
                return True
        return False

    @staticmethod
    def get_all_files(dirPath: str, is_relevant_filename: Callable[[str], bool], recursive: bool=True) -> list[str]:
        if not os.path.isdir(dirPath):
            raise FileNotFoundError
        results: list[str] = []
        for path in glob.glob(f"{dirPath}/*"):
            if os.path.isfile(path):
                filename = os.path.basename(path)
                if is_relevant_filename(filename):
                    results.append(path)
            elif os.path.isdir(path):
                if recursive:
                    results.extend(HistoryUrlManager.get_all_files(path, is_relevant_filename, recursive))
        return results

    @staticmethod
    def get_all_history_paths(browserHistoryDir: str) -> list[str]:
        return HistoryUrlManager.get_all_files(
            dirPath=browserHistoryDir,
            is_relevant_filename=lambda filename: filename in ['BrowserHistory.json', 'History.json'],
            recursive=True
        )

    @property
    def entries(self) -> list[HistoryUrl]:
        entries: list[HistoryUrl] = []
        for sectionName, section in self.sections.items():
            if type(section) is HistoryUrlSection:
                entries.extend(section.entries)
            elif type(section) is HistoryUrlSectionGroup:
                for _sectionName, _section in section.items():
                    entries.extend(_section.entries)
            else:
                raise TypeError
        entries.sort(key=lambda obj: min(obj.utctimes))
        return entries

    @staticmethod
    def from_history_paths(historyPaths: list[str]) -> HistoryUrlManager:
        manager = HistoryUrlManager()
        for path in tqdm(historyPaths):
            data = json.load(open(path, 'r'))
            for i, entry in enumerate(data['Browser History']):
                title: str = entry['title']
                url: str = entry['url']
                time_usec = entry['time_usec']

                url = urllib.parse.unquote(url)
                manager.process(url, time_usec)
        return manager

    @staticmethod
    def from_browser_history_dir(browserHistoryDir: str) -> HistoryUrlManager:
        historyPaths = HistoryUrlManager.get_all_history_paths(browserHistoryDir)
        historyPaths.sort()
        return HistoryUrlManager.from_history_paths(historyPaths)

    @staticmethod
    def debug():
        manager = HistoryUrlManager.from_browser_history_dir("/media/clayton/Data/study/jp_dict_data/browser_history")

        for sectionName, section in manager.sections.items():
            if type(section) is HistoryUrlSection:
                print(f"{sectionName}: {len(section.entries)}")
            elif type(section) is HistoryUrlSectionGroup:
                for _sectionName, _section in section.items():
                    print(f"{sectionName}.{_sectionName}: {len(_section.entries)}")
            else:
                raise TypeError
        
        entries = manager.entries
        print(f"{len(entries)=}")

        dumpPath = 'history_dump.json'
        HistoryUrl.save(entries, dumpPath)
        assert len(HistoryUrl.load(dumpPath)) == len(entries)

