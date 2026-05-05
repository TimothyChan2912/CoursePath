from flask import Flask, render_template, request, jsonify
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.parser import process_pdf
from backend.scheduler import generate_schedule, get_missing_prerequisites
from backend.reviews import add_review, get_reviews, get_all_reviews, get_average_rating
from backend.ai_assistant import get_system_prompt
from backend.catalog import COURSE_CATALOG

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

sessions = {}


@app.route("/")
def index():
    return render_template("index.html")


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

@app.route("/chat/system-prompt", methods=["POST"])
def chat_system_prompt():
    data = request.get_json() or {}
    completed = data.get("completed_courses", [])
    system_prompt = get_system_prompt(completed if completed else None)
    return jsonify({"system_prompt": system_prompt})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    completed = data.get("completed_courses", [])
    chat_history = data.get("chat_history", [])

    # Keep only expected role/content keys before sending to model backend.
    messages = []
    for item in chat_history:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str):
            messages.append({"role": role, "content": content})

    payload = {
        "model": os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        "stream": False,
        "messages": [
            {"role": "system", "content": get_system_prompt(completed if completed else None)},
            *messages,
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat"),
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError:
        return jsonify({
            "error": "Local model is unavailable. Start Ollama and pull a model (e.g. `ollama pull llama3.1:8b`)."
        }), 503
    except Exception:
        return jsonify({"error": "Failed to get response from local AI model."}), 500

    reply = (
        response_data.get("message", {}).get("content")
        if isinstance(response_data, dict) else None
    )
    if not reply:
        return jsonify({"error": "Local AI model returned an empty response."}), 502

    return jsonify({"reply": reply})


@app.route("/health/ai", methods=["GET"])
def ai_health():
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    tags_url = f"{ollama_base.rstrip('/')}/api/tags"
    req = urllib.request.Request(tags_url, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            tags_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError:
        return jsonify({
            "ready": False,
            "status": "offline",
            "message": "Ollama is not running",
            "model": model_name,
        }), 503
    except Exception:
        return jsonify({
            "ready": False,
            "status": "error",
            "message": "Could not verify Ollama status",
            "model": model_name,
        }), 500

    models = tags_data.get("models", []) if isinstance(tags_data, dict) else []
    available_names = {m.get("name") for m in models if isinstance(m, dict)}
    if model_name not in available_names:
        return jsonify({
            "ready": False,
            "status": "model_missing",
            "message": f"Model '{model_name}' not found locally",
            "model": model_name,
        }), 503

    return jsonify({
        "ready": True,
        "status": "ready",
        "message": "AI assistant is ready",
        "model": model_name,
    })

if __name__ == "__main__":
    app.run(debug=False, port=5000)