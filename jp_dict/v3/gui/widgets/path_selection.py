from abc import abstractmethod
import os
from PyQt5.QtWidgets import QWidget, QFileDialog, QPushButton, QLabel, \
    QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

class PathSelectButton(QWidget):
    pathUpdated = pyqtSignal()
    pathChanged = pyqtSignal(str)
    def __init__(
        self, parent: QWidget | None=None,
        showFullPath: bool=False,
        buttonText: str="Select Path",
        emptyLabel: str="No Path Selected"
    ):
        super().__init__(parent)
        
        # Flags
        self._emptyLabel = emptyLabel
        self._showFullPath = showFullPath

        # State
        self._path: str | None = None

        # Widgets
        self.button = QPushButton(buttonText, self)
        self.label = QLabel(self)
        self._update_label()
        
        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.button, stretch=0)
        layout.addWidget(self.label, stretch=1)
        self.setLayout(layout)

        # Signals
        self.button.clicked.connect(self.select_path)
        self.pathUpdated.connect(self._update_label)

    @property
    def path(self) -> str | None:
        return self._path

    @path.setter
    def path(self, path: str | None):
        if self._path != path:
            self._path = path
            self.pathUpdated.emit()
            self.pathChanged.emit(path)

    def _update_label(self):
        if self.path is None:
            self.label.setText(self._emptyLabel)
            self.label.setStyleSheet("color: gray;")
        else:
            self.label.setText(
                self.path
                if self._showFullPath
                else os.path.basename(self.path)
            )
            self.label.setStyleSheet("color: black;")

    @abstractmethod
    def open_dialog(self) -> str | None:
        raise NotImplementedError

    def select_path(self):
        # path = QFileDialog.getExistingDirectory(self, "Select Directory")
        path = self.open_dialog()
        if path == '':
            path = None
        self.path = path

class FileSelectButton(PathSelectButton):
    def __init__(
        self, parent: QWidget | None=None,
        showFullPath: bool=False,
        buttonText: str="Select File",
        emptyLabel: str="No File Selected"
    ):
        super().__init__(parent, showFullPath, buttonText, emptyLabel)

    def open_dialog(self):
        startDir = os.path.dirname(self.path) \
            if self.path is not None else os.getcwd()
        return QFileDialog.getOpenFileName(
            self, "Select File",
            directory=startDir
        )[0]

class DirectorySelectButton(PathSelectButton):
    def __init__(
        self, parent: QWidget | None=None,
        showFullPath: bool=False,
        buttonText: str="Select Directory",
        emptyLabel: str="No Directory Selected"
    ):
        super().__init__(parent, showFullPath, buttonText, emptyLabel)

    def open_dialog(self):
        startDir = os.path.dirname(self.path) \
            if self.path is not None else os.getcwd()
        return QFileDialog.getExistingDirectory(
            self, "Select Directory",
            directory=startDir
        )

class SaveFileSelectButton(FileSelectButton):
    def __init__(
        self, parent: QWidget | None=None,
        showFullPath: bool=False,
        buttonText: str="Select File Save",
        emptyLabel: str="No File Save Selected"
    ):
        super().__init__(parent, showFullPath, buttonText, emptyLabel)

    def open_dialog(self):
        return QFileDialog.getSaveFileName(self, "Select File Save")[0]
