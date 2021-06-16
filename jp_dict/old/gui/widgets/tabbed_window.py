from qtpy.QtCore import Slot
from qtpy.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton

# TODO: Add tabs to QVocabTracker window.
# Check Word List / Preview Definitions / ...
# Refer to: https://pythonspot.com/pyqt5-tabs/

class VocabTrackerTabbedWindow(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.resize(300, 200)

        # Add tabs
        self.check_word_list_tab = QWidget()
        self.tabs.addTab(self.check_word_list_tab, "Check Word List")

        self.preview_definitions_tab = QWidget()
        self.tabs.addTab(self.preview_definitions_tab, "Preview Definitions")

        # Check Word List tab
        self.check_word_list_tab.layout = QVBoxLayout(self)
        self.button0 = QPushButton("Test Button 0")
        self.check_word_list_tab.layout.addWidget(self.button0)
        self.check_word_list_tab.setLayout(self.check_word_list_tab.layout)

        # Preview Definitions tab
        self.preview_definitions_tab.layout = QVBoxLayout(self)
        self.button1 = QPushButton("Test Button 1")
        self.preview_definitions_tab.layout.addWidget(self.button1)
        self.preview_definitions_tab.setLayout(self.preview_definitions_tab.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    # @Slot()
    # def on_click(self):
    #     print("\n")
    #     for current_tabbed_window in self.vocab_tracker_tabbed_window.selectedItems():
    #         print(current_tabbed_window.row(), current_tabbed_window.column(), current_tabbed_window.text())