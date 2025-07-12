from typing import Any
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer

class BufferedDataTable(QTableWidget):
    def __init__(
        self, parent: QWidget | None=None,
        tableMaxNewRowsPerStep: int=5000,
        tableUpdateDelay: float=1.0
    ):
        super().__init__(parent)
        self._dataBuffer: list[dict[str, Any]] = []
        self._tableMaxNewRowsPerStep: int = tableMaxNewRowsPerStep
        self._tableUpdateDelay = tableUpdateDelay
        self._tableUpdateScheduledTimer = QTimer(self)
        self._tableUpdateScheduledTimer.setInterval(int(self._tableUpdateDelay * 1000))
        self._tableUpdateScheduledTimer.timeout.connect(self._on_table_update_timer_timeout)
        
        self._sortLocked: bool = True
        self._currentSortColumn: int | None = None
        self._currentSortOrder: Qt.SortOrder | None = None

        # Signals
        self.horizontalHeader().sectionClicked.connect(self._sort_table)

    def add_data_to_buffer(self, data: dict[str, Any]):
        self._dataBuffer.append(data)
        if not self._tableUpdateScheduledTimer.isActive():
            self._tableUpdateScheduledTimer.start()

    def _on_table_update_timer_timeout(self):
        self._update_table()
        if len(self._dataBuffer) == 0:
            self._tableUpdateScheduledTimer.stop()

    def _update_table(self):
        if len(self._dataBuffer) == 0:
            return

        _dataList: list[dict] = []
        for i in range(self._tableMaxNewRowsPerStep):
            if len(self._dataBuffer) == 0:
                break
            _data = self._dataBuffer.pop(0)
            _dataList.append(_data)

        if self.rowCount() == 0:
            self.setColumnCount(len(_dataList[0]))
            self.setHorizontalHeaderLabels(list(_dataList[0].keys()))

        scrollToBottomFlag = self.verticalScrollBar().value() \
            == self.verticalScrollBar().maximum()

        for _data in _dataList:
            row = self.rowCount()
            self.insertRow(row)
            for col, val in enumerate(_data.values()):
                if type(val) is int:
                    val = f"{val:05d}"
                item = QTableWidgetItem(str(val))
                self.setItem(row, col, item)

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        # Scroll to bottom if was already scrolled to bottom
        if scrollToBottomFlag:
            self.scrollToBottom()

    def _sort_table(self, column: int):
        if self._sortLocked:
            return
        if self._currentSortColumn is None or self._currentSortColumn != column:
            self._currentSortColumn = column
            self._currentSortOrder = Qt.SortOrder.AscendingOrder
        elif self._currentSortOrder == Qt.SortOrder.AscendingOrder:
            self._currentSortOrder = Qt.SortOrder.DescendingOrder
        else:
            self._currentSortOrder = Qt.SortOrder.AscendingOrder
        self.sortItems(column, self._currentSortOrder)
