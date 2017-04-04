import itertools
import sys
from collections import defaultdict
from typing import List, Sequence, Dict, Iterator

from openpyxl import load_workbook
from openpyxl.cell import Cell
from openpyxl.worksheet import Worksheet

# Dirty dirty (but awesome) hack for debugging
# e.g. the cell B4 containing 'test' would be repr'd as 'B4: test'
# noinspection PyUnresolvedReferences
Cell.__repr__ = lambda self: "{coords}: {value}".format(coords=self.coordinate, value=self.value)

def is_empty(cell: Cell):
    """
    Check whether an openpyxl Cell is empty
    Args: 
        cell: the Cell to check
    """
    return (cell.value or '').strip() == ''

def _find_in_cells(cells: Sequence[Cell], text: str) -> int:
    """
    Find the cell containing :param text: in :param cells:
    :return: the index of the cell found in :param cells: or -1 if it is not found
    """
    try:
        return next(col_cell_idx for col_cell_idx, col_cell in enumerate(cells) if
                    str(col_cell.value or '').lower().strip() == text.lower().strip())
    except StopIteration:
        return -1


class LoadingError(Exception):
    """
    Raised for problems in loading the xlsx file containing the students and subjects
    :argument problem_cell: the cell which caused the problem
    """

    def __init__(self, msg, cell: Cell = None):
        super().__init__(msg)
        self.cell = cell


class Datastore:
    student_list_start_row_index = 4

    def __init__(self, fp: str, worksheet_name='Classes'):
        self.worksheet = load_workbook(fp)[worksheet_name]  # type: Worksheet

        ending_column_index = 1
        for i, column in enumerate(self.worksheet.columns):
            if is_empty(column[0]):
                # if the two top cells are empty assume the rest of the column is too
                if is_empty(column[1]):
                    ending_column_index = i
                    break
                else:
                   raise LoadingError("Each subject must have a name", column[0])
        else:
            ending_column_index = i

        for column in list(self.worksheet.columns)[1:ending_column_index-1]:
            if column[1].value in ('', None):
                print(column[0])
                print(column[1])
                raise LoadingError("Each subject must have a teacher", column[1])
            if column[2].value in ('', None):
                raise LoadingError("Each subject must have a number of periods", column[2])


    def get_subjects(self) -> Iterator['Subject']:
        """
        Returns:
            All subject objects contained in the datastore
        """
        subject_name_row = list(self.worksheet.rows)[0][1:]  # type: List[Cell]
        columns = list(self.worksheet.columns)

        for cell in subject_name_row:
            column = columns[cell.col_idx - 1]

            name = column[0].value
            if name in ('', None):
                break

            teacher_name = (column[1].value or '').strip()
            if teacher_name == '':
                raise LoadingError('All subjects must have a teacher name', column[1])
            sl_periods_per_week = column[2].value
            extra_hl_periods_per_week = column[3].value or 0
            hl_marker_index = _find_in_cells(column, 'HL')
            # Index of the first empty cell after the students
            ending_marker_index = _find_in_cells(column[4:], '') + 4  
            # occurs if the empty cell is not in the cells returned by the library
            if ending_marker_index <= 4:  
                ending_marker_index = len(column)

            # If there is only one group in the subject
            if hl_marker_index == -1:
                students = [cell.value for cell in column[4:ending_marker_index] if
                        cell.value != None]
                if len(students) == 0:
                    continue
                yield Subject(name, sl_periods_per_week, teacher_name, students)
            # If there are both sl and hl students in the subject
            else:
                sl_students = [cell.value.strip() for cell in column[4:hl_marker_index]]
                hl_students = [cell.value.strip() for cell 
                               in column[hl_marker_index + 1:ending_marker_index]]
                if len(sl_students) == len(hl_students) == 0:
                    continue
                # common periods
                yield Subject(name + ' SL+HL', sl_periods_per_week, teacher_name, 
                        sl_students + hl_students)
                # extra hl periods
                yield Subject(name + ' HL', extra_hl_periods_per_week, teacher_name, 
                        hl_students)

    def get_students(self, include_teachers: bool = True) -> Dict[str, List['Subject']]:
        """
        Find which subjects each student has
        Args:
            include_teachers: if True, include teachers in the result, i.e. which subjects 
            each teacher teaches.

        Returns:
            A Dict, mapping student name -> list of subjects

        """
        subjects = list(self.get_subjects())

        student_names = list(set(itertools.chain(*(sub.student_names for sub in subjects))))
        if include_teachers:
            for sub in subjects:
                if sub.teacher_name not in student_names:
                    student_names.append(sub.teacher_name)

        students = defaultdict(list)  # type: defaultdict[str, List[Subject]]
        for subject in subjects:
            for student_name in student_names:
                if (student_name in subject.student_names or 
                        student_name == subject.teacher_name):
                    students[student_name].append(subject)

        return students


class Subject:
    def __init__(self, name: str, periods_per_week: int, teacher_name: str, 
            student_names: List[str]) -> None:
        self.name = name
        self.periods_per_week = periods_per_week
        self.period_names = ['{}-p{}'.format(name, i)
                             for i in range(1, periods_per_week + 1)]
        self.student_names = student_names
        self.teacher_name = teacher_name

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "Subject: {}".format(self.name)


def main():
    datastore = Datastore(sys.argv[1])
    for s in datastore.get_subjects():
        print(s)
        print([s.teacher_name] + list(s.student_names))

    print(datastore.get_students())

if __name__ == '__main__':
    main()
