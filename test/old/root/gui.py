import sys
from qtpy.QtWidgets import QApplication
from src.gui.widgets.vocab_tracker_main_window import QVocabTracker

app = QApplication(sys.argv)
vocab_tracker = QVocabTracker(app)
vocab_tracker.show()
sys.exit(app.exec_())