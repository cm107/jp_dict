from __future__ import annotations
from typing import List
from common_utils.base.basic import BasicLoadableObject, \
    BasicLoadableHandler, BasicHandler

class WritingKanjiInfo(BasicLoadableObject['WritingKanjiInfo']):
    def __init__(
        self, kanji: str,
        hit_count: int, used_in: List[str],
        earliest_time_usec: int, earliest_pos_idx: int # Used as a unique identifier
    ):
        super().__init__()
        self.kanji = kanji
        self.hit_count = hit_count
        self.used_in = used_in
        self.earliest_time_usec = earliest_time_usec
        self.earliest_pos_idx = earliest_pos_idx

class WritingKanjiInfoList(
    BasicLoadableHandler['WritingKanjiInfoList', 'WritingKanjiInfo'],
    BasicHandler['WritingKanjiInfoList', 'WritingKanjiInfo']
):
    def __init__(self, info_list: List[WritingKanjiInfo]=None):
        super().__init__(obj_type=WritingKanjiInfo, obj_list=info_list)
        self.info_list = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> WritingKanjiInfoList:
        return WritingKanjiInfoList([WritingKanjiInfo.from_dict(item_dict) for item_dict in dict_list])