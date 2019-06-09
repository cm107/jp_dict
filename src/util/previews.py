from bs4 import BeautifulSoup
from bs4.element import Tag
from .getters import get_soup_child, get_tag_child

blue_text = '\033[94m'
green_text = '\033[92m'
yellow_text = '\033[93m'
red_text = '\033[1;31;40m'
std_text = '\033[0m'

def preview_soup_nested_tag_children(soup: BeautifulSoup, nest_map: list, hidden_children: list):
    first = nest_map[0]
    result = get_soup_child(soup, first)

    next_nests = nest_map[1:]
    for i in next_nests:
        result = get_tag_child(result, i)
    preview_tag_children(result, hidden_children)

def preview_tag_children(html: Tag, hidden_children: list):
    if html is not None:
        html_children_list = list(html.children)
        list_len = len(html_children_list)
        for i in range(list_len):
            print("{}========{} begin========{}".format(blue_text, i, std_text))
            print("{}{}{}".format(green_text, type(html_children_list[i]), std_text))
            print("{}Content Length: {}{}".format(green_text, len(html_children_list[i]), std_text))
            if i not in hidden_children:
                print("{}".format(html_children_list[i]))
            else:
                print('Hidden')
            print("{}========{} end========{}".format(blue_text, i, std_text))

def preview_html_nested_tag_children(html: Tag, nest_map: list, hidden_children: list):
    if len(nest_map) == 0:
        preview_tag_children(html, hidden_children)
        return
    
    first = nest_map[0]
    result = get_tag_child(html, first)

    next_nests = nest_map[1:]
    for i in next_nests:
        result = get_tag_child(result, i)
    preview_tag_children(result, hidden_children)