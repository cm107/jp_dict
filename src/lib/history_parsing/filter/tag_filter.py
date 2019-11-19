from logger import logger

class TagFilter:
    @classmethod
    def check_invalid_target(self, category: str, target: str):
        if category == 'bool':
            if target not in ['true', 'false', 'none']:
                logger.error(f"Invalid target for category {category}: {target}")
                raise Exception
        elif category == 'char':
            if target not in ['all', 'partial', 'none']:
                logger.error(f"Invalid target for category {category}: {target}")
                raise Exception

    @classmethod
    def filter_by_wildcard_tag(self, tagged_cache_list: list, target: str) -> list:
        self.check_invalid_target('bool', target)
        result = []
        for tagged_cache in tagged_cache_list:
            if tagged_cache.contains_wildcard is None and target == 'none':
                result.append(tagged_cache)
            elif tagged_cache.contains_wildcard and target == 'true':
                result.append(tagged_cache)
            elif not tagged_cache.contains_wildcard and target == 'false':
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_eng_chars_tag(self, tagged_cache_list: list, target: str) -> list:
        self.check_invalid_target('bool', target)
        result = []
        for tagged_cache in tagged_cache_list:
            if tagged_cache.contains_eng_chars is None and target == 'none':
                result.append(tagged_cache)
            elif tagged_cache.contains_eng_chars and target == 'true':
                result.append(tagged_cache)
            elif not tagged_cache.contains_eng_chars and target == 'false':
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_typo_chars_tag(self, tagged_cache_list: list, target: str) -> list:
        self.check_invalid_target('bool', target)
        result = []
        for tagged_cache in tagged_cache_list:
            if tagged_cache.contains_typo_chars is None and target == 'none':
                result.append(tagged_cache)
            elif tagged_cache.contains_typo_chars and target == 'true':
                result.append(tagged_cache)
            elif not tagged_cache.contains_typo_chars and target == 'false':
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_garbage_chars_tag_group(self, tagged_cache_list: list, target: str) -> list:
        self.check_invalid_target('bool', target)
        result = []
        for tagged_cache in tagged_cache_list:
            if tagged_cache.is_not_processed_for_japanese_chars_yet() is None and target == 'none':
                result.append(tagged_cache)
            elif tagged_cache.is_garbage_word() and target == 'true':
                result.append(tagged_cache)
            elif not tagged_cache.is_garbage_word() and target == 'false':
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_hiragana_tag(self, tagged_cache_list: list, target: str) -> list:
        self.check_invalid_target('char', target)
        result = []
        for tagged_cache in tagged_cache_list:
            if tagged_cache.is_not_processed_for_japanese_chars_yet():
                logger.error(f"tagged_cache not labeled:\n{tagged_cache}")
                raise Exception
            if tagged_cache.hiragana_tag == target:
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_katakana_tag(self, tagged_cache_list: list, target: str) -> list:
        self.check_invalid_target('char', target)
        result = []
        for tagged_cache in tagged_cache_list:
            if tagged_cache.is_not_processed_for_japanese_chars_yet():
                logger.error(f"tagged_cache not labeled:\n{tagged_cache}")
                raise Exception
            if tagged_cache.katakana_tag == target:
                result.append(tagged_cache)
        return result

    @classmethod
    def filter_by_kanji_tag(self, tagged_cache_list: list, target: str) -> list:
        self.check_invalid_target('char', target)
        result = []
        for tagged_cache in tagged_cache_list:
            if tagged_cache.is_not_processed_for_japanese_chars_yet():
                logger.error(f"tagged_cache not labeled:\n{tagged_cache}")
                raise Exception
            if tagged_cache.kanji_tag == target:
                result.append(tagged_cache)
        return result