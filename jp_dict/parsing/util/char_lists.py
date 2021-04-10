wild_cards = ['?', '*', '？', '＊']
eng_chars = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]
typo_chars = [
    '「'
]
space_chars = [
    ' ', '　'
]
hiragana_chars = list("ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ")
katakana_chars = list("ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ")
misc_kana_chars = list("ー")

hiragana2katakana_map = {hiragana_char: katakana_char for hiragana_char, katakana_char in zip(hiragana_chars, katakana_chars)}
katakana2hiragana_map = {katakana_char: hiragana_char for hiragana_char, katakana_char in zip(hiragana_chars, katakana_chars)}

def convert_hiragana2katakana(text: str) -> str:
    if text is None:
        return None
    result = ''
    for parsed_char in list(text):
        if parsed_char in hiragana_chars:
            result += hiragana2katakana_map[parsed_char]
        else:
            result += parsed_char
    return result

def convert_katakana2hiragana(text: str) -> str:
    if text is None:
        return None
    result = ''
    for parsed_char in list(text):
        if parsed_char in katakana_chars:
            result += katakana2hiragana_map[parsed_char]
        else:
            result += parsed_char
    return result

circle_number_char2int = { # Refer to https://ja.wikipedia.org/wiki/丸数字
    '⓪': 0,
    '①': 1,
    '②': 2,
    '③': 3,
    '④': 4,
    '⑤': 5,
    '⑥': 6,
    '⑦': 7,
    '⑧': 8,
    '⑨': 9,
    '⑩': 10,
    '⑪': 11,
    '⑫': 12,
    '⑬': 13,
    '⑭': 14,
    '⑮': 15,
    '⑯': 16,
    '⑰': 17,
    '⑱': 18,
    '⑲': 19,
    '⑳': 20,
    '㉑': 21,
    '㉒': 22,
    '㉓': 23,
    '㉔': 24,
    '㉕': 25,
    '㉖': 26,
    '㉗': 27,
    '㉘': 28,
    '㉙': 29,
    '㉚': 30,
    '㉛': 31,
    '㉜': 32,
    '㉝': 33,
    '㉞': 34,
    '㉟': 35,
    '㊱': 36,
    '㊲': 37,
    '㊳': 38,
    '㊴': 39,
    '㊵': 40,
    '㊶': 41,
    '㊷': 42,
    '㊸': 43,
    '㊹': 44,
    '㊺': 45,
    '㊻': 46,
    '㊼': 47,
    '㊽': 48,
    '㊾': 49,
    '㊿': 50,
    '🄋': 0,
    '➀': 1,
    '➁': 2,
    '➂': 3,
    '➃': 4,
    '➄': 5,
    '➅': 6,
    '➆': 7,
    '➇': 8,
    '➈': 9,
    '➉': 10,
    '⓿': 0,
    '❶': 1,
    '❷': 2,
    '❸': 3,
    '❹': 4,
    '❺': 5,
    '❻': 6,
    '❼': 7,
    '❽': 8,
    '❾': 9,
    '❿': 10,
    '⓫': 11,
    '⓬': 12,
    '⓭': 13,
    '⓮': 14,
    '⓯': 15,
    '⓰': 16,
    '⓱': 17,
    '⓲': 18,
    '⓳': 19,
    '⓴': 20,
    '🄌': 0,
    '➊': 1,
    '➋': 2,
    '➌': 3,
    '➍': 4,
    '➎': 5,
    '➏': 6,
    '➐': 7,
    '➑': 8,
    '➒': 9,
    '➓': 10,
    '⓵': 1,
    '⓶': 2,
    '⓷': 3,
    '⓸': 4,
    '⓹': 5,
    '⓺': 6,
    '⓻': 7,
    '⓼': 8,
    '⓽': 9,
    '⓾': 10
}