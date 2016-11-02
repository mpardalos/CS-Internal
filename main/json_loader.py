import itertools
import json
from collections import defaultdict
from typing import List, TextIO

from main.models import Subject


def students_from_json_store(fp: IO) -> List:
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


def subjects_from_json_store(fp: TextIO) -> List:
    data = json.load(fp)
    subjects = [Subject(name, 3 if 'HL' in name else 2, students) for name, students in data.items()]
    return subjects
