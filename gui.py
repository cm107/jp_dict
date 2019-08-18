import sys
import functools
from qtpy.QtCore import QSize, QPoint, QSettings, QRect
from qtpy.QtGui import QImage, QPixmap, QPalette, QIcon, QPainter
from qtpy.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, \
    QFileDialog, QApplication, QAction, QWidget, QPushButton, QLineEdit
from qtpy.QtCore import Qt
from src.tools.word_list_updater import WordListUpdater

class MyPopup(QWidget):
    def __init__(self):
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
        self.submit_button.setGeometry(QRect(200, 200, 150, 40))
        self.submit_button.clicked.connect(self.submit)
        self.submit_button.setEnabled(False)

    def open_history_json(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
                                                  'JSON (*.json)', options=options)
        if filename:
            from src.submodules.common_utils.file_utils import file_exists
            if not file_exists(filename):
                QMessageBox.information(self, "Vocab Tracker", "Cannot find %s." % filename)
                return
            print(f"Opened {filename}")
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

    def enable_submit_if_valid(self):
        if self.history_json_path is not None and self.save_path is not None:
            self.submit_button.setEnabled(True)

    def submit(self):
        WordListUpdater(
            history_json_path=self.history_json_path,
            save_file_path=self.save_path
        ).run()

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
        self.shortcuts['file_open'] = ['Ctrl+O']

        # Actions
        file_open_action = QAction(
            parent=self,
            text='File &Open'
        )
        file_open_action.setShortcuts(self.shortcuts['file_open'])
        file_open_action.setIconText("Open JSON")
        file_open_action.setIcon(QIcon('/home/clayton/workspace/study/jp_dict/data/icons/open_icon.ico'))
        file_open_action.setToolTip("Opens a new browser history json.")
        file_open_action.setStatusTip("Opens a new browser history json.")
        file_open_action.triggered.connect(self.open)
        file_open_action.setCheckable(True)
        file_open_action.setEnabled(True)

        file_menubar = self.menuBar().addMenu('&File')
        file_menubar.addAction(file_open_action)
        edit_menubar = self.menuBar().addMenu('&Edit')
        view_menu = self.menuBar().addMenu('&View')
        help_menu = self.menuBar().addMenu('&Help')

        # Update Status Bar
        self.statusBar().showMessage(f'{self.app_name} started.')
        self.statusBar().show()

    def open(self):
        self.popup = MyPopup()
        self.popup.setGeometry(QRect(100, 100, 800, 400))
        self.popup.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    vocabTracker = QVocabTracker()
    vocabTracker.show()
    sys.exit(app.exec_())