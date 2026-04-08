import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_rms.settings")
django.setup()

from core.models import Course, Semester, Subject

# List of courses based on user's request
course_data = [
    {
        "name": "Bachelor of Computer Applications",
        "code": "BCA",
        "duration": "3 Years",
        "description": "A 3-year undergraduate program focusing on computer applications, software development, and programming languages.",
        "semesters": {
            "Semester 1": ["Fundamentals of IT", "C Programming", "Discrete Mathematics"],
            "Semester 2": ["Data Structures", "Object Oriented Programming using C++", "Operating Systems"],
            "Semester 3": ["Database Management Systems", "Java Programming", "Computer Networks"],
            "Semester 4": ["Web Technology", "Software Engineering", "Python Programming"],
            "Semester 5": ["Cloud Computing", "Artificial Intelligence", "Mobile App Development"],
            "Semester 6": ["Major Project", "Cyber Security", "Data Science"]
        }
    },
    {
        "name": "Bachelor of Business Administration",
        "code": "BBA",
        "duration": "3 Years",
        "description": "A 3-year undergraduate program providing foundational knowledge in business and management principles.",
        "semesters": {
            "Semester 1": ["Principles of Management", "Business Economics", "Financial Accounting"],
            "Semester 2": ["Organizational Behavior", "Business Statistics", "Marketing Management"],
            "Semester 3": ["Human Resource Management", "Financial Management", "Business Law"],
            "Semester 4": ["Research Methodology", "Operations Management", "Taxation"],
            "Semester 5": ["Strategic Management", "International Business", "Entrepreneurship"],
            "Semester 6": ["Business Analytics", "Supply Chain Management", "Project Work"]
        }
    },
    {
        "name": "Master of Business Administration",
        "code": "MBA",
        "duration": "2 Years",
        "description": "A 2-year postgraduate program designed to develop leadership, management, and strategic thinking.",
        "semesters": {
            "Semester 1": ["Managerial Economics", "Organizational Behavior", "Accounting for Managers"],
            "Semester 2": ["Human Resource Management", "Financial Management", "Marketing Management"],
            "Semester 3": ["Strategic Management", "Business Ethics", "Elective 1", "Elective 2"],
            "Semester 4": ["International Business", "Project Management", "Major Project"]
        }
    },
    {
        "name": "Bachelor of Technology",
        "code": "BTech",
        "duration": "4 Years",
        "description": "A 4-year undergraduate engineering degree with specialized branches like Computer Science, Electronics, etc.",
        "semesters": {
            "Semester 1": ["Engineering Mathematics-I", "Engineering Physics", "Basics of Civil Engineering"],
            "Semester 2": ["Engineering Mathematics-II", "Engineering Chemistry", "Basics of Mechanical Engineering"],
            "Semester 3": ["Data Structures", "Digital Logic Design", "Object Oriented Programming"],
            "Semester 4": ["Operating Systems", "Computer Architecture", "Database Management Systems"],
            "Semester 5": ["Computer Networks", "Design and Analysis of Algorithms", "Theory of Computation"],
            "Semester 6": ["Software Engineering", "Web Technologies", "Compiler Design"],
            "Semester 7": ["Artificial Intelligence", "Cloud Computing", "Minor Project"],
            "Semester 8": ["Machine Learning", "Big Data Analytics", "Major Project"]
        }
    },
    {
        "name": "Master of Computer Applications",
        "code": "MCA",
        "duration": "2 Years",
        "description": "A 2-year postgraduate program for deeper understanding of software engineering, network systems, and advanced programming.",
        "semesters": {
            "Semester 1": ["Advanced Java", "Data Structures using C++", "Computer Networks"],
            "Semester 2": ["Advanced Database Management Systems", "Software Engineering", "Python Programming"],
            "Semester 3": ["Artificial Intelligence", "Cloud Computing", "Web Technologies"],
            "Semester 4": ["Machine Learning", "Mobile App Development", "Major Project"]
        }
    },
    {
        "name": "Diploma in Computer Applications",
        "code": "DCA",
        "duration": "1 Year",
        "description": "A 1-year diploma program providing essential computer skills and fundamental IT knowledge.",
        "semesters": {
            "Semester 1": ["Fundamentals of Computers", "Operating Systems", "PC Packages"],
            "Semester 2": ["Database Handling (MS Access)", "Internet & Web Designing", "FoxPro/Programming"]
        }
    },
    {
        "name": "Post Graduate Diploma in Computer Applications",
        "code": "PGDCA",
        "duration": "1 Year",
        "description": "A 1-year postgraduate diploma focusing on advanced computer applications, programming, and database.",
        "semesters": {
            "Semester 1": ["Fundamentals of IT", "Programming in C", "Database Management Systems"],
            "Semester 2": ["Object Oriented Programming with C++", "Web Designing", "System Analysis and Design"]
        }
    }
]

print("Starting to seed courses...")
# Create courses and subsequent semesters/subjects
for data in course_data:
    course, created = Course.objects.get_or_create(code=data["code"], defaults={
        "name": data["name"],
        "duration": data["duration"],
        "description": data["description"]
    })
    
    if not created:
        course.name = data["name"]
        course.duration = data["duration"]
        course.description = data["description"]
        course.save()
    
    for sem_name, subjects in data["semesters"].items():
        semester, sem_created = Semester.objects.get_or_create(course=course, name=sem_name)
        for i, subject_name in enumerate(subjects):
            code_prefix = course.code
            sem_num = sem_name[-1]
            sub_num = i + 1
            generated_code = f"{code_prefix}-{sem_num}0{sub_num}"
            
            # Check if subject exists in the semester, if not create it
            subject, sub_created = Subject.objects.get_or_create(semester=semester, name=subject_name, defaults={
                "code": generated_code,
                "credits": 3
            })
            if not sub_created:
                subject.code = generated_code
                subject.save()

print("Database seeding completed! All courses, semesters, and subjects have been successfully generated.")
