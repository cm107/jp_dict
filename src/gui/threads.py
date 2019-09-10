import time, sys
from qtpy.QtCore import QThread, Signal, Slot
from qtpy.QtWidgets import QApplication, QTextEdit
from qtpy.QtGui import QTextCursor
from ..submodules.logger.logger_handler import logger

from ..tools.word_list_updater import WordListUpdater

# I can't figure out how to get the multi-threading to work with sys.stderr
# Refer to https://www.zeolearn.com/magazine/getting-started-guis-with-python-pyqt-qthread-class

class BackgroundThread(QThread):
    '''Keeps the main loop responsive'''

    def __init__(self, app: QApplication, worker: QThread):
        super(BackgroundThread, self).__init__()

        self.app = app
        self.worker = worker

    def run(self, sleep_time: float=0.1, silent: bool=True):
        '''This starts the thread on the start() call'''

        while self.worker.running:
            self.app.processEvents()
            if not silent:
                logger.info("Updating the main loop")
            time.sleep(sleep_time)

class TestWorkerThread(QThread):
    '''Does the work'''

    def __init__(self):
        super(TestWorkerThread, self).__init__()

        self.running = True

    def run(self):
        '''This starts the thread on the start() call'''

        # this goes over 1000 numbers, at 10 a second, will take
        # 100 seconds to complete, over a minute
        for i in range(1000):
            print(i)
            time.sleep(0.1)

        self.running = False

class WordListUpdaterThread(QThread):
    message_sig = Signal(str)
    def __init__(
        self, history_json_path: str, save_file_path: str
    ):
        super(WordListUpdaterThread, self).__init__()
        self.history_json_path = history_json_path
        self.save_file_path = save_file_path
        self.word_list_updater = WordListUpdater(
            history_json_path=self.history_json_path,
            save_file_path=self.save_file_path
        )
        self.running = True
        self.stop_flag = False
        self.current_index = None

    @Slot(bool)
    def on_stop_flag(self, stop_flag: bool):
        self.stop_flag = stop_flag
        self.current_index = self.word_list_updater.current_index

    def run(self):
        done = False
        while not done and not self.stop_flag:
            done = self.word_list_updater.step(message_sig=self.message_sig)
        self.running = False