import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QWidget
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QTableWidgetItem

import main.models
from main import models
from main import solver
from main.models import Subject
MainWindowUI = uic.loadUiType(os.path.join('main', 'ui', 'main.ui'))[0]
SubjectListWidgetUI = uic.loadUiType(os.path.join('main', 'ui', 'subject_list_widget.ui'))[0]
TimetableDialogUI = uic.loadUiType(os.path.join('main', 'ui', 'timetable_dialog.ui'))[0]


class MainWindow(QMainWindow, MainWindowUI):
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # Populate subject list
        with open(sys.argv[1]) as fp:
            for subject in main.models.Subject.subjects_from_json_store(fp):
                item = QListWidgetItem()
                widget = SubjectListWidget(subject, self.listWidget)
                item.setSizeHint(widget.sizeHint())
                self.listWidget.addItem(item)
                self.listWidget.setItemWidget(item, widget)

        # bind handlers
        self.actionQuit.triggered.connect(self.close)
        self.actionGenerateTable.triggered.connect(lambda: self.showNewTimetable(sys.argv[1]))

    def showNewTimetable(self, data_file_location):
        """
        Open a dialog to show a possible timetable for the the subjects and students in :param: data_file_location
        """
        dialog = QDialog(self)
        dialog.ui = TimetableDialogUI()
        dialog.ui.setupUi(dialog)

        with open(data_file_location) as f:
            result = next(solver.possible_timetables(models.students_from_json_store(f), 20))
        square_timetable = solver.solution_to_square_timetable(result)

        for row_index, row in enumerate(square_timetable):
            for column_index, period_name in enumerate(row):
                dialog.ui.timetableWidget.setItem(row_index, column_index, QTableWidgetItem(period_name))

        dialog.exec_()
        dialog.show()


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
