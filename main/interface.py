import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QWidget

from main.models import Subject
from main import json_loader
MainWindowUI = uic.loadUiType(os.path.join('main', 'ui', 'main.ui'))[0]
SubjectListWidgetUI = uic.loadUiType(os.path.join('main', 'ui', 'subject_list_widget.ui'))[0]


class MainWindow(QMainWindow, MainWindowUI):
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # Populate subject list
        with open(sys.argv[1]) as fp:
            for subject in json_loader.subjects_from_json_store(fp):
                item = QListWidgetItem()
                widget = SubjectListWidget(subject, self.listWidget)
                item.setSizeHint(widget.sizeHint())
                self.listWidget.addItem(item)
                self.listWidget.setItemWidget(item, widget)

        # bind handlers
        self.actionQuit.triggered.connect(self.close)


class SubjectListWidget(SubjectListWidgetUI, QWidget):
    def __init__(self, subject: Subject, parent: QWidget) -> None:
        super().__init__(parent)
        self.parent = parent
        self.subject = subject

        self.setupUi(self)
        self.subject_name_view.setText(subject.name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
