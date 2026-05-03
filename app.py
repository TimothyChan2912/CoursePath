from flask import Flask, render_template, request, jsonify
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.parser import process_pdf
from backend.scheduler import generate_schedule, get_missing_prerequisites
from backend.reviews import add_review, get_reviews, get_all_reviews, get_average_rating
from backend.ai_assistant import get_system_prompt
from backend.catalog import COURSE_CATALOG

# Uses Flask defaults: templates/ and static/ relative to app.py
app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

sessions = {}

# ─── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# ─── Upload & Parse Transcript ────────────────────────────────────────────────

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        courses = process_pdf(filepath)
    except Exception as e:
        return jsonify({"error": f"Failed to parse PDF: {str(e)}"}), 500

    schedule = generate_schedule(courses, num_semesters=4, courses_per_semester=4)
    eligible_now = get_missing_prerequisites(courses)

    return jsonify({
        "courses": courses,
        "schedule": schedule,
        "eligible_now": eligible_now[:6]
    })

# ─── Manual Schedule Generation ───────────────────────────────────────────────

@app.route("/schedule", methods=["POST"])
def get_schedule():
    data = request.get_json()
    completed = data.get("completed", [])
    semesters = data.get("semesters", 4)
    per_sem = data.get("per_semester", 4)

    schedule = generate_schedule(completed, num_semesters=semesters, courses_per_semester=per_sem)
    eligible_now = get_missing_prerequisites(completed)

    return jsonify({
        "schedule": schedule,
        "eligible_now": eligible_now[:6]
    })

# ─── Course Catalog ────────────────────────────────────────────────────────────

@app.route("/catalog", methods=["GET"])
def get_catalog():
    catalog_list = []
    for cid, info in COURSE_CATALOG.items():
        avg = get_average_rating(cid)
        reviews = get_reviews(cid)
        catalog_list.append({
            "id": cid,
            "name": info["name"],
            "units": info["units"],
            "description": info["description"],
            "prerequisites": info["prerequisites"],
            "category": info["category"],
            "avg_rating": avg,
            "review_count": len(reviews)
        })
    return jsonify({"catalog": catalog_list})

# ─── Reviews ──────────────────────────────────────────────────────────────────

@app.route("/reviews/<course_id>", methods=["GET"])
def get_course_reviews(course_id):
    reviews = get_reviews(course_id)
    avg = get_average_rating(course_id)
    return jsonify({"reviews": reviews, "average": avg})

@app.route("/reviews", methods=["POST"])
def post_review():
    data = request.get_json()
    required = ["course_id", "professor", "rating", "comment"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    rating = int(data["rating"])
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be 1-5"}), 400

    reviews = add_review(
        course_id=data["course_id"],
        professor=data["professor"],
        rating=rating,
        comment=data["comment"],
        author=data.get("author", "Anonymous")
    )
    return jsonify({"success": True, "reviews": reviews})

# ─── AI Chat ──────────────────────────────────────────────────────────────────

@app.route("/chat/system-prompt", methods=["POST"])
def chat_system_prompt():
    data = request.get_json() or {}
    completed = data.get("completed_courses", [])
    system_prompt = get_system_prompt(completed if completed else None)
    return jsonify({"system_prompt": system_prompt})

if __name__ == "__main__":
    app.run(debug=True, port=5000)