from __future__ import annotations
from dataclasses import dataclass
import json
from typing import TYPE_CHECKING, Any
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, \
    QTabWidget, QTabBar, QProgressBar, QTableWidget, QTableWidgetItem, \
    QTableView, QTableWidgetSelectionRange, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal, pyqtBoundSignal, \
    QObject, QThread, QThreadPool, QRunnable, QTimer

import numpy as np
import pandas as pd
import urllib.parse

from ...util.time_utils import get_localtime_from_time_usec
from .gui_settings import guiSettings
from ..history_util import HistoryUtil
if TYPE_CHECKING:
    from .main_window import MainWindow

class CalcHistoryEntriesThread(QThread):
    combiningHistoryStart = pyqtSignal(int)
    combiningHistoryProgress = pyqtSignal(int)
    combiningHistoryFinish = pyqtSignal()
    historyEntriesReady = pyqtSignal(list)

    def __init__(
        self,
        historyPaths: list[str],
        parent: QWidget | None=None
    ):
        super().__init__(parent)
        self.historyPaths: list[str] = historyPaths

    def run(self):
        self.combiningHistoryStart.emit(len(self.historyPaths))
        combinedTimeEntryMap: dict[int, dict] = dict()
        for i, path in enumerate(self.historyPaths):
            data = json.load(open(path, 'r'))
            entries: list[dict] = data['Browser History'][::-1]
            while len(entries) > 0:
                entry = entries.pop()
                combinedTimeEntryMap[entry['time_usec']] = entry
            self.combiningHistoryProgress.emit(i+1)
        combinedEntries: list[dict] = list(combinedTimeEntryMap.values())
        combinedEntries.sort(key=lambda obj: obj['time_usec'])
        self.historyEntriesReady.emit(combinedEntries)
        self.combiningHistoryFinish.emit()

class HistoryInfoObj(QObject):
    historyPathsUpdated = pyqtSignal()
    historyPathsChanged = pyqtSignal(list)
    historyEntriesUpdated = pyqtSignal()
    historyEntriesChanged = pyqtSignal(list)
    jishoHistoryEntriesUpdated = pyqtSignal()
    jishoHistoryEntriesChanged = pyqtSignal(list)
    jishoSearchWordsUpdated = pyqtSignal()
    jishoSearchWordsChanged = pyqtSignal(dict)
    wordDfUpdated = pyqtSignal()
    wordDfChanged = pyqtSignal(pd.DataFrame)

    combiningHistoryStart = pyqtSignal(int)
    combiningHistoryProgress = pyqtSignal(int)
    combiningHistoryFinish = pyqtSignal()
    def __init__(self, parent: QObject | None=None):
        super().__init__(parent)
        self._historyPaths: list[str] | None = None
        self._historyEntries: list[dict] | None = None
        self._calcHistoryEntriesThread: CalcHistoryEntriesThread | None = None
        self._jishoHistoryEntries: list[dict] | None = None
        self._jishoSearchWords: dict[str, list[int]] | None = None
        self._wordDf: pd.DataFrame | None = None

        # Signals
        self.historyPathsUpdated.connect(self._calc_history_entries)
        self.historyEntriesUpdated.connect(self._calc_jisho_history_entries)
        self.jishoHistoryEntriesUpdated.connect(self._calc_jisho_search_words)
        self.jishoSearchWordsUpdated.connect(self._calc_word_df)
        self.wordDfUpdated.connect(lambda: print(self.wordDf))

    def find_history_paths(self):
        self.historyPaths = HistoryUtil.get_history_paths(guiSettings.historyDir)
    
    def _calc_history_entries(self):
        thread = CalcHistoryEntriesThread(self.historyPaths)
        thread.combiningHistoryStart.connect(self.combiningHistoryStart)
        thread.combiningHistoryProgress.connect(self.combiningHistoryProgress)
        thread.combiningHistoryFinish.connect(self.combiningHistoryFinish)
        
        def update_history_entries(historyEntries: list[dict]):
            self.historyEntries = historyEntries

        thread.historyEntriesReady.connect(update_history_entries)
        thread.start()
        thread.finished.connect(thread.deleteLater)
        self._calcHistoryEntriesThread = thread

    def _calc_jisho_history_entries(self):
        self.jishoHistoryEntries = [
            entry for entry in self.historyEntries
            if entry['url'].startswith('https://jisho.org/search/')
        ]

    def _calc_jisho_search_words(self):
        def get_word(url: str) -> str:
            url = urllib.parse.unquote(url)
            word = url.replace('https://jisho.org/search/', '')
            return word

        words: dict[str, list[int]] = dict()
        for entry in self.jishoHistoryEntries:
            word = get_word(entry['url'])
            if any([
                invalidStr in word
                for invalidStr in guiSettings.invalidSearchStrList
            ]):
                continue
            if word not in words:
                words[word] = []
            words[word].append(entry['time_usec'])

        self.jishoSearchWords = words

    def _calc_word_df(self):
        data: dict[str, list[Any]] = dict()
        def add(key: str, value: Any):
            if key not in data:
                data[key] = []
            data[key].append(value)

        for word, time_usec_list in self.jishoSearchWords.items():
            add('Search Word', word)
            add('Search Count', len(time_usec_list))
            firstSearchTime = get_localtime_from_time_usec(min(time_usec_list))
            lastSearchTime = get_localtime_from_time_usec(max(time_usec_list))
            add('First Search', firstSearchTime.strftime('%Y-%m-%d %H:%M:%S'))
            add('Last Search', lastSearchTime.strftime('%Y-%m-%d %H:%M:%S'))
            add('ID', min(time_usec_list))

        wordDf = pd.DataFrame(data)
        self.wordDf = wordDf

    @property
    def historyPaths(self) -> list[str]:
        if self._historyPaths is None:
            raise ValueError("History paths not set.")
        return self._historyPaths

    @historyPaths.setter
    def historyPaths(self, value: list[str]):
        self._historyPaths = value
        self.historyPathsUpdated.emit()
        self.historyPathsChanged.emit(value)
    
    @property
    def historyEntries(self) -> list[dict]:
        if self._historyEntries is None:
            raise ValueError("History entries not set.")
        return self._historyEntries

    @historyEntries.setter
    def historyEntries(self, value: list[dict]):
        self._historyEntries = value
        self.historyEntriesUpdated.emit()
        self.historyEntriesChanged.emit(value)

    @property
    def jishoHistoryEntries(self) -> list[dict]:
        if self._jishoHistoryEntries is None:
            raise ValueError("Jisho history entries not set.")
        return self._jishoHistoryEntries

    @jishoHistoryEntries.setter
    def jishoHistoryEntries(self, value: list[dict]):
        self._jishoHistoryEntries = value
        self.jishoHistoryEntriesUpdated.emit()
        self.jishoHistoryEntriesChanged.emit(value)

    @property
    def jishoSearchWords(self) -> dict[str, list[int]]:
        if self._jishoSearchWords is None:
            raise ValueError("Jisho search words not set.")
        return self._jishoSearchWords
    
    @jishoSearchWords.setter
    def jishoSearchWords(self, value: dict[str, list[int]]):
        self._jishoSearchWords = value
        self.jishoSearchWordsUpdated.emit()
        self.jishoSearchWordsChanged.emit(value)
    
    @property
    def wordDf(self) -> pd.DataFrame:
        if self._wordDf is None:
            raise ValueError("Word dataframe not set.")
        return self._wordDf
    
    @wordDf.setter
    def wordDf(self, value: pd.DataFrame):
        self._wordDf = value
        self.wordDfUpdated.emit()
        self.wordDfChanged.emit(value)

class HistoryInfoTab(QWidget):
    def __init__(self, mainWindow: MainWindow=None):
        self._mainWindow = mainWindow
        super().__init__(mainWindow)
        self.historyInfo = HistoryInfoObj(self)

        # Widgets
        self.calcHistoryInfoButton = QPushButton("Calc History")
        self.combiningHistoryProgress = QProgressBar(self)
        self.combiningHistoryProgress.hide()
        self.numHistoryPathsLabel = QLabel("History Paths: N/A")
        self.numHistoryEntriesLabel = QLabel("History Entries: N/A")
        self.numJishoRelatedEntriesLabel = QLabel("Jisho Related Entries: N/A")
        self.numSearchedWordsLabel = QLabel("Searched Words: N/A")
        self.wordTable = QTableWidget(self)
        self.currentSortColumn: int | None = None
        self.currentSortOrder: Qt.SortOrder | None = None

        # Signals
        self.calcHistoryInfoButton.clicked.connect(self.historyInfo.find_history_paths)
        self.historyInfo.combiningHistoryStart.connect(self.combiningHistoryProgress.show)
        self.historyInfo.combiningHistoryStart.connect(
            lambda total: self.combiningHistoryProgress.setMaximum(total)
        )
        self.historyInfo.combiningHistoryProgress.connect(
            lambda value: self.combiningHistoryProgress.setValue(value)
        )
        self.historyInfo.combiningHistoryFinish.connect(self.combiningHistoryProgress.hide)
        self.historyInfo.historyPathsUpdated.connect(
            lambda: self.numHistoryPathsLabel.setText(f"History Paths: {len(self.historyInfo.historyPaths)}")
        )
        self.historyInfo.historyEntriesUpdated.connect(
            lambda: self.numHistoryEntriesLabel.setText(f"History Entries: {len(self.historyInfo.historyEntries)}")
        )
        self.historyInfo.jishoHistoryEntriesUpdated.connect(
            lambda: self.numJishoRelatedEntriesLabel.setText(f"Jisho Related Entries: {len(self.historyInfo.jishoHistoryEntries)}")
        )
        self.historyInfo.jishoSearchWordsUpdated.connect(
            lambda: self.numSearchedWordsLabel.setText(f"Searched Words: {len(self.historyInfo.jishoSearchWords)}")
        )
        self.historyInfo.wordDfUpdated.connect(self.populate_table)
        self.wordTable.horizontalHeader().sectionClicked.connect(self.sort_table)

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        calcHistoryButtonRow = QHBoxLayout()
        self.calcHistoryInfoButton.setFixedWidth(200)
        self.combiningHistoryProgress.setFixedWidth(400)
        calcHistoryButtonRow.addWidget(self.calcHistoryInfoButton, stretch=0)
        calcHistoryButtonRow.addWidget(self.combiningHistoryProgress, stretch=0)
        calcHistoryButtonRow.addStretch(1)
        layout.addLayout(calcHistoryButtonRow, stretch=0)
        layout.addWidget(self.numHistoryPathsLabel, alignment=Qt.AlignmentFlag.AlignLeft, stretch=0)
        layout.addWidget(self.numHistoryEntriesLabel, alignment=Qt.AlignmentFlag.AlignLeft, stretch=0)
        layout.addWidget(self.numJishoRelatedEntriesLabel, alignment=Qt.AlignmentFlag.AlignLeft, stretch=0)
        layout.addWidget(self.numSearchedWordsLabel, alignment=Qt.AlignmentFlag.AlignLeft, stretch=0)
        layout.addWidget(self.wordTable, stretch=1)

    def populate_table(self):
        df = self.historyInfo.wordDf
        self.wordTable.setRowCount(df.shape[0])
        self.wordTable.setColumnCount(df.shape[1])
        self.wordTable.setHorizontalHeaderLabels(df.columns)
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                val = df.iloc[i, j]
                if type(val) is np.int64:
                    val = f"{int(val):02d}"
                elif type(val) is str:
                    pass
                else:
                    raise TypeError(f"Unsupported type: {type(val)}")
                item = QTableWidgetItem(val)
                self.wordTable.setItem(i, j, item)
        self.wordTable.resizeColumnsToContents()

    def sort_table(self, column: int):
        if self.currentSortColumn is None or self.currentSortColumn != column:
            self.currentSortColumn = column
            self.currentSortOrder = Qt.SortOrder.AscendingOrder
        elif self.currentSortOrder == Qt.SortOrder.AscendingOrder:
            self.currentSortOrder = Qt.SortOrder.DescendingOrder
        else:
            self.currentSortOrder = Qt.SortOrder.AscendingOrder
        self.wordTable.sortItems(column, self.currentSortOrder)

    def start(self):
        pass
