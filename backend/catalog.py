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
    "MATH 30", "MATH 31", "MATH 42", "MATH 161A",
    "CS 146", "CS 147", "CS 149",
    "CS 151", "CS 152", "CS 154",
    "CS 157A", "CS 160", "CS 166",
    "CS 195", "CS 196"
]

ELECTIVE_COURSES = [
    "CS 171", "CS 175", "CS 176", "CS 179",
    "CS 185C", "CS 168", "CS 174", "CS 157B",
    "CS 158A", "CS 165"
]

# Courses required before others (graph)
def get_prerequisites(course_id):
    return COURSE_CATALOG.get(course_id, {}).get("prerequisites", [])

def get_course_info(course_id):
    return COURSE_CATALOG.get(course_id, None)