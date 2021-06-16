import requests
from logger import logger

def check_page_response_status(response: requests.models.Response):
    if response.status_code != 200:
        logger.error('Response obtained from page is not nominal.')
        logger.error(f"Status code: {response.status_code}")
        raise Exception