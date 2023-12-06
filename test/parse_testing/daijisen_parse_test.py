from jp_dict.parsing.kotobank.kotobank_structs import KotobankWordHtmlParser

# parser = KotobankWordHtmlParser.from_search_word('数多')
# parser = KotobankWordHtmlParser.from_search_word('大勢')
# parser = KotobankWordHtmlParser.from_search_word('新手')
# parser = KotobankWordHtmlParser.from_search_word('アキレス腱')
# parser = KotobankWordHtmlParser.from_search_word('気骨')
# parser = KotobankWordHtmlParser.from_search_word('集る')
# parser = KotobankWordHtmlParser.from_search_word('邪')
# parser = KotobankWordHtmlParser.from_search_word('吹出す')
# parser = KotobankWordHtmlParser.from_search_word('控目')
# parser = KotobankWordHtmlParser.from_search_word('斥候')
# parser = KotobankWordHtmlParser.from_search_word('白色')
parser = KotobankWordHtmlParser.from_search_word('水を向ける')
# parser = KotobankWordHtmlParser.from_search_word('端正')
# parser = KotobankWordHtmlParser.from_search_word('痩せぎす')
# parser = KotobankWordHtmlParser.from_search_word('淀む')
print(f"{parser.url=}")
result = parser.parse()
result.save_to_path('/tmp/kotobank_test.json', overwrite=True)
print(f"result.dictionary_names: {result.dictionary_names}")
# print(result.digital_daijisen_content)
html = result.digital_daijisen_content.custom_str().replace('\n', '<br>')
# print(html)

temp_path = '/tmp/temp.html'
f = open(temp_path, 'w')
f.writelines(html)

# import webbrowser
# # new = 2 # open in a new tab, if possible
# new = 1
# webbrowser.open(temp_path,new=new)