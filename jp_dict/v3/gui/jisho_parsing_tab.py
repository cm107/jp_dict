from __future__ import annotations
from dataclasses import dataclass
import enum
import os
from typing import TYPE_CHECKING
import multiprocessing as mp
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, \
    QTabWidget, QTabBar, QProgressBar, QTableWidget, QTableWidgetItem, \
    QTableView, QTableWidgetSelectionRange, QCheckBox, \
    QDialog, QDialogButtonBox
from PyQt5.QtCore import Qt, pyqtSignal, pyqtBoundSignal, \
    QObject, QThread, QThreadPool, QRunnable, QTimer

from ..serializable_obj import SettingsObj
from .widgets.data_table import BufferedDataTable
from ...parsing.jisho.jisho_structs import JishoSearchHtmlParser, JishoSearchQuery
from .gui_settings import guiSettings
if TYPE_CHECKING:
    from .main_window import MainWindow

@dataclass
class JishoParsingSettings(SettingsObj):
    skipContentForExisting: bool = False

    def save_to_meta(self):
        self.save(guiSettings.jishoParsingSettingsPath)
        assert os.path.isfile(guiSettings.jishoParsingSettingsPath)
    
    @classmethod
    def load_from_meta(cls):
        if not os.path.isfile(guiSettings.jishoParsingSettingsPath):
            return cls()
        return cls.load(guiSettings.jishoParsingSettingsPath)

class JishoParsingSettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None=None):
        super().__init__(parent)

        # Widgets
        self.skipContentForExisting = QCheckBox(
            "Skip content for existing entries",
            self
        )
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self
        )

        # Signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.rejected.connect(self.reject)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.skipContentForExisting)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        # Start
        self.load()

    def get_data(self) -> JishoParsingSettings:
        return JishoParsingSettings(
            skipContentForExisting=self.skipContentForExisting.isChecked()
        )
    
    def apply_data(self, data: JishoParsingSettings):
        self.skipContentForExisting.setChecked(data.skipContentForExisting)
    
    def save(self):
        self.get_data().save_to_meta()
    
    def load(self):
        self.apply_data(JishoParsingSettings.load_from_meta())

class JishoParsingThread(QThread): # Single thread implementation
    def __init__(
        self,
        jishoParsingData: JishoParsingData,
        words: list[tuple[int, str]],
        dumpDir: str
    ):
        self._jishoParsingData = jishoParsingData
        super().__init__(jishoParsingData)
        self.words: list[tuple[int, str]] = words
        self.dumpDir = dumpDir

    def run(self):
        data = self._jishoParsingData

        os.makedirs(self.dumpDir, exist_ok=True)
        data.jishoParsingStarted.emit(len(self.words))
        for i, (id, word) in enumerate(self.words):
            data.jishoParsingWord.emit(word)

            wordStatus: JishoParsedWordStatus = None
            savePath = f"{self.dumpDir}/{word}.json"
            if not os.path.isfile(savePath):
                url = f"https://jisho.org/search/{word}"
                parser = JishoSearchHtmlParser(url=url)
                try:
                    searchQuery = parser.parse(history_group_id=id)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Failed to parse: {word}")
                    print(f"Refer to: {url}")
                    raise
                searchQuery.save_to_path(savePath, overwrite=True)
                data.jishoWordSaved.emit(savePath)
                wordStatus = JishoParsedWordStatus.NEW
            else:
                searchQuery: JishoSearchQuery = JishoSearchQuery.load_from_path(savePath)
                assert searchQuery.history_group_id == id, \
                    f"history_group_id mismatch: {searchQuery.history_group_id} != {id}"
                wordStatus = JishoParsedWordStatus.EXISTING

            data.jishoParsedWordAndStatus.emit(searchQuery, wordStatus)
            data.jishoParsedWord.emit(searchQuery)
            data.jishoParsingProgress.emit(i+1)
        data.jishoParsingFinished.emit()

class JishoParsingTask(QRunnable):
    def __init__(
        self, id: int, word: str, dumpDir: str,
        savedSignal: pyqtBoundSignal,
        parsedWordAndStatusSignal: pyqtBoundSignal,
        parsedWordSignal: pyqtBoundSignal,
        taskFinishedSignal: pyqtBoundSignal
    ):
        super().__init__()
        self.id = id
        self.word = word
        self.dumpDir = dumpDir

        self.savedSignal = savedSignal
        self.parsedWordAndStatusSignal = parsedWordAndStatusSignal
        self.parsedWordSignal = parsedWordSignal
        self.progressSignal = taskFinishedSignal
    
    def run(self):
        wordStatus: JishoParsedWordStatus = None
        savePath = f"{self.dumpDir}/{self.word}.json"
        if not os.path.isfile(savePath):
            url = f"https://jisho.org/search/{self.word}"
            parser = JishoSearchHtmlParser(url=url)
            try:
                searchQuery = parser.parse(history_group_id=self.id)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Failed to parse: {self.word}")
                print(f"Refer to: {url}")
                raise
            searchQuery.save_to_path(savePath, overwrite=True)
            self.savedSignal.emit(savePath)
            wordStatus = JishoParsedWordStatus.NEW
        else:
            searchQuery: JishoSearchQuery = JishoSearchQuery.load_from_path(savePath)
            assert searchQuery.history_group_id == self.id, \
                f"history_group_id mismatch: {searchQuery.history_group_id} != {self.id}"
            wordStatus = JishoParsedWordStatus.EXISTING
        
        self.parsedWordAndStatusSignal.emit(searchQuery, wordStatus)
        self.parsedWordSignal.emit(searchQuery)
        self.progressSignal.emit()

class JishoParsingTaskManager(QObject): # Parallel implementation
    taskFinished = pyqtSignal()
    busySignalChanged = pyqtSignal(bool)
    def __init__(self, jishoParsingData: JishoParsingData):
        self._jishoParsingData = jishoParsingData
        super().__init__(jishoParsingData)

        self.finishedTaskCount: int | None = None
        self.nTasks: int | None = None
        self._isBusy: bool = False
        self.taskFinished.connect(self.on_task_finished)

    @property
    def isBusy(self):
        return self._isBusy
    
    @isBusy.setter
    def isBusy(self, value: bool):
        if self._isBusy != value:
            self._isBusy = value
            self.busySignalChanged.emit(self._isBusy)

    def start_tasks(self, words: list[tuple[int, str]], dumpDir: str):
        self.isBusy = True
        self._jishoParsingData.jishoParsingStarted.emit(len(words))
        pool = QThreadPool.globalInstance()
        assert pool is not None
        nThreads = min(mp.cpu_count() - 2, 5)
        pool.setMaxThreadCount(nThreads)
        tasks: list[JishoParsingTask] = []
        for i, (id, word) in enumerate(words):
            task = JishoParsingTask(
                id=id,
                word=word,
                dumpDir=dumpDir,
                savedSignal=self._jishoParsingData.jishoWordSaved,
                parsedWordAndStatusSignal=self._jishoParsingData.jishoParsedWordAndStatus,
                parsedWordSignal=self._jishoParsingData.jishoParsedWord,
                taskFinishedSignal=self.taskFinished
            )
            tasks.append(task)
        
        self.nTasks = len(tasks)
        self.finishedTaskCount = 0
        for i, task in enumerate(tasks):
            pool.start(task)
    
    def on_task_finished(self):
        self.finishedTaskCount += 1
        self._jishoParsingData.jishoParsingProgress.emit(self.finishedTaskCount)
        if self.finishedTaskCount == self.nTasks:
            self._jishoParsingData.jishoParsingFinished.emit()
            self.isBusy = False

class JishoParsedWordStatus(enum.Enum):
    EXISTING = 0
    NEW = 1

class JishoParsingData(QObject):
    jishoParsingStarted = pyqtSignal(int)
    jishoParsingWord = pyqtSignal(str)
    jishoParsedWord = pyqtSignal(JishoSearchQuery)
    jishoParsedWordAndStatus = pyqtSignal(JishoSearchQuery, JishoParsedWordStatus)
    jishoWordSaved = pyqtSignal(str)
    jishoParsingProgress = pyqtSignal(int)
    jishoParsingFinished = pyqtSignal()

    parsedSearchQueriesUpdated = pyqtSignal()
    parsedSearchQueriesChanged = pyqtSignal(list)
    def __init__(self, jishoParsingTab: JishoParsingTab):
        self._jishoParsingTab = jishoParsingTab
        self._parsedSearchQueries: list[JishoSearchQuery] | None = None
        self._parsingThread: JishoParsingThread | None = None
        self._parsingTaskManager: JishoParsingTaskManager | None = None
        super().__init__(jishoParsingTab)

        self.jishoParsedWord.connect(self.add_parsed_search_query)

    @property
    def parsedSearchQueries(self):
        return self._parsedSearchQueries

    def parse_jisho_data(self):
        jishoSearchWords = self._jishoParsingTab._mainWindow.historyInfoTab.historyInfo.jishoSearchWords
        words = [
            (min(usec_times), word)
            for word, usec_times in jishoSearchWords.items()
        ]
        thread = JishoParsingThread(
            jishoParsingData=self,
            words=words,
            dumpDir=guiSettings.jishoDataDir
        )
        thread.started.connect(self._jishoParsingTab.parseJishoButton.setEnabled(False))
        thread.finished.connect(self._jishoParsingTab.parseJishoButton.setEnabled(True))
        thread.start()
        thread.finished.connect(thread.deleteLater)
        self._parsingThread = thread
    
    def parse_jisho_data_in_parallel(self):
        jishoSearchWords = self._jishoParsingTab._mainWindow.historyInfoTab.historyInfo.jishoSearchWords
        words = [
            (min(usec_times), word)
            for word, usec_times in jishoSearchWords.items()
        ]
        self._parsingTaskManager = JishoParsingTaskManager(self)
        self._parsingTaskManager.busySignalChanged.connect(
            lambda isBusy: self._jishoParsingTab.parseJishoButton.setEnabled(not isBusy)
        )
        self._parsingTaskManager.start_tasks(words, guiSettings.jishoDataDir)

    def add_parsed_search_query(self, searchQuery: JishoSearchQuery):
        if self._parsedSearchQueries is None:
            self._parsedSearchQueries = []
        self._parsedSearchQueries.append(searchQuery)
        self.parsedSearchQueriesUpdated.emit()
        self.parsedSearchQueriesChanged.emit(self._parsedSearchQueries)

class JishoParsingTab(QWidget):
    settingsUpdated = pyqtSignal()
    settingsChanged = pyqtSignal(JishoParsingSettings)

    def __init__(self, mainWindow: MainWindow=None):
        self._mainWindow = mainWindow
        super().__init__(mainWindow)
        self.data = JishoParsingData(self)

        # Widgets
        self.parseJishoButton = QPushButton("Parse Jisho Data")
        self.parseJishoProgress = QProgressBar(self)
        self.parseJishoProgress.hide()
        self.numParsedJishoWordsLabel = QLabel("Number of Parsed Jisho Words: N/A")
        self.jishoParseTable = BufferedDataTable(
            self, tableMaxNewRowsPerStep=5000, tableUpdateDelay=3.0
        )

        # Signals
        self.parseJishoButton.setEnabled(False)
        self._mainWindow.historyInfoTab.historyInfo.jishoSearchWordsUpdated.connect(
            lambda: self.parseJishoButton.setEnabled(
                self._mainWindow.historyInfoTab.historyInfo.jishoSearchWords is not None
                and len(self._mainWindow.historyInfoTab.historyInfo.jishoSearchWords) > 0
            )
        )
        self.parseJishoButton.clicked.connect(self.data.parse_jisho_data_in_parallel)
        self.data.jishoParsingStarted.connect(self.parseJishoProgress.show)
        self.data.jishoParsingStarted.connect(
            lambda total: self.parseJishoProgress.setMaximum(total)
        )
        self.data.jishoParsingProgress.connect(
            lambda value: self.parseJishoProgress.setValue(value)
        )
        self.data.jishoParsingFinished.connect(self.parseJishoProgress.hide)
        self.data.jishoParsingStarted.connect(
            lambda: self.jishoParseTable.clearContents()
        )
        self.data.jishoParsedWordAndStatus.connect(self.add_query_to_table)
        self.data.parsedSearchQueriesUpdated.connect(
            lambda: self.numParsedJishoWordsLabel.setText(
                f"Number of Parsed Jisho Words: {len(self.data.parsedSearchQueries)}"
            )
        )
        self.data.jishoParsingFinished.connect(self.on_finished_parsing)

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        parseButtonRow = QHBoxLayout()
        self.parseJishoButton.setFixedWidth(200)
        self.parseJishoProgress.setFixedWidth(400)
        parseButtonRow.addWidget(self.parseJishoButton, stretch=0)
        parseButtonRow.addWidget(self.parseJishoProgress, stretch=0)
        parseButtonRow.addStretch(1)
        layout.addLayout(parseButtonRow, stretch=0)
        layout.addWidget(self.numParsedJishoWordsLabel, alignment=Qt.AlignmentFlag.AlignLeft, stretch=0)
        layout.addWidget(self.jishoParseTable, stretch=1)

    @property
    def settings(self) -> JishoParsingSettings:
        return JishoParsingSettings.load_from_meta()

    def add_query_to_table(self, searchQuery: JishoSearchQuery, wordStatus: JishoParsedWordStatus):
        s = self.settings
        _data = {}
        _data['ID'] = searchQuery.history_group_id
        _data['Title'] = searchQuery.title
        _data['Exact Matches'] = len(searchQuery.exact_matches)
        _data['Nonexact Matches'] = len(searchQuery.nonexact_matches)
        _data['Result Count'] = searchQuery.result_count
        if s.skipContentForExisting and wordStatus == JishoParsedWordStatus.EXISTING:
            _data['Contents'] = "(Skipped existing)"
        elif len(searchQuery.nonexact_matches) == 0 and len(searchQuery.exact_matches) == 0:
            _data['Contents'] = "None"
        elif len(searchQuery.exact_matches) == 1:
            _data['Contents'] = searchQuery.exact_matches[0].custom_str(indent=0)
        else:
            _data['Contents'] = '(omitted)'

        self.jishoParseTable.add_data_to_buffer(_data)

    def on_finished_parsing(self):
        self.jishoParseTable._sortLocked = False
        self.jishoParseTable._sort_table(0)

    def open_settings_dialog(self):
        dialog = JishoParsingSettingsDialog(self)
        ret = dialog.exec()
        if ret == QDialog.DialogCode.Accepted:
            self.settingsUpdated.emit()
            self.settingsChanged.emit(self.settings)
