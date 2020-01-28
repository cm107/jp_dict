from __future__ import annotations
from .misc import Link
from .base import BaseParsedObject

class CategoryLabel(BaseParsedObject):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def __str__(self):
        return self.text

    @classmethod
    def buffer(self, category_label: CategoryLabel) -> CategoryLabel:
        return category_label

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [CategoryLabel(text=f'Text {i}') for i in range(num_samples)]

class SeeAlsoLink(Link):
    def __init__(self, text: str, url: str):
        super().__init__(text, url)

    def __str__(self):
        return 'See also ' + super().__str__()

    @classmethod
    def buffer(self, see_also_link: SeeAlsoLink) -> SeeAlsoLink:
        return see_also_link

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [
            SeeAlsoLink(text=f'Text {i}', url=f'URL {i}') \
                for i in range(num_samples)
        ]

class RestrictionInfo(BaseParsedObject):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def __str__(self):
        return self.text

    @classmethod
    def buffer(self, restriction_info: RestrictionInfo) -> RestrictionInfo:
        return restriction_info

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [RestrictionInfo(text=f'Text {i}') for i in range(num_samples)]

class AdditionalInfo(BaseParsedObject):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def __str__(self):
        return self.text

    @classmethod
    def buffer(self, additional_info: AdditionalInfo) -> AdditionalInfo:
        return additional_info

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [AdditionalInfo(text=f'Text {i}') for i in range(num_samples)]

class AntonymLink(Link):
    def __init__(self, text: str, url: str):
        super().__init__(text, url)

    def __str__(self):
        return super().__str__()

    @classmethod
    def buffer(self, antonym_link: AntonymLink) -> AntonymLink:
        return antonym_link

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [
            AntonymLink(text=f'Text {i}', url=f'URL {i}') \
                for i in range(num_samples)
        ]

class SourceInfo(BaseParsedObject):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def __str__(self):
        return self.text

    @classmethod
    def buffer(self, source_info: SourceInfo) -> SourceInfo:
        return source_info

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [SourceInfo(text=f'Text {i}') for i in range(num_samples)]

class SupplementalInfo(BaseParsedObject):
    def __init__(
        self, category_label: CategoryLabel=None, see_also_link: SeeAlsoLink=None,
        restriction_info: RestrictionInfo=None, additional_info: AdditionalInfo=None,
        antonym_link: AntonymLink=None, source_info: SourceInfo=None
        ):
        super().__init__()
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

    @classmethod
    def buffer(self, supplemental_info: SupplementalInfo) -> SupplementalInfo:
        return supplemental_info

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        # return [
        #     SupplementalInfo(
        #         category_label=CategoryLabel(text=f'Text {i}'),
        #         see_also_link=SeeAlsoLink(text=f'Text {i}', url=f'URL {i}'),
        #         restriction_info=RestrictionInfo(text=f'Text {i}'),
        #         additional_info=AdditionalInfo(text=f'Text {i}'),
        #         antonym_link=AntonymLink(text=f'Text {i}', url=f'URL {i}'),
        #         source_info=SourceInfo(text=f'Text {i}')
        #     ) \
        #         for i in range(num_samples)
        # ]

        return [
            SupplementalInfo(
                category_label=category_label, see_also_link=see_also_link,
                restriction_info=restriction_info, additional_info=additional_info,
                antonym_link=antonym_link, source_info=source_info
            ) for category_label, see_also_link, restriction_info, additional_info, antonym_link, source_info in \
                zip(
                    CategoryLabel.sample(num_samples), SeeAlsoLink.sample(num_samples),
                    RestrictionInfo.sample(num_samples), AdditionalInfo.sample(num_samples),
                    AntonymLink.sample(num_samples), SourceInfo.sample(num_samples)
                )
        ]