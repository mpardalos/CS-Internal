import os
import sys
import shutil

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from timetable_plus import models
from timetable_plus import solver
from timetable_plus import views

MainWindowUI = uic.loadUiType(os.path.join('timetable_plus', 'ui', 'main.ui'))[0]


class MainWindow(QMainWindow, MainWindowUI):
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)

        self.setupUi(self)
        self.setWindowTitle('Timetable+')

        self.write_button.setEnabled(False)

        self.open_button.clicked.connect(self.get_students)
        self.write_button.clicked.connect(self.generate_timetable)
        self.actionCreateTemplate.triggered.connect(self.create_template)

        self.students = []
        self.input_file_name = ''
        self.datastore = None

    def get_students(self):
        """
            Get the list of students from a user-selected file and store it in
            MainWindow.students
        """
        # noinspection PyCallByClass,PyArgumentList
        self.input_file_name, _ = QFileDialog.getOpenFileName(self, 'Choose File to Open',
                                                              os.path.expanduser('~'),
                                                              'Microsoft Excel Spreadsheet Files (*.xlsx)')
        if self.input_file_name != '':
            try:
                self.datastore = models.Datastore(self.input_file_name)
                self.students = list(self.datastore
                                     .get_students(self.actionIncludeTeachers.isChecked()).values())
            except models.LoadingError as e:
                # noinspection PyArgumentList
                if e.cell is not None:
                    QMessageBox.critical(self, 'Invalid input file',
                                         f'The file you selected had an error in cell {e.cell.coordinate}: {str(e)}'
                                         .format(cell=e.cell.coordinate, msg=e))
                else:
                    QMessageBox.critical(self, 'Invalid input file', f'The file you selected had an error: {str(e)}')
            else:
                self.statusbar.showMessage('Opened {}'.format(self.input_file_name))
                self.write_button.setEnabled(True)

    def generate_timetable(self):
        # noinspection PyCallByClass,PyArgumentList
        output_filename, _ = QFileDialog.getSaveFileName(self, 'Choose File to Save to',
                                                         os.path.join(os.path.expanduser('~'), 'timetable.xlsx'),
                                                         'Microsoft Excel Spreadsheet Files (*.xlsx);;All Files')

        if output_filename != '':
            self.statusbar.showMessage('Processing...')

            tt = solver.possible_timetables(self.students, 20)
            views.timetable_to_workbook(next(tt)).save(output_filename)

            self.statusbar.showMessage('Saved to {}'.format(output_filename))

    def create_template(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Choose File to Save template to',
                                                  os.path.join(os.path.expanduser('~'), 'template.xlsx'),
                                                  'Microsoft Excel Spreadsheet Files (*.xlsx);;All Files')

        if filename != '':
            shutil.copyfile(os.path.join('resources', 'template.xlsx'), filename)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
