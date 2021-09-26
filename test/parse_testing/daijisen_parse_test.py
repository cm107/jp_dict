from jp_dict.parsing.kotobank.kotobank_structs import KotobankWordHtmlParser

# parser = KotobankWordHtmlParser.from_search_word('虐げる')
parser = KotobankWordHtmlParser.from_search_word('数多')
# parser = KotobankWordHtmlParser.from_search_word('手札')
# parser = KotobankWordHtmlParser.from_search_word('風雅')
# parser = KotobankWordHtmlParser.from_search_word('英田')
result = parser.parse()
print(f"result.dictionary_names: {result.dictionary_names}")
# print(result.seisenpan_content.custom_str())
print(result.custom_str())
# print(result.digital_daijisen_content.custom_str())