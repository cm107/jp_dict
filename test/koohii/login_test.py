from webbot import Browser

web = Browser(showWindow=False)
web.go_to('https://kanji.koohii.com/account')
web.type('jpdict_scraper', into='Username')
web.type('password', into='Password')
web.click('Sign In')

search_kanji = '迂'
search_url = f'https://kanji.koohii.com/study/kanji/{search_kanji}'
web.go_to(search_url)
html = web.get_page_source()
print(html)