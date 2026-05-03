import json
from backend.catalog import COURSE_CATALOG, REQUIRED_COURSES, ELECTIVE_COURSES
from backend.reviews import get_all_reviews, get_average_rating

def build_context(completed_courses=None):
    """Build a knowledge context string from the course catalog and reviews."""
    lines = ["=== SJSU CS Degree Course Catalog ===\n"]

    for cid, info in COURSE_CATALOG.items():
        prereqs = ", ".join(info["prerequisites"]) if info["prerequisites"] else "None"
        avg = get_average_rating(cid)
        rating_str = f" | Avg Rating: {avg}/5" if avg else ""
        lines.append(
            f"{cid}: {info['name']} ({info['units']} units) | "
            f"Category: {info['category']} | "
            f"Prerequisites: {prereqs}{rating_str}\n"
            f"  Description: {info['description']}\n"
        )

    lines.append("\n=== Degree Requirements ===\n")
    lines.append("Required Courses: " + ", ".join(REQUIRED_COURSES) + "\n")
    lines.append("Available Electives: " + ", ".join(ELECTIVE_COURSES) + "\n")

    if completed_courses:
        lines.append("\n=== Student's Completed Courses ===\n")
        lines.append(", ".join(completed_courses) + "\n")

        remaining = [c for c in REQUIRED_COURSES if c not in set(completed_courses)]
        lines.append("\nRemaining Required: " + (", ".join(remaining) if remaining else "All complete!") + "\n")

    reviews = get_all_reviews()
    if reviews:
        lines.append("\n=== Course Reviews ===\n")
        for cid, revs in reviews.items():
            for r in revs[:3]:  # Limit to 3 reviews per course
                lines.append(f"{cid} - Prof. {r['professor']} ({r['rating']}/5): {r['comment']}\n")

    return "".join(lines)


def get_system_prompt(completed_courses=None):
    context = build_context(completed_courses)
    return f"""You are an enrollment assistant for SJSU's Computer Science department. 
You help students plan their schedules, understand prerequisites, and make informed course selections.

You have access to the following information:

{context}

Guidelines:
- Be helpful, friendly, and concise.
- Always reference specific course IDs (e.g., "CS 146") when discussing courses.
- When recommending courses, explain why based on the student's completed courses.
- If a student asks about prerequisites, be precise and accurate.
- Suggest electives that align with the student's apparent interests.
- Keep responses to 2-4 paragraphs unless a detailed breakdown is requested.
"""