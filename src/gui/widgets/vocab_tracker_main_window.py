import sys
from qtpy.QtCore import QSize, QPoint, QSettings, QRect
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QMainWindow, QApplication, QAction, QTextEdit, QVBoxLayout
from ...submodules.logger.logger_handler import logger
from ...gui.widgets.browser_history_load_popup import BrowserHistoryLoadPopup

class QVocabTracker(QMainWindow):
    def __init__(self, app):
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

        # Application
        self.app = app

    def update_word_list(self):
        self.popup = BrowserHistoryLoadPopup(self.app)
        self.popup.setGeometry(QRect(100, 100, 800, 400))
        self.popup.show()
