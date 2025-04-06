from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar
import bs4
from bs4 import BeautifulSoup
import requests

@dataclass
class ParsedData:
    url: str

PD = TypeVar('PD', bound=ParsedData)

class Parser(Generic[PD]):
    def __init__(self):
        pass

    def soup(self, url: str) -> tuple[int, BeautifulSoup]:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html5lib') if response.status_code == 200 else None
        return response.status_code, soup

    @abstractmethod
    def parse(self, url: str) -> PD:
        raise NotImplementedError

@dataclass
class SearchWordParsedData(ParsedData):
    word: str

SWPD = TypeVar('SWPD', bound=SearchWordParsedData)

class SearchWordParser(Parser, Generic[SWPD]):
    def __init__(
        self,
        baseUrl: str,
        searchUrlGetter: Callable[[str, str], str] | None=None
    ):
        self.baseUrl = baseUrl
        if searchUrlGetter is None:
            searchUrlGetter = lambda _baseUrl, _searchWord: (
                f"{_baseUrl}/{_searchWord}"
            )
        self.searchUrlGetter = searchUrlGetter

    def soup(self, word: str) -> tuple[int, BeautifulSoup]:
        url = self.searchUrlGetter(self.baseUrl, word)
        return super().soup(url)

    @abstractmethod
    def parse(self, word: str) -> SWPD:
        raise NotImplementedError

class JishoSearchWordParsedData(SearchWordParsedData):
    pass # Todo

class JishoSearchParser(SearchWordParser[JishoSearchWordParsedData]):
    def __init__(self):
        super().__init__(
            baseUrl='https://jisho.org/search',
            searchUrlGetter=lambda baseUrl, word: f"{baseUrl}/{word}"
        )

    def parse(self, word: str) -> JishoSearchWordParsedData:
        status, soup = self.soup(word)
        assert status == 200, f"{status=}"
        # print(soup.prettify())

        def analyze_child_dict(
            child, heading: str | None=None, indent: int=0,
            callbackDict: dict[str, Callable[[Any], Any]] | None=None
        ):
            if heading is None:
                heading = str(type(child))

            tab = '\t' * indent
            printStr = f"{tab}{heading}"

            tab = '\t' * (indent + 1)

            for key, val in child.__dict__.items():
                if callbackDict is not None and key in callbackDict:
                    printStr += f'\n{tab}{key}: {callbackDict[key](val)}'
                elif key in ['name', 'attrs']:
                    printStr += f'\n{tab}{key}: {val}'
                else:
                    printStr += f'\n{tab}{key}: {type(val)=}'
            print(printStr)

        class Tag:
            def __init__(
                self, src: bs4.element.Tag,
                parent: Tag=None,
                children: list[Tag]=None,
                text: list[str]=None,
                comments: list[str]=None,
            ):
                self.src = src

                self.parent = parent
                self.children = children if children is not None else []
                self.text = text if text is not None else []
                self.comments = comments if comments is not None else []
            
            @property
            def name(self) -> str:
                return self.src.name

            @property
            def attrs(self):
                return self.src.attrs

            def depth(self) -> int:
                if self.parent is None:
                    return 0
                else:
                    return self.parent.depth() + 1

            def populate_children(self):
                for child in self.src.children:
                    if type(child) is bs4.element.Tag:
                        tag = Tag(child, parent=self)
                        tag.populate_children()
                        self.children.append(tag)
                    elif type(child) is bs4.element.NavigableString:
                        self.text.append(child.text)
                    elif type(child) is bs4.element.Comment:
                        # print(f"Comment: {child.text=}")
                        # analyze_child_dict(
                        #     child, 'bs4.element.Comment',
                        #     callbackDict={
                        #         key: lambda val: (
                        #             val.rstrip()
                        #         )
                        #         for key in ['previous_element', 'next_element', 'previous_sibling', 'next_sibling']
                        #     }
                        # )
                        assert not hasattr(child, 'children')
                        self.comments.append(child.text)
                    elif type(child) in [bs4.element.Doctype]:
                        continue
                    else:
                        raise TypeError(f"{type(child)=}")
            
            def size(self) -> int:
                if len(self.children) == 0:
                    return 1
                else:
                    return sum([child.size() for child in self.children])

            def get_flat_hierarchy(
                self, depth: int=None, localDepth: int=None,
                workingHierarchy: list[Tag] | None=None
            ) -> list[Tag]:
                if workingHierarchy is None:
                    workingHierarchy = [self]
                else:
                    workingHierarchy.append(self)

                myDepth = self.depth()
                if localDepth is not None:
                    depth = myDepth + localDepth
                if depth is None or myDepth < depth:
                    for child in self.children:
                        child.get_flat_hierarchy(
                            depth=depth, workingHierarchy=workingHierarchy
                        )
                return workingHierarchy

            def summarize_hierarchy(
                self, indent: str=0,
                depth: int=None, localDepth: int=None,
                showLineNum: bool=False,
                showText: bool=False
            ) -> tuple[int, str]:
                hierarchy = self.get_flat_hierarchy(depth=depth, localDepth=localDepth)
                rootDepth = self.depth()
                if localDepth is not None:
                    depth = rootDepth + localDepth

                printStr = ""
                for lineNum, tag in enumerate(hierarchy):
                    myDepth = tag.depth()

                    tab = '\t' * (indent + myDepth - rootDepth)

                    if lineNum > 0:
                        printStr += '\n'
                    if showLineNum:
                        printStr += f"{lineNum}\t"
                    printStr += f"{tab}{tag.name}"
                    
                    if len(tag.attrs) > 0:
                        attrsStr = ','.join([f"{key}->{val}" for key, val in tag.attrs.items()])
                        attrsStr = f"({attrsStr})"
                        printStr += f" {attrsStr}"

                    first = True
                    if len(tag.text) > 0:
                        printStr += ':' if first else ','; first = False
                        if not showText:
                            printStr += f" Texts->{len(tag.text)}"
                        else:
                            printStr += f" Texts->{tag.text}"
                    if len(tag.comments) > 0:
                        printStr += ':' if first else ','; first = False
                        printStr += f" Comments->{len(tag.comments)}"

                    if depth is not None and myDepth == depth and len(tag.children) > 0:
                        printStr += ':' if first else ','; first = False
                        printStr += f" Children->{len(tag.children)}"

                return printStr
            
        print(f"{[type(child) for child in soup.children]=}")
        
        # for child in soup.children:
        #     print(f"{type(child)=}")
        #     if type(child) is bs4.element.Doctype:
        #         # analyze_child_dict(child, heading='bs4.element.Doctype')
        #         continue
        #     elif type(child) is bs4.element.Tag:
        #         tag = Tag(child)
        #         tag.populate_children()
        #         print(f"{tag.size()=}")
        #         print(tag.summarize_hierarchy(depth=3))
        tag = Tag(soup)
        tag.populate_children()
        _tag = (
            tag
            .get_flat_hierarchy(localDepth=3)[23]
            .get_flat_hierarchy(localDepth=3)[14]
            .get_flat_hierarchy(localDepth=3)[2]
        )
        print(f"{_tag.size()=}")
        print(_tag.summarize_hierarchy(localDepth=3, showLineNum=True, showText=False))

    
    @staticmethod
    def debug():
        parser = JishoSearchParser()
        parser.parse('言葉')

        
