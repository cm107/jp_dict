from __future__ import annotations
from .supplemental_info import SupplementalInfo
from ..base import BaseParsedObject

class DefinitionSection(BaseParsedObject):
    def __init__(self, section_number: int, definition_text: str, supplemental_info: SupplementalInfo=None):
        super().__init__()
        self.section_number = section_number
        self.definition_text = definition_text
        self.supplemental_info = supplemental_info

    def __str__(self):
        if self.supplemental_info is not None:
            return "{}. {}  {}".format(self.section_number, self.definition_text, self.supplemental_info)
        else:
            return "{}. {}".format(self.section_number, self.definition_text)

    @classmethod
    def buffer(self, definition_section: DefinitionSection) -> DefinitionSection:
        return definition_section

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [
            DefinitionSection(
                section_number=i, definition_text=f'Definition Text {i}', supplemental_info=supplemental_info
            ) \
                for i, supplemental_info in zip(range(num_samples), SupplementalInfo.sample(num_samples))
        ]

class DefinitionGroup(BaseParsedObject):
    def __init__(self, group_usage: str, definition_sections: list):
        super().__init__()
        self.group_usage = group_usage
        self.definition_sections = definition_sections

    def __str__(self):
        print_str = '{}\n'.format(self.group_usage)
        for definition_section in self.definition_sections:
            print_str += "\t{}\n".format(definition_section)
        return print_str

    @classmethod
    def buffer(self, definition_group: DefinitionGroup) -> DefinitionGroup:
        return definition_group

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        definition_section_list_list = []
        for i in range(num_samples):
            definition_section_list = []
            for j, supplemental_info in zip(range(3), SupplementalInfo.sample(3)):
                definition_section_list.append(
                    DefinitionSection(
                        section_number=j, definition_text=f'Definition Text {i}_{j}',
                        supplemental_info=supplemental_info
                    )
                )
            definition_section_list_list.append(definition_section_list)
        return [
            DefinitionGroup(group_usage=f"Group Usage {i}", definition_sections=definition_section_list) \
                for i, definition_section_list in zip(range(num_samples), definition_section_list_list)
        ]

class Definitions(BaseParsedObject):
    def __init__(self, def_groups: list):
        super().__init__()
        self.def_groups = def_groups

    def __str__(self):
        print_str = ''
        for def_group in self.def_groups:
            print_str += def_group.__str__()
        return print_str

    @classmethod
    def buffer(self, definitions: Definitions) -> Definitions:
        return definitions

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        def_group_list_list = []
        for i in range(num_samples):
            def_group_list = DefinitionGroup.sample(3)
            new_def_group_list = []
            for j, def_group in enumerate(def_group_list):
                def_group = DefinitionGroup.buffer(def_group)
                new_def_group = DefinitionGroup(
                    group_usage=f'{def_group.group_usage}_{i}',
                    definition_sections=def_group.definition_sections
                )
                new_def_group_list.append(new_def_group)
            def_group_list_list.append(new_def_group_list)
        return [Definitions(def_groups=def_group_list) for def_group_list in def_group_list_list]