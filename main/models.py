import itertools
import json
from collections import defaultdict
from typing import List, TextIO


class Subject:
    def __init__(self, name: str, periods_per_week: int, student_names: List[str]) -> None:
        self.name = name
        self.periods_per_week = periods_per_week
        self.period_names = ['{}-p{}'.format(name, i) 
                for i in range(1, periods_per_week+1)]
        self.student_names = student_names
        
    def __eq__(self, other):
        return isinstance(other, type(self)) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "Subject: {}".format(self.name)

    @staticmethod
    def subjects_from_json_store(fp: TextIO) -> List:
        data = json.load(fp)
        subjects = [Subject(name, 3 if 'HL' in name else 2, students) for name, students in data.items()]
        return subjects


def students_from_json_store(fp: TextIO) -> List:
    """
    Create a list of students and their subjects from a json file containing an object of the form:
    {
        subject_name: [student1, student2, ...]
    }

    Args:
        fp: the file from which to load the data
    """
    # The json input is subjects mapped to their students
    subjects = json.load(fp)

    # Invert the json input, from map of subjects -> student to one of students -> subjects
    student_names = set(itertools.chain(*subjects.values()))

    students = defaultdict(list)  # type: defaultdict[str, List[Subject]]
    for subject_name, subject_students in subjects.items():
        for student_name in student_names:
            if student_name in subject_students:
                students[student_name].append(Subject(subject_name, 3 if 'HL' in subject_name else 2))

    return list(students.values())


