import json
import os
from datetime import datetime

REVIEWS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "reviews.json")

def _load_reviews():
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_reviews(reviews):
    os.makedirs(os.path.dirname(REVIEWS_FILE), exist_ok=True)
    with open(REVIEWS_FILE, "w") as f:
        json.dump(reviews, f, indent=2)

def add_review(course_id, professor, rating, comment, author="Anonymous"):
    reviews = _load_reviews()
    key = course_id.strip()
    if key not in reviews:
        reviews[key] = []
    reviews[key].append({
        "professor": professor,
        "rating": int(rating),
        "comment": comment,
        "author": author,
        "date": datetime.now().strftime("%B %d, %Y")
    })
    _save_reviews(reviews)
    return reviews[key]

def get_reviews(course_id):
    reviews = _load_reviews()
    return reviews.get(course_id.strip(), [])

def get_all_reviews():
    return _load_reviews()

def get_average_rating(course_id):
    reviews = get_reviews(course_id)
    if not reviews:
        return None
    return round(sum(r["rating"] for r in reviews) / len(reviews), 1)