import operator
from ...submodules.logger.logger_handler import logger

class Cache:
    def __init__(self, item):
        self.item = item
        self.hit_count = 0

    def hit(self):
        self.hit_count += 1

class CacheHandler:
    def __init__(self):
        self.cache_list = []

    def add_new(self, item):
        new_cache = Cache(item)
        new_cache.hit()
        self.cache_list.append(new_cache)

    def search_item(self, item, item_key: str=None) -> (bool, int):
        found = False
        found_index = None
        for i, cache in zip(range(len(self.cache_list)), self.cache_list):
            if item_key is None:
                if cache.item == item:
                    found = True
                    found_index = i
                    break
            else:
                # logger.red(f"type(cache.item)={type(cache.item)}")
                if cache.item[item_key] == item[item_key]:
                    found = True
                    found_index = i
                    break
        return found, found_index

    def sort(self):
        self.cache_list.sort(key=operator.attrgetter('hit_count'), reverse=True)

    def process(self, item, item_key: str=None):
        found, found_index = self.search_item(item=item, item_key=item_key)
        if found:
            self.cache_list[found_index].hit()
            self.sort()
        else:
            self.add_new(item)
        return not found

    def print_cache_summary(self):
        logger.cyan("Cache Hits:")
        for cache in self.cache_list:
            logger.blue(f"{cache.hit_count}: {cache.item}")