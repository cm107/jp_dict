from .supplemental_info import SupplementalInfo

class DefinitionSection:
    def __init__(self, section_number: int, definition_text: str, supplemental_info: SupplementalInfo=None):
        self.section_number = section_number
        self.definition_text = definition_text
        self.supplemental_info = supplemental_info

    def __str__(self):
        if self.supplemental_info is not None:
            return "{}. {}  {}".format(self.section_number, self.definition_text, self.supplemental_info)
        else:
            return "{}. {}".format(self.section_number, self.definition_text)

    def __repr__(self):
        return self.__str__()

class DefinitionGroup:
    def __init__(self, group_usage: str, definition_sections: list):
        self.group_usage = group_usage
        self.definition_sections = definition_sections

    def __str__(self):
        print_str = '{}\n'.format(self.group_usage)
        for definition_section in self.definition_sections:
            print_str += "\t{}\n".format(definition_section)
        return print_str
    
    def __repr__(self):
        return self.__str__()

class Definitions:
    def __init__(self, def_groups: list):
        self.def_groups = def_groups

    def __str__(self):
        print_str = ''
        for def_group in self.def_groups:
            print_str += def_group.__str__()
        return print_str
    
    def __repr__(self):
        return self.__str__()