import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
import random
    
def extract_coid(li):
    a_tag = li.find('a')
    if not a_tag:
        return None
    
    onclick = a_tag.get('onclick', '')
    match = re.search(r"showCourse\('\d+',\s*'(\d+)'", onclick)

    if match:
        return match.group(1)
    return None

def scrape_course_list(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.select("a[onclick^='showCourse']")
    print(f"Found {len(links)} links")

    coids = []

    for a in links:
        onclick = a.get("onclick", "")
        print(f"onclick: {onclick}")  
        match = re.search(r"showCourse\('\d+',\s*'(\d+)'", onclick)
        if match:
            coids.append(match.group(1))

    print("Found COIDs:", coids) 
    return coids

def fetch_course_details(coid):
    url = f"https://catalog.sjsu.edu/preview_course_nopop.php?catoid=17&coid={coid}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_course_id(text):
    match = re.search(r'[A-Z]{2,4}\s?\d+[A-Z]*', text)
    if match:
        return match.group().replace(' ', '')
    else:
        return None
    
def extract_prereqs(text):
    match = re.search(r"Prerequisite\(s\)?:?(.*?)(Corequisite|Grading|$)", text)
    if not match:
        return []
    
    prereq_text = match.group(1)
    conditions = re.split(r'\s*(?:and|or)\s*', prereq_text, flags=re.IGNORECASE)

    courses = []

    for condition in conditions:
        found_courses = re.findall(r"[A-Z]{2,4}\s?\d+[A-Z]*", condition)
        courses.extend(found_courses)

    return list({course.replace(' ', '') for course in courses})

def extract_coreqs(text):
    match = re.search(r"Corequisite\(s\)?:?(.*?)(Prerequisite|Grading|$)", text)
    if not match:
        return []
    
    coreq_text = match.group(1)
    conditions = re.split(r'\s*(?:and|or)\s*', coreq_text, flags=re.IGNORECASE)

    courses = []

    for condition in conditions:
        found_courses = re.findall(r"[A-Z]{2,4}\s?\d+[A-Z]*", condition)
        courses.extend(found_courses)

    return list({course.replace(' ', '') for course in courses})

def extract_units(text):
    match = re.search(r"(\d+)\s*unit", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def extract_description(text):
    match = re.search(
        r"\d+\s*unit\(s\)\s*(.*?)\s*(?:Prerequisite|Satisfies|Grading|$)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if match:
        return match.group(1).strip()
    return None

def parse_course_block(soup):    
    title_tag = soup.find("h1", id="course_preview_title")

    if not title_tag:
        return None
    
    title = clean_text(title_tag.get_text(strip=True))
    text = clean_text(soup.get_text(' ', strip=True))

    course_id = extract_course_id(title)
    prereqs = extract_prereqs(text)

    return {
        'course_id': course_id,
        'title': title,
        'description': extract_description(text),
        'prerequisites': prereqs,
        'corequisites': extract_coreqs(text),
        'units': extract_units(text)
    }

def scrape_courses(url, limit=None):
    coids = scrape_course_list(url)

    if limit:
        coids = coids[:limit]

    catalog = []

    for coid in coids:
        soup = fetch_course_details(coid)
        parsed = parse_course_block(soup)

        if parsed and parsed["course_id"]:
            catalog.append(parsed)

        time_delay = random.uniform(5, 10)
        time.sleep(time_delay)

    return catalog

def save_catalog(data):
    with open('catalog.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    url = 'https://catalog.sjsu.edu/preview_entity.php?catoid=17&ent_oid=2335#'
    data = scrape_courses(url)
    save_catalog(data)

