from collections import namedtuple

from past import autotranslate
# python-constraint is python2, so we'll use python-future's autotranslate function
autotranslate(['constraint'])
import constraint

# periods is an int for how many periods per week are required for this subject
subject = namedtuple("subject", ['name', 'periods'])


def solve(subjects: list, max_students_per_class: int, periods_per_week: int):
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




# Test data
periods_per_week = 20
HistorySL = subject("HistorySL", 2)
HistoryHL = subject("HistoryHL", 3)
MathSL = subject("MathSL", 2)
MathHL = subject("MathHL", 3)
BiologySL = subject("BiologySL", 2)
BiologyHL = subject("BiologyHL", 3)

subjects = [
    HistorySL,
    HistoryHL,
    MathSL,
    MathHL,
    BiologySL,
    BiologyHL
]

max_students_per_class = 14

solve(subjects, max_students_per_class, periods_per_week)
