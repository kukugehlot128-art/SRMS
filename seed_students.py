import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_rms.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from core.models import StudentProfile, Course, Semester, Subject

# Create dummy students for every existing semester in every course.
courses = Course.objects.all()
students_data = [
    ("Aarav", "Patel"),
    ("Vivaan", "Sharma"),
    ("Aditya", "Kumar"),
    ("Vihaan", "Singh"),
    ("Arjun", "Gupta"),
    ("Sai", "Rao"),
    ("Priya", "Devi"),
    ("Diya", "Jain"),
    ("Ananya", "Desai"),
    ("Kavya", "Menon"),
    ("Neha", "Reddy"),
    ("Riya", "Bose")
]

created_count = 0
for course in courses:
    semesters = Semester.objects.filter(course=course)
    for semester in semesters:
        subjects = Subject.objects.filter(semester=semester)
        
        # Pick 2-3 random names for this semester
        num_students = random.randint(2, 4)
        selected_names = random.sample(students_data, num_students)
        
        for first, last in selected_names:
            username = f"{first.lower()}_{last.lower()}_{course.code.lower()}_{semester.id}_{random.randint(100,999)}"
            email = f"{username}@edu.college.com"
            roll_number = f"{course.code}{semester.id}{random.randint(1000, 9999)}"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'email': email}
            )
            if created:
                user.set_password('student123')
                user.save()
            
            profile, p_created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'roll_number': roll_number,
                    'course': course,
                    'semester': semester,
                    'admission_year': 2025
                }
            )
            # Enroll them in all subjects of that semester
            if p_created and subjects.exists():
                profile.enrolled_subjects.set(subjects)
                profile.save()
            
            if p_created:
                created_count += 1

print(f"✅ Successfully seeded {created_count} dynamic dummy students across all courses and semesters!")
