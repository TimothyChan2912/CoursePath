import json
import os
import re

# Required courses for CS degree (ordered by dependency)
REQUIRED_COURSES = [
    "CS 46A", "CS 46B", "CS 47",
    "CS 146", "CS 147", "CS 149",
    "CS 151", "CS 152", "CS 154",
    "CS 157A", "CS 160", "CS 166",
]

REQUIRED_EITHER_ONE_OF = [
    ("CS 49C", "CS 49J"),
]

LOWER_DIVISION_CORE_COURSES = ["CS 46A", "CS 46B", "CS 47"]
UPPER_DIVISION_CORE_COURSES = [c for c in REQUIRED_COURSES if c not in LOWER_DIVISION_CORE_COURSES]

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
    "CS 48", "CS 85A", "CS 85C",
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


_FALLBACK_CATALOG = {}


def _load_catalog_from_json():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "catalog.json")
    try:
        with open(data_path, "r", encoding="utf-8") as catalog_file:
            raw_courses = json.load(catalog_file)
    except (OSError, json.JSONDecodeError):
        return dict(_FALLBACK_CATALOG)

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

    return loaded_catalog if loaded_catalog else dict(_FALLBACK_CATALOG)


COURSE_CATALOG = _load_catalog_from_json()
