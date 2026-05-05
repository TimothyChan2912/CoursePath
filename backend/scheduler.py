from collections import defaultdict, deque
from backend.catalog import (
    COURSE_CATALOG,
    REQUIRED_COURSES,
    REQUIRED_EITHER_ONE_OF,
    ELECTIVE_COURSES,
    MAJOR_ELECTIVE_COURSES,
    CS_ELECTIVE_UNITS_REQUIRED,
    get_prerequisites,
)

def topological_sort(courses_to_take, catalog):
    """
    Returns a topologically sorted list of courses respecting prerequisites.
    Uses Kahn's algorithm (BFS-based topological sort).
    """
    # Build adjacency and in-degree for the subgraph of needed courses
    needed = set(courses_to_take)
    in_degree = defaultdict(int)
    adj = defaultdict(list)

    for course in needed:
        prereqs = catalog.get(course, {}).get("prerequisites", [])
        for pre in prereqs:
            if pre in needed:
                adj[pre].append(course)
                in_degree[course] += 1

    # Initialize queue with courses that have no prerequisites (in this subgraph)
    queue = deque()
    for course in needed:
        if in_degree[course] == 0:
            queue.append(course)

    sorted_courses = []
    while queue:
        course = queue.popleft()
        sorted_courses.append(course)
        for neighbor in adj[course]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Handle any cycles (shouldn't occur in valid prerequisite chains)
    for course in needed:
        if course not in sorted_courses:
            sorted_courses.append(course)

    return sorted_courses


def generate_schedule(completed_courses, num_semesters=4, courses_per_semester=4, include_electives=True):
    """
    Given a list of completed courses, generate a recommended schedule
    for remaining required + elective courses.

    Returns a list of semesters, each containing a list of course dicts.
    """
    # Normalize completed course IDs (strip extra spaces)
    completed = set()

    for c in completed_courses:
        c_normalized = c.strip()
        completed.add(c_normalized)

    completed_elective_units = sum(
        COURSE_CATALOG.get(c, {}).get("units", 0)
        for c in completed
        if c in ELECTIVE_COURSES
    )
    remaining_elective_units = max(
        CS_ELECTIVE_UNITS_REQUIRED - completed_elective_units, 0
    )

    # Determine which required courses are still needed
    remaining_required = [c for c in REQUIRED_COURSES if c not in completed]
    remaining_required.extend(_pick_remaining_required_either_groups(completed))
    requirement_courses = set(remaining_required) | set(ELECTIVE_COURSES)

    all_remaining = list(remaining_required)

    # Topological sort of all remaining courses
    sorted_courses = topological_sort(all_remaining, COURSE_CATALOG)

    # Now greedily assign courses to semesters, respecting prerequisites
    semesters = []
    scheduled = set(completed)  # Start with already-completed courses

    remaining = list(sorted_courses)

    for sem_num in range(1, num_semesters + 1):
        semester_courses = []
        still_remaining = []

        for course in remaining:
            if len(semester_courses) >= courses_per_semester:
                still_remaining.append(course)
                continue

            if _prereqs_satisfied_for_plan(course, scheduled, requirement_courses):
                semester_courses.append(course)
            else:
                still_remaining.append(course)

        for c in semester_courses:
            scheduled.add(c)
        
        remaining_elective_units = _append_electives_for_semester(
            semester_courses, scheduled, remaining_elective_units, courses_per_semester, requirement_courses
        )

        semester_label = f"Semester {sem_num}"
        semesters.append({
            "label": semester_label,
            "courses": [_course_detail(c) for c in semester_courses]
        })

        remaining = still_remaining

        if not remaining:
            break

    # If courses remain after all semesters, add extra semesters
    extra = 1
    while remaining:
        semester_courses = []
        still_remaining = []
        for course in remaining:
            if len(semester_courses) >= courses_per_semester:
                still_remaining.append(course)
                continue
            if _prereqs_satisfied_for_plan(course, scheduled, requirement_courses):
                semester_courses.append(course)
            else:
                still_remaining.append(course)
        for c in semester_courses:
            scheduled.add(c)

        remaining_elective_units = _append_electives_for_semester(
            semester_courses, scheduled, remaining_elective_units, courses_per_semester, requirement_courses
        )

        semesters.append({
            "label": f"Semester {num_semesters + extra}",
            "courses": [_course_detail(c) for c in semester_courses]
        })
        remaining = still_remaining
        extra += 1
        if extra > 10:  # Safety break
            break

    return semesters


def _select_remaining_electives(completed):
    completed_elective_units = sum(
        COURSE_CATALOG.get(course_id, {}).get("units", 0)
        for course_id in completed
        if course_id in ELECTIVE_COURSES
    )
    units_needed = max(CS_ELECTIVE_UNITS_REQUIRED - completed_elective_units, 0)
    if units_needed == 0:
        return []

    selected = []
    selected_units = 0
    for course_id in ELECTIVE_COURSES:
        if course_id in completed:
            continue

        selected.append(course_id)
        selected_units += COURSE_CATALOG.get(course_id, {}).get("units", 3)
        if selected_units >= units_needed:
            break

    return selected


def _pick_remaining_required_either_groups(completed):
    selected = []
    for group in REQUIRED_EITHER_ONE_OF:
        if any(course in completed for course in group):
            continue
        selected.append(_best_course_from_group(group, completed))
    return selected


def _best_course_from_group(group, completed):
    best = None
    best_unmet = None
    for course_id in group:
        prereqs = COURSE_CATALOG.get(course_id, {}).get("prerequisites", [])
        unmet = sum(1 for prereq in prereqs if prereq not in completed)
        if best is None or unmet < best_unmet:
            best = course_id
            best_unmet = unmet
    return best


def _has_major_elective(course_ids):
    return any(course_id in MAJOR_ELECTIVE_COURSES for course_id in course_ids)


def _append_electives_for_semester(
    semester_courses, scheduled, remaining_units, courses_per_semester, requirement_courses
):
    if remaining_units <= 0 or len(semester_courses) >= courses_per_semester:
        return remaining_units

    needs_major_elective = not _has_major_elective(scheduled | set(semester_courses))
    candidate_pool = MAJOR_ELECTIVE_COURSES if needs_major_elective else ELECTIVE_COURSES

    for course in candidate_pool:
        if remaining_units <= 0 or len(semester_courses) >= courses_per_semester:
            break
        if course in scheduled or course in semester_courses:
            continue

        if not _prereqs_satisfied_for_plan(course, scheduled, requirement_courses):
            continue

        semester_courses.append(course)
        scheduled.add(course)
        remaining_units -= COURSE_CATALOG.get(course, {}).get("units", 3)

    return remaining_units


def _prereqs_satisfied_for_plan(course_id, scheduled, requirement_courses):
    prereqs = COURSE_CATALOG.get(course_id, {}).get("prerequisites", [])
    relevant_prereqs = [p for p in prereqs if p in requirement_courses]
    return all(prereq in scheduled for prereq in relevant_prereqs)


def _course_detail(course_id):
    info = COURSE_CATALOG.get(course_id, {})
    return {
        "id": course_id,
        "name": info.get("name", "Unknown Course"),
        "units": info.get("units", 3),
        "description": info.get("description", ""),
        "prerequisites": info.get("prerequisites", []),
        "category": info.get("category", "Elective")
    }


def get_missing_prerequisites(completed_courses):
    """
    Find courses the student could take next (all prereqs satisfied).
    """
    completed = set(c.strip() for c in completed_courses)
    eligible = []
    for course_id, info in COURSE_CATALOG.items():
        if course_id in completed:
            continue
        prereqs = info.get("prerequisites", [])
        if all(p in completed for p in prereqs):
            eligible.append(_course_detail(course_id))
    return eligible
