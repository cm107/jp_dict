class BrowserHistoryItem:
    def __init__(
        self, favicon_url: str, page_transition: str, title: str,
        url: str, client_id: str, time_usec: int
    ):
        self.favicon_url = favicon_url
        self.page_transition = page_transition
        self.title = title
        self.url = url
        self.client_id = client_id
        self.time_usec = time_usec

class BrowserHistory:
    def __init__(self):
        self.history_items = []

    def add(self, history_item: BrowserHistoryItem):
        self.history_items.append(history_item)

    def get_favicon_url_list(self) -> list:
        favicon_url_list = []
        for history_item in self.history_items:
            favicon_url_list.append(history_item.favicon_url)
        return favicon_url_list