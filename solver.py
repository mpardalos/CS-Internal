import pprint
from collections import namedtuple

import itertools
from ortools.constraint_solver import pywrapcp

# periods is an int for how many periods per week are required for this subject
Subject = namedtuple("subject", ['name', 'periods'])

class Student:
    def __init__(self, subjects):
        self.subjects = subjects
        self.periods = list(itertools.chain(*[
            ['{}-p{}'.format(subject.name, period_num)
                for period_num in range(1, subject.periods+1)]
                for subject in subjects]))


def solve(students: list, subjects: list, max_students_per_class: int, periods_per_week: int):
    """
    Create a timetable for the given number of periods, subjects, and students per subject
    
    Args:
        periods_per_week (int): The number of periods in the whole timetable
        subjects ([str]): The subjects that should appear on the timetable
        max_students_per_class (int): The number of students per class
    """
    solver = pywrapcp.Solver("timetable")

    periods = {
        '{}-p{}'.format(subject.name, i): solver.IntVar(1, periods_per_week, '{}-p{}'.format(subject.name, i))
        for subject in subjects
        for i in range(1, subject.periods+1)
    }

    for student in students:
        student_periods = [periods[period_name] for period_name in student.periods]
        solver.AddConstraint(solver.AllDifferent(student_periods))

    db = solver.Phase(list(periods.values()),
                      solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
                      solver.ASSIGN_CENTER_VALUE)
    solver.NewSearch(db)
    solver.NextSolution()

    pprint.pprint(periods)

# Test data
periods_per_week = 20
HistorySL = Subject("HistorySL", 2)
HistoryHL = Subject("HistoryHL", 3)
MathSL = Subject("MathSL", 2)
MathHL = Subject("MathHL", 3)
BiologySL = Subject("BiologySL", 2)
BiologyHL = Subject("BiologyHL", 3)

subjects = [
    HistorySL,
    HistoryHL,
    MathSL,
    MathHL,
    BiologySL,
    BiologyHL
]

students = [
    Student([HistorySL, MathHL]),
    Student([BiologySL, HistoryHL]),
    Student([MathSL, BiologyHL]),
    Student([HistorySL, BiologyHL]),
]

max_students_per_class = 14

solve(students, subjects, max_students_per_class, periods_per_week)
