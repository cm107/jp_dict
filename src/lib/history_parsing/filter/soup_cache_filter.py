from logger import logger
from ..cache import Cache
from ..soup_saver import SoupSaveItem
from .core import TaggedCache, TaggedCacheHandler, CacheFilter

class TaggedSoupCache(TaggedCache):
    def __init__(self, soup_cache: Cache):
        super().__init__(cache=soup_cache)
        
    def get_search_word_and_url(self, cache: Cache) -> (str, str):
        if 'url' not in cache.item:
            logger.error(f"'url' not found in cache.item")
            logger.error(f"This is not a soup cache.")
            raise Exception
        if 'soup_save_item' not in cache.item:
            logger.error(f"'soup_save_item' not found in cache.item")
            logger.error(f"This is not a soup cache.")
            raise Exception
        url = cache.item['url']
        soup_save_item = cache.item['soup_save_item']
        soup_save_item = SoupSaveItem.buffer(soup_save_item)
        if not soup_save_item.save_exists():
            logger.error(f"Couldn't find soup save: {soup_save_item.save_path}")
            raise Exception
        soup = soup_save_item.load()
        search_word = soup.title.text.split('-')[0][:-1]
        return search_word, url

class TaggedSoupCacheHandler(TaggedCacheHandler):
    def __init__(self):
        super().__init__()

    def add(self, tagged_cache: TaggedSoupCache):
        self.tagged_cache_list.append(tagged_cache)

    def add_from_cache(self, cache: Cache):
        self.add(TaggedSoupCache(cache))

class SoupCacheFilter(CacheFilter):
    def __init__(self, cache_list: list):
        super().__init__(cache_list=cache_list)

    def get_tagged_cache_handler(self) -> TaggedSoupCacheHandler:
        return TaggedSoupCacheHandler()