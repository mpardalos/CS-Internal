import pprint
from collections import namedtuple

import itertools
from ortools.constraint_solver import pywrapcp

class Subject:
    def __init__(self, name: str, periods_per_week: int):
        self.name = name
        self.periods_per_week = periods_per_week
        self.period_names = ['{}-p{}'.format(name, i) for i in range(1, periods_per_week+1)]
        
    def __eq__(self, other):
        return isinstance(other, type(self)) and self.name == other.name

    def __hash__(self):
        return hash(self.name)
        
def possible_timetables(students: list, periods_per_week: int):
    """
    Yield possible timetables
    
    Args:
        students: a list of tuples of Subjects, one for each student, containing that student's Subjects
        periods_per_week: The number of periods in the whole timetable

    Returns:
        A dict of {period name: the position in the timetable that the period should occupy}
    """
    solver = pywrapcp.Solver("timetable")

    # Flatten the list that contains each student's subjects and remove duplicates
    subjects = set(itertools.chain(*students))

    # Get the list of all the periods for all subjects
    period_names = itertools.chain(*[subject.period_names for subject in subjects])

    # Generate a dict of period_name:period_variable
    # We need a dict to be able to access each period's variable by name
    period_variables = {period_name: solver.IntVar(1, periods_per_week+1, period_name) 
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
        yield {period_name: period_variable.Value() for period_name, period_variable in period_variables.items()}


if __name__ == '__main__':
    # Test data
    periods_per_week = 20
    HistorySL = Subject("HistorySL", 2)
    HistoryHL = Subject("HistoryHL", 3)
    MathSL = Subject("MathSL", 2)
    MathHL = Subject("MathHL", 3)
    BiologySL = Subject("BiologySL", 2)
    BiologyHL = Subject("BiologyHL", 3)

    students = [
        (HistorySL, MathHL),
        (BiologySL, HistoryHL),
        (MathSL, BiologyHL),
        (HistorySL, BiologyHL)
    ]

    solutions = possible_timetables(students, periods_per_week)

    pprint.pprint(next(solutions))
