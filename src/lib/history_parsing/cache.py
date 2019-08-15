import operator
from ...submodules.logger.logger_handler import logger

class Cache:
    def __init__(self, item):
        self.item = item
        self.hit_count = 0
        self.times_usec = []

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

    def check_url(self, url: str, time_usec: int) -> bool:
        found, found_index, duplicate = self.search_item(item={'url': url, 'search_word': None}, time_usec=time_usec, item_key='url')
        if found and not duplicate:
            self.cache_list[found_index].hit(time_usec=time_usec)
            self.sort()
        return found, duplicate

    def search_item(self, item, time_usec: int, item_key: str=None) -> (bool, int):
        found = False
        duplicate = False
        found_index = None
        for i, cache in zip(range(len(self.cache_list)), self.cache_list):
            if item_key is None:
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
        # logger.cyan("Cache Hits:")
        print("Cache Hits:")
        for cache in self.cache_list:
            # logger.blue(f"{cache.hit_count}: {cache.item}")
            print(f"{cache.hit_count}: {cache.item}")