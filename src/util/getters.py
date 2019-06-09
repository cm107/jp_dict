import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

def get_response(url: str) -> requests.models.Response:
    return requests.get(url)

def get_soup(page: requests.models.Response) -> BeautifulSoup:
    return BeautifulSoup(page.content, 'html.parser')

def get_soup_child(soup: BeautifulSoup, index: int) -> list:
    return list(soup.children)[index]

def get_soup_nested_tag_child(soup: BeautifulSoup, nest_map: list) -> Tag:
    first = nest_map[0]
    result = get_soup_child(soup, first)

    next_nests = nest_map[1:]
    for i in next_nests:
        result = get_tag_child(result, i)
    return result

def get_tag_child(tag: Tag, index: int):
    return list(tag.children)[index]

def get_all_tag_children(tag: Tag) -> list:
    children_list = list(tag.children)
    children_list_len = len(children_list)
    tag_children = []
    
    for i in range(0, children_list_len):
        if type(children_list[i]) is Tag:
            tag_children.append(children_list[i])
    return tag_children

def get_html_nested_tag_child(html: Tag, nest_map: list) -> Tag:
    if len(nest_map) == 0:
        return html
    
    first = nest_map[0]
    result = get_tag_child(html, first)

    next_nests = nest_map[1:]
    for i in next_nests:
        result = get_tag_child(result, i)
    return result