import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from main import models
from main import solver
from main import views

MainWindowUI = uic.loadUiType(os.path.join('main', 'ui', 'main.ui'))[0]


class MainWindow(QMainWindow, MainWindowUI):
    # whether to include the teachers when generating the timetable.
    # WARNING: takes an *extremely* long time
    include_teachers = False
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)

        self.setupUi(self)
        self.setWindowTitle('Choose Students file')

        self.write_button.setEnabled(False)

        self.open_button.clicked.connect(self.get_file_to_open)
        self.write_button.clicked.connect(self.generate_timetable)

        self.datastore = None

    def get_file_to_open(self):
        # noinspection PyCallByClass,PyArgumentList
        self.input_file_name, _ = QFileDialog.getOpenFileName(self, 'Choose File to Open', os.path.expanduser('~'))
        if self.input_file_name != '':
            try:
                self.datastore = models.Datastore(self.input_file_name)
            except models.LoadingError as e:
                # noinspection PyArgumentList
                QMessageBox.critical(self, 'Invalid input file',
                                     'The file you selected had an error in cell {cell}: {msg}'
                                     .format(cell=e.cell.coordinate, msg=e))
            else:
                self.statusbar.showMessage('Opened {}'.format(self.input_file_name))
                self.write_button.setEnabled(True)


    def generate_timetable(self):
        # noinspection PyCallByClass,PyArgumentList
        output_filename, _ = QFileDialog.getSaveFileName(self, 'Choose File to Save to', os.path.expanduser('~'))

        students = list(self.datastore.get_students(self.include_teachers).values())

        tt = solver.possible_timetables(students, 20)
        views.timetable_to_workbook(next(tt)).save(output_filename)

        self.statusbar.showMessage('Saved to {}'.format(output_filename))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
