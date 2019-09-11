import sys
from qtpy.QtCore import QSize, QPoint, QSettings, QRect
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QMainWindow, QAction, QTabWidget, QFileDialog, \
    QMessageBox, QLineEdit, QPushButton
from ...submodules.logger.logger_handler import logger
from ...submodules.common_utils.file_utils import file_exists
from ...gui.widgets.browser_history_load_popup import BrowserHistoryLoadPopup
from ...gui.widgets.tabed_window import VocabTrackerTabbedWindow

# TODO: Implement VocabTrackerTabedWindow

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

        # QMainWindow UI
        load_section_y = 30
        tabbed_window_y = 60

        self.load_button = QPushButton("Load", self)
        self.load_button.setGeometry(QRect(0, load_section_y, 100, 30))
        self.load_button.clicked.connect(self.load_vocab_list)
        self.load_button.setEnabled(True)

        self.load_button_textbox = QLineEdit(self)
        self.load_button_textbox.setGeometry(110, load_section_y, 600, 30)

        self.vocab_tracker_tabbed_window = VocabTrackerTabbedWindow(self)
        self.vocab_tracker_tabbed_window.move(10, tabbed_window_y)
        self.vocab_tracker_tabbed_window.resize(400, 400)
        # self.setCentralWidget(self.vocab_tracker_tabbed_window)

        # QMainWindow UI related variables
        self.vocab_list_path = None

    def update_word_list(self):
        self.popup = BrowserHistoryLoadPopup(self.app)
        self.popup.setGeometry(QRect(100, 100, 800, 400))
        self.popup.show()

    def load_vocab_list(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Load Vocab List',
            "/home/clayton/workspace/study/jp_dict/data/word_list_save",
            'PKL(*.pkl)',
            options=options
        )
        if filename:
            if not file_exists(filename):
                QMessageBox.information(self, "Vocab Tracker", f"Cannot find {filename}")
                return
            self.vocab_list_path = filename
            logger.info(f"Opened {filename}")
            self.load_button_textbox.setText(filename)
            self.enable_stuff_if_vocab_list_is_valid()

    def enable_stuff_if_vocab_list_is_valid(self):
        pass
            
        
