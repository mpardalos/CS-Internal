import itertools
from itertools import repeat
from sys import argv
from typing import Sequence, Dict, Generator

from ortools.constraint_solver import pywrapcp
from terminaltables import AsciiTable

from main.models import Subject


def possible_timetables(students: Sequence[Sequence[Subject]], periods_per_week: int) -> Generator[
    Dict[str, int], None, None]:
    """
    Yield possible timetables
    
    Args:
        students: a list of tuples of Subjects, one for each student, containing that student's Subjects
        periods_per_week: The number of periods in the whole timetable

    Returns:
        A generator that yields possible timetables in the form of dicts mapping period names to the position
        in the timetable that they should occupy}
    """
    solver = pywrapcp.Solver("timetable")

    # Flatten the list that contains each student's subjects and remove duplicates
    subjects = set(itertools.chain(*students))

    # Get the list of all the periods for all subjects
    period_names = itertools.chain(*[subject.period_names for subject in subjects])

    # Generate a dict of period_name:period_variable
    # We need a dict to be able to access each period's variable by name
    period_variables = {period_name: solver.IntVar(1, periods_per_week, period_name)
                        for period_name in period_names}

    for student in students:
        # Get the list of all the periods for the student's subjects
        student_period_names = list(itertools.chain(*[subject.period_names for subject in student]))

        # Filter the list of all periods to get only those that the student is a part of
        student_period_variables = [
            period_var
            for period_name, period_var in period_variables.items()
            if period_name in student_period_names
            ]

        # All of the student's periods must be scheduled at different times
        solver.AddConstraint(solver.AllDifferent(student_period_variables))

    db = solver.Phase(list(period_variables.values()),
                      solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
                      solver.ASSIGN_CENTER_VALUE)
    solver.NewSearch(db)

    while solver.NextSolution():
        yield {
            period_name: period_variable.Value()
            for period_name, period_variable
            in period_variables.items()
            }


def timetable_dict_to_ascii_table(timetable_dict: Dict[str, int]) -> str:
    flat_timetable = list(repeat('', 20))
    for subject, period in timetable_dict.items():
        flat_timetable[period - 1] += (subject + '\n')

    # convert the flat list of periods into a 2D timetable
    square_timetable = list(zip(*[flat_timetable[i:i + 4] for i in range(0, len(flat_timetable), 4)]))
    return AsciiTable([['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']] + square_timetable).table


if __name__ == '__main__':
    with open(argv[1]) as f:
        # Get one possible timetable and print it
        result = next(possible_timetables(Subject.students_from_json_store(f), 20))
        print(timetable_dict_to_ascii_table(result))
