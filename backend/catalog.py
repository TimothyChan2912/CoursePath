import json
import os
import re

COURSE_CATALOG = {
    # Lower Division Core
    "CS 22A": {
        "name": "Python for Programmers",
        "units": 3,
        "description": "Object-oriented programming with Python. Problem solving, algorithms, data structures.",
        "prerequisites": [],
        "category": "Lower Division Core",
        "ge": False
    },
    "CS 46A": {
        "name": "Introduction to Programming",
        "units": 3,
        "description": "Introduction to object-oriented programming using Java. Variables, control flow, classes.",
        "prerequisites": [],
        "category": "Lower Division Core",
        "ge": False
    },
    "CS 46B": {
        "name": "Introduction to Data Structures",
        "units": 3,
        "description": "Abstract data types, linked lists, stacks, queues, trees, recursion.",
        "prerequisites": ["CS 46A"],
        "category": "Lower Division Core",
        "ge": False
    },
    "CS 47": {
        "name": "Introduction to Computer Systems",
        "units": 3,
        "description": "Computer organization, assembly language, memory hierarchy.",
        "prerequisites": ["CS 46A"],
        "category": "Lower Division Core",
        "ge": False
    },
    "CS 49J": {
        "name": "Programming in Java",
        "units": 3,
        "description": "Object-oriented programming in Java for students with prior programming experience.",
        "prerequisites": [],
        "category": "Lower Division Core",
        "ge": False
    },
    "MATH 30": {
        "name": "Calculus I",
        "units": 3,
        "description": "Limits, derivatives, integrals, and the fundamental theorem of calculus.",
        "prerequisites": [],
        "category": "Math",
        "ge": False
    },
    "MATH 31": {
        "name": "Calculus II",
        "units": 3,
        "description": "Integration techniques, sequences, series, polar coordinates.",
        "prerequisites": ["MATH 30"],
        "category": "Math",
        "ge": False
    },
    "MATH 42": {
        "name": "Discrete Mathematics",
        "units": 3,
        "description": "Logic, sets, proofs, combinatorics, graph theory.",
        "prerequisites": ["MATH 30"],
        "category": "Math",
        "ge": False
    },
    "MATH 161A": {
        "name": "Applied Probability and Statistics I",
        "units": 3,
        "description": "Probability, random variables, distributions, statistical inference.",
        "prerequisites": ["MATH 31"],
        "category": "Math",
        "ge": False
    },
    # Upper Division Core
    "CS 146": {
        "name": "Data Structures and Algorithms",
        "units": 3,
        "description": "Advanced data structures, algorithm analysis, sorting, searching, graph algorithms.",
        "prerequisites": ["CS 46B", "MATH 42"],
        "category": "Upper Division Core",
        "ge": False
    },
    "CS 147": {
        "name": "Computer Architecture",
        "units": 3,
        "description": "Processor design, pipeline, memory systems, I/O.",
        "prerequisites": ["CS 47"],
        "category": "Upper Division Core",
        "ge": False
    },
    "CS 149": {
        "name": "Operating Systems",
        "units": 3,
        "description": "Processes, threads, scheduling, memory management, file systems.",
        "prerequisites": ["CS 146", "CS 147"],
        "category": "Upper Division Core",
        "ge": False
    },
    "CS 151": {
        "name": "Object-Oriented Design",
        "units": 3,
        "description": "Design patterns, UML, SOLID principles, refactoring.",
        "prerequisites": ["CS 146"],
        "category": "Upper Division Core",
        "ge": False
    },
    "CS 152": {
        "name": "Programming Paradigms",
        "units": 3,
        "description": "Functional, logic, and object-oriented programming. Language design.",
        "prerequisites": ["CS 146"],
        "category": "Upper Division Core",
        "ge": False
    },
    "CS 154": {
        "name": "Theory of Computation",
        "units": 3,
        "description": "Automata, formal languages, Turing machines, complexity theory.",
        "prerequisites": ["CS 146", "MATH 42"],
        "category": "Upper Division Core",
        "ge": False
    },
    "CS 157A": {
        "name": "Introduction to Database Management Systems",
        "units": 3,
        "description": "Relational model, SQL, normalization, transactions.",
        "prerequisites": ["CS 146"],
        "category": "Upper Division Core",
        "ge": False
    },
    "CS 160": {
        "name": "Software Engineering",
        "units": 3,
        "description": "Software development process, requirements, design, testing, project management.",
        "prerequisites": ["CS 151"],
        "category": "Upper Division Core",
        "ge": False
    },
    "CS 166": {
        "name": "Information Security",
        "units": 3,
        "description": "Cryptography, network security, authentication, security protocols.",
        "prerequisites": ["CS 146"],
        "category": "Upper Division Core",
        "ge": False
    },
    # Electives
    "CS 171": {
        "name": "Artificial Intelligence",
        "units": 3,
        "description": "Search, knowledge representation, machine learning, natural language processing.",
        "prerequisites": ["CS 146", "MATH 42"],
        "category": "Elective",
        "ge": False
    },
    "CS 175": {
        "name": "Computer Graphics",
        "units": 3,
        "description": "2D/3D graphics, rendering, shading, animation.",
        "prerequisites": ["CS 146", "MATH 31"],
        "category": "Elective",
        "ge": False
    },
    "CS 176": {
        "name": "Computer Vision",
        "units": 3,
        "description": "Image processing, feature detection, deep learning for vision.",
        "prerequisites": ["CS 146", "MATH 161A"],
        "category": "Elective",
        "ge": False
    },
    "CS 179": {
        "name": "Machine Learning",
        "units": 3,
        "description": "Supervised and unsupervised learning, neural networks, evaluation.",
        "prerequisites": ["CS 146", "MATH 161A"],
        "category": "Elective",
        "ge": False
    },
    "CS 185C": {
        "name": "Topics in Artificial Intelligence: NLP",
        "units": 3,
        "description": "Natural language processing, transformers, text classification.",
        "prerequisites": ["CS 179"],
        "category": "Elective",
        "ge": False
    },
    "CS 168": {
        "name": "Internet and Cloud Computing",
        "units": 3,
        "description": "Cloud architecture, distributed systems, containerization.",
        "prerequisites": ["CS 149"],
        "category": "Elective",
        "ge": False
    },
    "CS 174": {
        "name": "Mobile Software Engineering",
        "units": 3,
        "description": "Mobile app development for iOS and Android.",
        "prerequisites": ["CS 151"],
        "category": "Elective",
        "ge": False
    },
    "CS 157B": {
        "name": "Advanced Topics in Database Management",
        "units": 3,
        "description": "NoSQL databases, distributed databases, query optimization.",
        "prerequisites": ["CS 157A"],
        "category": "Elective",
        "ge": False
    },
    "CS 158A": {
        "name": "Computer Networks",
        "units": 3,
        "description": "Network protocols, TCP/IP, routing, network programming.",
        "prerequisites": ["CS 149"],
        "category": "Elective",
        "ge": False
    },
    "CS 165": {
        "name": "Programming Language Design",
        "units": 3,
        "description": "Language specification, compilers, interpreters.",
        "prerequisites": ["CS 152", "CS 154"],
        "category": "Elective",
        "ge": False
    },
    "CS 195": {
        "name": "Senior Project I",
        "units": 3,
        "description": "Capstone project planning, requirements, initial implementation.",
        "prerequisites": ["CS 160"],
        "category": "Senior Project",
        "ge": False
    },
    "CS 196": {
        "name": "Senior Project II",
        "units": 3,
        "description": "Capstone project completion, presentation.",
        "prerequisites": ["CS 195"],
        "category": "Senior Project",
        "ge": False
    },
}

# Required courses for CS degree (ordered by dependency)
REQUIRED_COURSES = [
    "CS 46A", "CS 46B", "CS 47",
    "CS 146", "CS 147", "CS 149",
    "CS 151", "CS 152", "CS 154",
    "CS 157A", "CS 160", "CS 166",
]

LOWER_DIVISION_CORE_COURSES = ["CS 46A", "CS 46B", "CS 47"]
UPPER_DIVISION_CORE_COURSES = [c for c in REQUIRED_COURSES if c not in LOWER_DIVISION_CORE_COURSES]

# Requirement group: complete one of these
REQUIRED_EITHER_ONE_OF = [
    ("CS 49C", "CS 49J"),
]

# At least one course is required from this list.
MAJOR_ELECTIVE_COURSES = [
    "CS 122", "CS 123A", "CS 123B", "CS 131", "CS 132",
    "CS 133", "CS 134", "CS 136", "CS 144", "CS 153",
    "CS 155", "CS 156", "CS 157B", "CS 157C", "CS 158B",
    "CS 159", "CS 161", "CS 168", "CS 171", "CS 174",
    "CS 175", "CS 176",
]

UPPER_DIVISION_ELECTIVE_COURSES = [
    "CS 108", "CS 136", "CS 143C", "CS 143M",
    "CS 180", "CS 180H", "CS 185A", "CS 185C",
    "CS 190", "CS 190I",
]

LOWER_DIVISION_ELECTIVE_COURSES = [
    "CS 48", "CS 85A", "CS 85C", "CS 49C", "CS 49J",
]

MATH_ELECTIVE_COURSES = [
    "MATH 142", "MATH 161A", "MATH 162", "MATH 177",
    "MATH 178", "MATH 179", "MATH 203",
]

_ALL_ELECTIVES = (
    MAJOR_ELECTIVE_COURSES
    + UPPER_DIVISION_ELECTIVE_COURSES
    + LOWER_DIVISION_ELECTIVE_COURSES
    + MATH_ELECTIVE_COURSES
)
ELECTIVE_COURSES = list(dict.fromkeys(_ALL_ELECTIVES))

CS_ELECTIVE_UNITS_REQUIRED = 14


def _normalize_course_id(raw_course_id):
    if not raw_course_id:
        return raw_course_id
    compact = str(raw_course_id).strip().replace(" ", "")
    match = re.match(r"^([A-Za-z]+)(.+)$", compact)
    if not match:
        return compact.upper()
    return f"{match.group(1).upper()} {match.group(2).upper()}"


def _title_to_name(title):
    if not title:
        return "Unknown Course"
    parts = str(title).split(" - ", 1)
    return parts[1].strip() if len(parts) == 2 else str(title).strip()


def _classify_course_category(course_id, fallback_category):
    if course_id in LOWER_DIVISION_CORE_COURSES:
        return "Lower Division Core"
    if course_id in UPPER_DIVISION_CORE_COURSES:
        return "Upper Division Core"
    if course_id in MAJOR_ELECTIVE_COURSES:
        return "Major Elective"
    if course_id in UPPER_DIVISION_ELECTIVE_COURSES:
        return "Upper Division Elective"
    if course_id in LOWER_DIVISION_ELECTIVE_COURSES:
        return "Lower Division Elective"
    if course_id in MATH_ELECTIVE_COURSES:
        return "Mathematics Elective"
    return fallback_category or "Catalog"


def _load_catalog_from_json():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "catalog.json")
    try:
        with open(data_path, "r", encoding="utf-8") as catalog_file:
            raw_courses = json.load(catalog_file)
    except (OSError, json.JSONDecodeError):
        return COURSE_CATALOG

    loaded_catalog = {}
    for raw_course in raw_courses:
        if not isinstance(raw_course, dict):
            continue
        course_id = _normalize_course_id(raw_course.get("course_id"))
        if not course_id:
            continue

        loaded_catalog[course_id] = {
            "name": _title_to_name(raw_course.get("title")),
            "units": raw_course.get("units", 0),
            "description": raw_course.get("description", ""),
            "prerequisites": [
                _normalize_course_id(prereq) for prereq in raw_course.get("prerequisites", [])
            ],
            "category": _classify_course_category(course_id, raw_course.get("category")),
            "ge": bool(raw_course.get("ge", False)),
        }

    return loaded_catalog or COURSE_CATALOG


COURSE_CATALOG = _load_catalog_from_json()

# Courses required before others (graph)
def get_prerequisites(course_id):
    return COURSE_CATALOG.get(course_id, {}).get("prerequisites", [])

def get_course_info(course_id):
    return COURSE_CATALOG.get(course_id, None)
