import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

MainWindowUI = uic.loadUiType(os.path.join('ui', 'main.ui'))[0]


class MainWindow(QMainWindow, MainWindowUI):
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # bind handlers
        self.actionQuit.triggered.connect(self.close)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
