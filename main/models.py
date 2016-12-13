import itertools
import sys
from collections import defaultdict
from pprint import pprint
from typing import List, Sequence, Dict, Iterator

from openpyxl import load_workbook
from openpyxl.cell import Cell
from openpyxl.worksheet import Worksheet

# Dirty dirty (but awesome) hack for debugging
# e.g. the cell B4 containing 'test' would be repr'd as 'B4: test'
# noinspection PyUnresolvedReferences
Cell.__repr__ = lambda self: "{coords}: {value}".format(coords=self.coordinate, value=self.value)


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


class Datastore:
    def __init__(self, fp: str, worksheet_name='Classes'):
        self.worksheet = load_workbook(fp)[worksheet_name]  # type: Worksheet

        # TODO: Add validation

    def get_subjects(self) -> Iterator['Subject']:
        subject_name_row = list(self.worksheet.rows)[0][1:]  # type: List[Cell]
        columns = list(self.worksheet.columns)

        for cell in subject_name_row:
            column = columns[cell.col_idx - 1]

            name = column[0].value
            if name == '' or name is None:
                break

            teacher_name = column[1].value

            sl_periods_per_week = column[2].value

            hl_periods_per_week = column[3].value

            # find index of the cell containing the text 'hl' and 'sl'
            sl_marker_index = _find_in_cells(column, 'sl')
            hl_marker_index = _find_in_cells(column, 'hl')
            ending_marker_index = _find_in_cells(column, '')  # TODO: handle early empty cell
            sl_students = [cell.value for cell in column[sl_marker_index + 1:hl_marker_index]]
            hl_students = [cell.value for cell in column[hl_marker_index + 1:ending_marker_index]]

            # SL
            yield Subject(name + ' SL', sl_periods_per_week, teacher_name, sl_students)
            # HL
            yield Subject(name + ' HL', hl_periods_per_week, teacher_name, hl_students)

    def get_students(self) -> Dict[str, List['Subject']]:
        subjects = self.get_subjects()
        subjects, subjects_copy = itertools.tee(subjects)

        student_names = set(itertools.chain(*(sub.student_names for sub in subjects_copy)))

        students = defaultdict(list)  # type: defaultdict[str, List[Subject]]
        for subject in subjects:
            for student_name in student_names:
                if student_name in subject.student_names:
                    students[student_name].append(subject)

        return students


class Subject:
    def __init__(self, name: str, periods_per_week: int, teacher_name: str, student_names: List[str] = None) -> None:
        self.name = name
        self.periods_per_week = periods_per_week
        self.period_names = ['{}-p{}'.format(name, i)
                             for i in range(1, periods_per_week + 1)]
        self.student_names = student_names or []
        self.teacher_name = teacher_name

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "Subject: {}".format(self.name)


if __name__ == '__main__':
    datastore = Datastore(sys.argv[1])
    for s in datastore.get_subjects():
        print(s)
        print([s.teacher_name] + s.student_names)

    pprint(datastore.get_students())