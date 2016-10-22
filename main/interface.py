import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem

from main import json_loader
MainWindowUI = uic.loadUiType(os.path.join('main', 'ui', 'main.ui'))[0]


class MainWindow(QMainWindow, MainWindowUI):
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # Populate subject list
        with open(sys.argv[1]) as fp:
            for subject in json_loader.subjects_from_json_store(fp):
                self.listWidget.addItem(QListWidgetItem(subject, self.listWidget))

        # bind handlers
        self.actionQuit.triggered.connect(self.close)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
