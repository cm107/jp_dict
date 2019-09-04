from qtpy.QtCore import QObject, Signal

class MyStream(QObject):
    message = Signal(str)
    def __init__(self, parent=None):
        super(MyStream, self).__init__(parent)

    def write(self, message):
        self.message.emit(str(message))