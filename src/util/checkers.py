import requests

def check_page_response_status(response: requests.models.Response):
    if response.status_code != 200:
        raise Exception('Response obtained from page is not nominal.')