import argparse
import sys
from PyQt5.QtWidgets import QApplication
from ..gui.gui_settings import guiSettings
from ..gui.main_window import MainWindow

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--local',
        action='store_true',
        default=False
    )
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    guiSettings.metaDirIsLocal = args.local

    app = QApplication([])
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
