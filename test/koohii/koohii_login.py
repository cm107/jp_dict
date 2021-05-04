import requests
from bs4 import BeautifulSoup
import urllib3

class KoohiiParser:
    def __init__(self):
        if not self.login():
            raise Exception('Failed to login to koohii. Need to adjust headers.')

    @property
    def login_headers(self) -> str:
        """
        Refer to: https://stackoverflow.com/a/61140905
        Code converted from curl using this tool: https://curl.trillworks.com/
        """
        return {
            'authority': 'kanji.koohii.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'origin': 'https://kanji.koohii.com',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://kanji.koohii.com/account',
            'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7',
            'cookie': '_ga=GA1.2.382089607.1620143131; _gid=GA1.2.1242003175.1620143131; koohii=4529ba44ec89fe74eb227bde07aeffa2; _gat=1',
        }

    @property
    def login_data(self) -> str:
        return {
        'referer': '@homepage',
        'username': 'jpdict_scraper',
        'password': 'password',
        'commit': 'Sign In'
        }

    def login(self) -> bool:
        response = requests.post(
            'https://kanji.koohii.com/login',
            headers=self.login_headers, data=self.login_data
        )
        return response.status_code == 200
    
    @property
    def search_headers(self) -> str:
        return {
            'authority': 'kanji.koohii.com',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://kanji.koohii.com/study',
            'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7',
            'cookie': '_ga=GA1.2.382089607.1620143131; _gid=GA1.2.1242003175.1620143131; koohii=6709def3e83ad9451f66297125042faa; _gat=1',
        }
    
    def get_search_soup(self, search_kanji: str) -> BeautifulSoup:
        search_url = f'https://kanji.koohii.com/study/kanji/{search_kanji}'
        _http = urllib3.PoolManager()
        page = _http.request(method='GET', url=search_url, headers=self.search_headers)
        assert page.status == 200, f'Received page status of {page.status}'
        return BeautifulSoup(page.data, 'html.parser')

    def parse(self, search_kanji: str):
        soup = self.get_search_soup(search_kanji=search_kanji)
        row_html = soup.find(name='div', class_='row')
        # print(row_html)
        lesson_name_html = (
            row_html
            .find(name='div', class_='col-md-9')
            .find(name='div', id='EditStoryComponent')
            .find(name='div', style='position:relative;')
            .find(name='h2')
        )
        lesson_name = lesson_name_html.text.strip()
        print(f'lesson_name: {lesson_name}')
        frame_num_html = row_html.find(name='div', title='Frame number', class_='framenum')
        frame_num = frame_num_html.text.strip()
        print(f'frame_num: {frame_num}')
        keyword_html = row_html.find(name='span', class_='JSEditKeyword')
        keyword = keyword_html.text.strip()
        print(f'keyword: {keyword}')
        kanji_html = row_html.find(name='div', class_='kanji')
        kanji = kanji_html.text.strip()
        print(f'kanji: {kanji}')
        stroke_count_html = row_html.find(name='div', title='Stroke count', class_='strokecount')
        stroke_count_text, reading = stroke_count_html.text.strip().split('\n')
        stroke_count = int(stroke_count_text.replace('[', '').replace(']', ''))
        print(f'stroke_count: {stroke_count}')
        print(f'reading: {reading}')

        new_shared_story_html_list = (
            row_html
            .find(name='div', id='sharedstories-new')
            .find_all(name='div', class_='story')
        )
        new_shared_story_text_list = [html.text.strip() for html in new_shared_story_html_list]
        print(new_shared_story_text_list)
        shared_story_html_list = (
            row_html
            .find(name='div', id='SharedStoriesListComponent')
            .find_all(name='div', class_='story')
        )
        shared_story_text_list = [html.text.strip() for html in shared_story_html_list]
        print(shared_story_text_list)
        # TODO: Finish implementing

parser = KoohiiParser()
parser.parse('迂')