import time, sys
from qtpy.QtCore import QThread, Signal, Slot
from qtpy.QtWidgets import QApplication, QTextEdit
from qtpy.QtGui import QTextCursor
from ..submodules.logger.logger_handler import logger

from ..tools.word_list_updater import WordListUpdater
from .stream import MyStream

# I can't figure out how to get the multi-threading to work with sys.stderr

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
    def __init__(
        self, history_json_path: str, save_file_path: str, textEdit: QTextEdit,
        app: QApplication
    ):
        super(WordListUpdaterThread, self).__init__()
        self.history_json_path = history_json_path
        self.save_file_path = save_file_path
        self.textEdit = textEdit
        self.app = app

        stream = MyStream()
        stream.message.connect(self.on_myStream_message)
        sys.stdout = stream

        print("Test!!!!!!!!!!!!!!!")
        self.app.processEvents()

        self.running = True

    @Slot(str)
    def on_myStream_message(self, message):
        self.textEdit.moveCursor(QTextCursor.End)
        self.textEdit.insertPlainText(message)

    def run(self):
        print("Thread run start")
        self.app.processEvents()
        WordListUpdater(self.history_json_path, self.save_file_path).run(self.app)
        self.running = False