from __future__ import annotations
from typing import List
from common_utils.base.basic import BasicLoadableObject, \
    BasicHandler, BasicLoadableHandler

class CardTemplate(BasicLoadableObject['CardTemplate']):
    def __init__(self, name: str, front: str, back: str):
        super().__init__()
        self.name = name
        self.front = front
        self.back = back
    
    def to_dict(self) -> dict:
        return {
            'Name': self.name,
            'Front': self.front,
            'Back': self.back
        }

    @classmethod
    def from_dict(cls, item_dict: dict) -> CardTemplate:
        return CardTemplate(
            name=item_dict['Name'],
            front=item_dict['Front'],
            back=item_dict['Back']
        )

    @staticmethod
    def _find_fields(s: str, left_identifier: str='{{', right_identifier: str='}}') -> List[str]:
        left_split = s.split(left_identifier)
        left_split = [part for part in left_split if right_identifier in part]
        right_split = [part.split(right_identifier)[0] for part in left_split]
        return right_split

    @property
    def front_fields(self) -> List[str]:
        return self._find_fields(s=self.front, left_identifier='{{', right_identifier='}}')

    @property
    def back_fields(self) -> List[str]:
        return self._find_fields(s=self.back, left_identifier='{{', right_identifier='}}')

    @property
    def fields(self) -> List[str]:
        return list(set(self.front_fields + self.back_fields))


class CardTemplateList(
    BasicLoadableHandler['CardTemplateList', 'CardTemplate'],
    BasicHandler['CardTemplateList', 'CardTemplate']
):
    def __init__(self, templates: List[CardTemplate]=None):
        super().__init__(obj_type=CardTemplate, obj_list=templates)
        self.templates = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> CardTemplateList:
        return CardTemplateList([CardTemplate.from_dict(item_dict) for item_dict in dict_list])
    
    def get_update_format_dict(self) -> dict:
        result_dict = {}
        for template in self:
            result_dict[template.name] = {
                'Front': template.front,
                'Back': template.back
            }
        return result_dict

    @property
    def fields(self) -> List[str]:
        fields = []
        for template in self:
            fields.extend(template.fields)
        return list(set(fields))