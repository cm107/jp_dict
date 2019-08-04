from ...lib.history_parsing.history_parser import HistoryParser

class FaviconDownloader:
    def __init__(self, history_json_path: str, icon_dump_dir: str):
        self.history_parser = HistoryParser(history_json_path=history_json_path)
        self.icon_dump_dir = icon_dump_dir

    def run(self):
        self.history_parser.load()
        self.history_parser.download_all_favicon(icon_dump_dir=self.icon_dump_dir)