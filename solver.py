from collections import namedtuple

from past import autotranslate
# python-constraint is python2, so we'll use python-future's autotranslate function
autotranslate(['constraint'])
import constraint

# periods is an int for how many periods per week are required for this subject
Subject = namedtuple("subject", ['name', 'periods'])

class Student:
    def __init__(self, subjects):
        self.subjects = subjects
        self.periods = [
            ['{subject_name}-period{period_num}'.format(subject_name=Subject.name, period_num=period_num) for period_num in range(subject.periods)]
                for subject in subjects]


def solve(students: list, subjects: list, max_students_per_class: int, periods_per_week: int):
    """
    Create a timetable for the given number of periods, subjects, and students per subject
    
    Args:
        periods_per_week (int): The number of periods in the whole timetable
        subjects ([str]): The subjects that should appear on the timetable
        max_students_per_class (int): The number of students per class
    """

    problem = constraint.Problem()

    # Add one variable per subject period
    for subject in subjects:
        # Start numbering from 1
        for period_num in range(1, subject.periods+1):
            problem.addVariable('{subject_name}-period{period_num}'.format(subject_name=subject.name, period_num=period_num),
                                constraint.Domain(range(1, periods_per_week + 1)))

    # Each student is represented by a constraint that does not allow for his or her subjects to be on the same period
    for student in students:
        problem.addConstraint(constraint.AllDifferentConstraint(), student.periods)

    # TODO: Crashes because of py2/py3 incompatibility
    problem.getSolution()

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
