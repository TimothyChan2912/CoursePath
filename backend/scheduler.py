from collections import defaultdict, deque
from backend.catalog import COURSE_CATALOG, REQUIRED_COURSES, ELECTIVE_COURSES, get_prerequisites

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

    # Determine which required courses are still needed
    remaining_required = [c for c in REQUIRED_COURSES if c not in completed]

    # Determine eligible electives (not taken, prerequisites met or will be met)
    all_remaining = list(remaining_required)
    if include_electives:
        for e in ELECTIVE_COURSES:
            if e not in completed:
                all_remaining.append(e)

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

            prereqs = COURSE_CATALOG.get(course, {}).get("prerequisites", [])
            if all(p in scheduled for p in prereqs):
                semester_courses.append(course)
            else:
                still_remaining.append(course)

        for c in semester_courses:
            scheduled.add(c)

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
            prereqs = COURSE_CATALOG.get(course, {}).get("prerequisites", [])
            if all(p in scheduled for p in prereqs):
                semester_courses.append(course)
            else:
                still_remaining.append(course)
        for c in semester_courses:
            scheduled.add(c)
        semesters.append({
            "label": f"Semester {num_semesters + extra}",
            "courses": [_course_detail(c) for c in semester_courses]
        })
        remaining = still_remaining
        extra += 1
        if extra > 10:  # Safety break
            break

    return semesters


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