import sys
from string import ascii_uppercase

import itertools
from typing import Dict, List

from openpyxl import Workbook
from terminaltables import AsciiTable

from main import models
from main import solver

Timetable = Dict[models.Subject, List[int]]

def timetable_to_workbook(timetable: Timetable, sheet_name: str = 'Timetable', periods_per_day: int = 4):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    for subject in timetable:
        for period in timetable[subject]:
            # TODO: error when some period is out of bounds (e.g. period 200 when there are just 4 periods / day)
            # since everything is zero-indexed, floor division by the number of periods in a day gives us the day to
            # which the period belongs, # i.e. for 4 periods in a day 0-3 -> day 0 (Monday) , 4-7 -> day 1 (Tuesday)...
            # and the modulo by four gives the period in that day
            day = period // periods_per_day
            period_in_day = period % periods_per_day

            cell = ws['{}{}'.format(ascii_uppercase[day], period_in_day + 1)]
            cell.value = (cell.value or '') + subject.name + '\n'

    return wb


def timetable_dict_to_ascii_table(timetable: Timetable) -> str:
    flat_timetable = list(itertools.repeat('', 20))
    for subject, periods in timetable.items():
        for period in periods:
            flat_timetable[period] += (subject.name + '\n')
    square_timetable = list(zip(*[flat_timetable[i:i + 4] for i in range(0, len(flat_timetable), 4)]))

    return AsciiTable(
        [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']] + square_timetable
    ).table


def main():
    ds = models.Datastore(sys.argv[1])
    students = list(ds.get_students().values())

    tt = solver.possible_timetables(students, 20)
    timetable_to_workbook(next(tt)).save('out.xlsx')

if __name__ == '__main__':
    main()
