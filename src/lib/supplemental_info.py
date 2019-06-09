from .misc import Link

class CategoryLabel:
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.__str__()

class SeeAlsoLink:
    def __init__(self, text: str, url: str):
        self.link = Link(text, url)

    def __str__(self):
        return 'See also ' + self.link.__str__()

    def __repr__(self):
        return self.__str__()

class RestrictionInfo:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.__str__()

class AdditionalInfo:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.__str__()

class AntonymLink:
    def __init__(self, text: str, url: str):
        self.link = Link(text, url)

    def __str__(self):
        return self.link.__str__()

    def __repr__(self):
        return self.__str__()

class SourceInfo:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.__str__()

class SupplementalInfo:
    def __init__(
        self, category_label: CategoryLabel=None, see_also_link: SeeAlsoLink=None,
        restriction_info: RestrictionInfo=None, additional_info: AdditionalInfo=None,
        antonym_link: AntonymLink=None, source_info: SourceInfo=None
        ):
        self.category_label = category_label
        self.see_also_link = see_also_link
        self.restriction_info = restriction_info
        self.additional_info = additional_info
        self.antonym_link = antonym_link
        self.source_info = source_info

    def __str__(self):
        def append_str(first: bool, print_str: str, item) -> (bool, str):
            result_str = print_str
            if first:
                result_str += '{}'.format(item)
            else:
                result_str += ', {}'.format(item)
            return False, result_str

        first = True
        print_str = ''
        if self.category_label is not None:
            first, print_str = append_str(first, print_str, self.category_label)
        if self.see_also_link is not None:
            first, print_str = append_str(first, print_str, self.see_also_link)
        if self.restriction_info is not None:
            first, print_str = append_str(first, print_str, self.restriction_info)
        if self.additional_info is not None:
            first, print_str = append_str(first, print_str, self.additional_info)
        if self.antonym_link is not None:
            first, print_str = append_str(first, print_str, self.antonym_link)
        if self.source_info is not None:
            first, print_str = append_str(first, print_str, self.source_info)
        return print_str

    def __repr__(self):
        return self.__str__()
