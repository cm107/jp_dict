from __future__ import annotations
import operator
from logger import logger

class Cache:
    def __init__(self, item):
        self.item = item
        self.hit_count = 0
        self.times_usec = []

    def __str__(self):
        print_str = f'item: {self.item}'
        print_str += f'\nhit_count: {self.hit_count}'
        return print_str

    def __repr__(self):
        return self.__str__()

    def __key(self) -> tuple:
        return tuple([self.__class__] + list(self.__dict__.values()))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__key() == other.__key()
        return NotImplemented

    @classmethod
    def buffer(self, cache: Cache) -> Cache:
        return cache

    def copy(self) -> Cache:
        cache = Cache(item=self.item)
        cache.hit_count = self.hit_count
        cache.times_usec = self.times_usec
        return cache

    def hit(self, time_usec: int):
        self.hit_count += 1
        self.times_usec.append(time_usec)

class CacheHandler:
    def __init__(self):
        self.cache_list = []

    def add_new(self, item, time_usec: int):
        new_cache = Cache(item=item)
        new_cache.hit(time_usec=time_usec)
        self.cache_list.append(new_cache)

    def search_item(self, item, time_usec: int, item_key: str=None) -> (bool, int):
        found = False
        duplicate = False
        found_index = None
        for i, cache in zip(range(len(self.cache_list)), self.cache_list):
            if item_key is None:
                logger.purple(f"cache.item: {cache.item}, item: {item}")
                if cache.item == item:
                    found = True
                    found_index = i
                    duplicate = True if time_usec in cache.times_usec else False
                    break
            else:
                if cache.item[item_key] == item[item_key]:
                    found = True
                    found_index = i
                    duplicate = True if time_usec in cache.times_usec else False
                    break
        return found, found_index, duplicate

    def sort(self):
        self.cache_list.sort(key=operator.attrgetter('hit_count'), reverse=True)

    def process(self, item, time_usec: int, item_key: str=None):
        found, found_index, duplicate = self.search_item(item=item, time_usec=time_usec, item_key=item_key)
        if not found:
            self.add_new(item, time_usec)
        elif not duplicate:
            self.cache_list[found_index].hit(time_usec)
            self.sort()
        return not found

    def print_cache_summary(self):
        print("Cache Hits:")
        for cache in self.cache_list:
            print(f"{cache.hit_count}: {cache.item}")

class SearchWordCacheHandler(CacheHandler):
    def __init__(self):
        super().__init__()

    def check_url(self, url: str, time_usec: int) -> (bool, bool):
        found, found_index, duplicate = self.search_item(item={'url': url, 'search_word': None}, time_usec=time_usec, item_key='url')
        if found and not duplicate:
            self.cache_list[found_index].hit(time_usec=time_usec)
            self.sort()
        return found, duplicate

class SoupCacheHandler(CacheHandler):
    def __init__(self):
        super().__init__()

    def check_url(self, url: str, time_usec: int) -> (bool, bool):
        found, found_index, duplicate = self.search_item(item={'url': url, 'soup_save_item': None}, time_usec=time_usec, item_key='url')
        if found and not duplicate:
            self.cache_list[found_index].hit(time_usec=time_usec)
            self.sort()
        return found, duplicate

class CharCacheHandler(CacheHandler):
    def __init__(self):
        super().__init__()
        self.count = 0

    def add_new(self, char: str):
        """
        CacheHandler method overridden.
        """
        self.count += 1
        new_cache = Cache(item={'char': char})
        new_cache.hit(time_usec=self.count)
        self.cache_list.append(new_cache)

    def check_char(self, char: str) -> (bool, bool):
        self.count += 1
        found, found_index, duplicate = self.search_item(item={'char': char}, time_usec=self.count, item_key='char')
        if found and not duplicate:
            self.cache_list[found_index].hit(time_usec=self.count)
            self.sort()
        return found, duplicate