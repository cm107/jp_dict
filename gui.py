import sys
import functools
from qtpy.QtCore import QSize, QPoint, QSettings, QRect, Signal, QObject, Slot
from qtpy.QtGui import QImage, QPixmap, QPalette, QIcon, QPainter, QTextCursor
from qtpy.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, \
    QFileDialog, QApplication, QAction, QWidget, QPushButton, QLineEdit, QTextEdit, QVBoxLayout
from qtpy.QtCore import Qt
from src.tools.word_list_updater import WordListUpdater
from src.submodules.logger.logger_handler import logger

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

        # super(BrowserHistoryLoadPopup, self).__init__(parent)

        # self.pushButtonPrint = QPushButton(self)
        # self.pushButtonPrint.setText("Click Me!")
        # self.pushButtonPrint.clicked.connect(self.submit)

        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(QRect(20, 140, 750, 230))

        # self.layoutVertical = QVBoxLayout(self)
        # # self.layoutVertical.addWidget(self.submit_button)
        # self.layoutVertical.addWidget(self.textEdit)
        # self.layoutVertical.setGeometry(QRect(75, 250, 50, 100))

    # def normalOutputWritten(self, text):
    #     """Append text to the QTextEdit."""
    #     cursor = self.et.textCursor()
    #     cursor.movePosition(QTextCursor.End)
    #     cursor.insertText(text)
    #     self.et.setTextCursor(cursor)
    #     self.et.ensureCursorVisible()

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

class QVocabTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_name = "VocabTracker"
        self.popup = None

        self.setWindowTitle("Vocabulary Tracker")
        self.settings = QSettings(self.app_name, self.app_name)
        size = self.settings.value('window/size', QSize(600, 500))
        position = self.settings.value('window/position', QPoint(0, 0))
        self.resize(size)
        self.move(position)

        # Shortcuts
        self.shortcuts = {}
        self.shortcuts['load_browser_history'] = ['Ctrl+L']

        # Actions
        load_browser_history_action = QAction(
            parent=self,
            text='&Load Browser History'
        )
        load_browser_history_action.setShortcuts(self.shortcuts['load_browser_history'])
        load_browser_history_action.setIconText("Load browser history")
        load_browser_history_action.setIcon(QIcon('/home/clayton/workspace/study/jp_dict/data/icons/open_icon.ico'))
        load_browser_history_action.setToolTip("Loads browser history from json and updates word list.")
        load_browser_history_action.setStatusTip("Loads browser history from json and updates word list.")
        load_browser_history_action.triggered.connect(self.update_word_list)
        load_browser_history_action.setCheckable(True)
        load_browser_history_action.setEnabled(True)

        file_menubar = self.menuBar().addMenu('&File')
        file_menubar.addAction(load_browser_history_action)
        edit_menubar = self.menuBar().addMenu('&Edit')
        view_menu = self.menuBar().addMenu('&View')
        help_menu = self.menuBar().addMenu('&Help')

        # Update Status Bar
        self.statusBar().showMessage(f'{self.app_name} started.')
        self.statusBar().show()

    def update_word_list(self):
        self.popup = BrowserHistoryLoadPopup()
        self.popup.setGeometry(QRect(100, 100, 800, 400))
        self.popup.show()

        stream = MyStream()
        stream.message.connect(self.popup.on_myStream_message)
        sys.stdout = stream

if __name__ == '__main__':
    app = QApplication(sys.argv)
    vocabTracker = QVocabTracker()
    vocabTracker.show()

    # stream = MyStream()
    # stream.message.connect(vocabTracker.popup.on_myStream_message)
    # sys.stdout = myStream

    sys.exit(app.exec_())