import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from main import models
from main import solver
from main import views

MainWindowUI = uic.loadUiType(os.path.join('main', 'ui', 'main.ui'))[0]


class MainWindow(QMainWindow, MainWindowUI):
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)

        self.setupUi(self)
        self.setWindowTitle('Choose Students file')

        self.write_button.setEnabled(False)

        self.open_button.clicked.connect(self.get_file_to_open)
        self.write_button.clicked.connect(self.generate_timetable)

        self.input_file_name = ''

    def get_file_to_open(self):
        # noinspection PyCallByClass,PyArgumentList
        self.input_file_name, _ = QFileDialog.getOpenFileName(self, 'Choose File to Open', os.path.expanduser('~'))
        if self.input_file_name != '':
            self.statusbar.showMessage('Opened {}'.format(self.input_file_name))
            self.write_button.setEnabled(True)

    def generate_timetable(self):
        # noinspection PyCallByClass,PyArgumentList
        output_filename, _ = QFileDialog.getSaveFileName(self, 'Choose File to Save to', os.path.expanduser('~'))

        ds = models.Datastore(self.input_file_name)
        students = list(ds.get_students().values())

        tt = solver.possible_timetables(students, 20)
        views.timetable_to_workbook(next(tt)).save(output_filename)

        self.statusbar.showMessage('Saved to {}'.format(output_filename))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
