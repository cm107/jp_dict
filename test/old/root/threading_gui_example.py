# load modules
import time

# from PySide import QtCore, QtGui
from qtpy.QtCore import QThread
from qtpy.QtWidgets import QApplication


# APPLICATION STUFF
# -----------------

APP = QApplication([])


# THREADS
# -------


class WorkerThread(QThread):
    '''Does the work'''

    def __init__(self):
        super(WorkerThread, self).__init__()

        self.running = True

    def run(self):
        '''This starts the thread on the start() call'''

        # this goes over 1000 numbers, at 10 a second, will take
        # 100 seconds to complete, over a minute
        for i in range(1000):
            print(i)
            time.sleep(0.1)

        self.running = False


class BackgroundThread(QThread):
    '''Keeps the main loop responsive'''

    def __init__(self, worker):
        super(BackgroundThread, self).__init__()

        self.worker = worker

    def run(self):
        '''This starts the thread on the start() call'''

        while self.worker.running:
            APP.processEvents()
            print("Updating the main loop")
            time.sleep(0.1)

# MAIN
# ----

def main():
    # make threads
    worker = WorkerThread()
    background = BackgroundThread(worker)

    # start the threads
    worker.start()
    background.start()
    # wait until done
    worker.wait()

if __name__ == '__main__':
    main()