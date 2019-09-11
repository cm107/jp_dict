import sys
from qtpy.QtCore import QRect, Signal, QObject, Slot
from qtpy.QtGui import QTextCursor
from qtpy.QtWidgets import QMessageBox, QFileDialog, QWidget, QPushButton, \
    QLineEdit, QTextEdit
from ...tools.word_list_updater import WordListUpdater
from ...submodules.logger.logger_handler import logger
from ...gui.threads import BackgroundThread, WordListUpdaterThread
from src.submodules.common_utils.file_utils import file_exists

class BrowserHistoryLoadPopup(QWidget):
    stop_sig = Signal(bool)
    def __init__(self, app=None):
        QWidget.__init__(self)
        self.btn1 = QPushButton("JSON File", self)
        self.btn1.setGeometry(QRect(0, 0, 100, 30))
        self.btn1.clicked.connect(self.open_history_json)

        self.textbox1 = QLineEdit(self)
        self.textbox1.setGeometry(110, 0, 600, 30)

        self.btn2 = QPushButton("Save Path", self)
        self.btn2.setGeometry(QRect(0, 40, 100, 30))
        self.btn2.clicked.connect(self.select_save_path)

        self.textbox2 = QLineEdit(self)
        self.textbox2.setGeometry(110, 40, 600, 30)

        self.history_json_path = None
        self.save_file_path = None

        self.submit_button = QPushButton("Start", self)
        self.submit_button.setGeometry(QRect(300, 85, 150, 40))
        self.submit_button.clicked.connect(self.submit)
        self.submit_button.setEnabled(False)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setGeometry(QRect(500, 85, 150, 40))
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setEnabled(False)
        self.stop_flag = False

        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(QRect(20, 140, 750, 230))

        self.test_count = 0

        self.submit_thread = None

        self.app = app

    def open_history_json(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'QFileDialog.getOpenFileName()',
            '/home/clayton/workspace/study/jp_dict/data/browser_history',
            'JSON (*.json)',
            options=options
        )
        if filename:
            if not file_exists(filename):
                QMessageBox.information(self, "Vocab Tracker", f"Cannot find {filename}")
                return
            logger.info(f"Opened {filename}")
        self.history_json_path = filename
        self.textbox1.setText(filename)
        self.enable_submit_if_valid()

    def select_save_path(self):
        paths = QFileDialog.getSaveFileName(
            self,
            'Vocab List Save',
            "/home/clayton/workspace/study/jp_dict/data/word_list_save",
            'PKL(*.pkl)'
        )
        self.save_file_path = paths[0]
        self.textbox2.setText(self.save_file_path)
        self.enable_submit_if_valid()
        logger.info(f"Opened {self.save_file_path}")

    def enable_submit_if_valid(self):
        if self.history_json_path is not None and self.save_file_path is not None:
            self.submit_button.setEnabled(True)

    def submit(self):
        logger.info('BrowserHistoryLoadPopup: submit')
        self.submit_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        current_index = None
        if self.submit_thread is not None and self.submit_thread.current_index is not None:
            current_index = self.submit_thread.current_index
        self.submit_thread = WordListUpdaterThread(
            history_json_path=self.history_json_path,
            save_file_path=self.save_file_path
        )
        if current_index is not None:
            self.submit_thread.current_index = current_index
            self.submit_thread.word_list_updater.current_index = current_index
        self.submit_thread.start()
        self.submit_thread.message_sig.connect(self.on_wordlist_updater_message)
        self.stop_button.setEnabled(True)

    def stop(self):
        logger.info('BrowserHistoryLoadPopup: stop')
        self.stop_flag = True
        self.stop_button.setEnabled(False)
        self.stop_sig.connect(self.submit_thread.on_stop_flag)
        self.stop_sig.emit(self.stop_flag)
        self.submit_button.setEnabled(True)

    @Slot(str)
    def on_wordlist_updater_message(self, message):
        self.textEdit.moveCursor(QTextCursor.End)
        self.textEdit.insertPlainText(message)