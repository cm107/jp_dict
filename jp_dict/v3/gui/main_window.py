from __future__ import annotations
from PyQt5.QtWidgets import QMainWindow, \
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, \
    QTabWidget

from .gui_settings import guiSettings
from .history_info_tab import HistoryInfoTab
from .jisho_parsing_tab import JishoParsingTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(guiSettings.windowTitle)
        self.setGeometry(*guiSettings.windowPos, *guiSettings.windowSize)
        self.setStyleSheet(f"font-size: {guiSettings.fontSize}px;")

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        self.tabs = QTabWidget()
        self.tabs.resize(300, 200)

        self.historyInfoTab = HistoryInfoTab(self)
        self.tabs.addTab(self.historyInfoTab, "History Info")
        self.jishoParsingTab = JishoParsingTab(self)
        self.tabs.addTab(self.jishoParsingTab, "Jisho Parsing")

        layout = QVBoxLayout()
        centralWidget.setLayout(layout)
        layout.addWidget(self.tabs)

        # Execute Start Logic
        self.start()
    
    def start(self):
        self.historyInfoTab.start()
