from qtpy.QtCore import QRect, Signal, QObject, Slot
from qtpy.QtGui import QTextCursor
from qtpy.QtWidgets import QMessageBox, QFileDialog, QWidget, QPushButton, \
    QLineEdit, QTextEdit
from ..tools.word_list_updater import WordListUpdater
from ..submodules.logger.logger_handler import logger

# TODO: Figure out how get gui to refresh while script is running, and not just when the script returns.
# https://stackoverflow.com/questions/24371274/how-to-dynamically-update-qtextedit

# Try implementing text stream in popup window as shown in link:
# https://stackoverflow.com/questions/15637768/pyqt-how-to-capture-output-of-pythons-interpreter-and-display-it-in-qedittext
class MyStream(QObject):
    message = Signal(str)
    def __init__(self, parent=None):
        super(MyStream, self).__init__(parent)

    def write(self, message):
        self.message.emit(str(message))

class BrowserHistoryLoadPopup(QWidget):
    def __init__(self, parent=None):
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
        self.save_path = None

        self.submit_button = QPushButton("Start", self)
        self.submit_button.setGeometry(QRect(300, 85, 150, 40))
        self.submit_button.clicked.connect(self.submit)
        self.submit_button.setEnabled(False)

        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(QRect(20, 140, 750, 230))

    def test(self):
        from src.tools.word_list_updater import PrintTest
        PrintTest().test()

    def open_history_json(self):
        import time
        for i in range(5):
            self.test()
            time.sleep(1)

        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
                                                  'JSON (*.json)', options=options)
        if filename:
            from src.submodules.common_utils.file_utils import file_exists
            if not file_exists(filename):
                QMessageBox.information(self, "Vocab Tracker", "Cannot find %s." % filename)
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
        self.save_path = paths[0]
        self.textbox2.setText(self.save_path)
        self.enable_submit_if_valid()
        logger.info(f"Opened {self.save_path}")

    def enable_submit_if_valid(self):
        if self.history_json_path is not None and self.save_path is not None:
            self.submit_button.setEnabled(True)

    # @Slot()
    def submit(self):
        logger.blue("Test")
        WordListUpdater(
            history_json_path=self.history_json_path,
            save_file_path=self.save_path
        ).run()

    @Slot(str)
    def on_myStream_message(self, message):
        self.textEdit.moveCursor(QTextCursor.End)
        self.textEdit.insertPlainText(message)