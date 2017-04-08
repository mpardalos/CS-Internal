import itertools
import sys
from collections import defaultdict
from typing import List, Iterator, Dict

from ortools.constraint_solver import pywrapcp

from timetable_plus import models, views
from timetable_plus.models import Subject, LoadingError


def possible_timetables(students: List[List[Subject]], periods_per_week: int) -> \
        Iterator[Dict[Subject, List[int]]]:
    """
    Yield possible timetables
    
    Args:
        students: a list of tuples of Subjects, one for each student, containing that
        student's Subjects
        periods_per_week: The number of periods in the whole timetable

    Returns:
        A generator that yields possible timetables in the form of dicts mapping subject
        names to the position in the timetable that they should occupy}
    """
    solver = pywrapcp.Solver("timetable")

    # Flatten the list that contains each student's subjects and remove duplicates
    subjects = set(itertools.chain(*students))

    # Get the list of all the periods for all subjects
    period_names = itertools.chain(*[subject.period_names for subject in subjects])

    # Generate a dict of period_name:period_variable
    # We need a dict to be able to access each period's variable by name
    period_variables = {period_name: solver.IntVar(0, periods_per_week - 1, period_name)
                        for period_name in period_names}

    for student in students:
        # Get the list of all the periods for the student's subjects
        student_period_names = list(
            itertools.chain(*[subject.period_names for subject in student])
        )

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
        subject_map = defaultdict(list)
        for period_name, period_variable in period_variables.items():
            for subject in subjects:
                if period_name in subject.period_names:
                    subject_map[subject].append(period_variable.Value())

        yield subject_map


def main():
    try:
        ds = models.Datastore(sys.argv[1])
        students = list(ds.get_students().values())
    except LoadingError as e:
        print(f'Loading Error in cell {e.cell.coordinate}: {str(e)}')
    else:
        result = next(possible_timetables(students, 20))
        print(views.timetable_dict_to_ascii_table(result))


if __name__ == '__main__':
    main()
