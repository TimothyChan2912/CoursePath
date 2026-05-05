import pdfplumber
import re

def extract_text(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text


def extract_courses(text):
    pattern = r"\b[A-Z]{2,4}\s?\d{2,3}[A-Z]?\b"
    return re.findall(pattern, text)

def clean_text(text):
    text = re.sub(r"(\d)([A-Z]{2,4})", r"\1 \2", text)
    text = re.sub(r"([A-Z])(\d)", r"\1 \2", text)
    return text

def clean_courses(courses):
    garbage_words = {"FALL", "SUMMER", "SPRING", "WINTER", "STER", "SION"}

    cleaned_courses = []
    for course in courses:
        if not any(word in course for word in garbage_words):
            cleaned_courses.append(course)

    return cleaned_courses

def process_pdf(pdf_path):
    text = extract_text(pdf_path)
    text = clean_text(text)        
    courses = extract_courses(text)
    cleaned_courses = clean_courses(courses)

    if "AP Calculus AB" in text:
        cleaned_courses.append("MATH 30")
    if "AP Computer Science A" in text:
        cleaned_courses.append("CS 46A")

    return cleaned_courses