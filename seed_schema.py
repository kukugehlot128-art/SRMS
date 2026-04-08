import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_rms.settings')
django.setup()

from core.models import User, Course, Semester, ExamType, Subject

# Create Admin User
if not dict(User.objects.filter(username='admin').values()) and not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Superuser created")

# Create Course
course, created = Course.objects.get_or_create(
    code='BCA',
    defaults={
        'name': 'Bachelor of Computer Applications',
        'duration': '3 Years',
        'description': 'A 3-year undergraduate degree in computer applications.'
    }
)

if created:
    print("Course BCA created")

# Create Semesters
semester_names = ['1BCA', '2BCA', '3BCA', '4BCA', '5BCA', '6BCA']
for name in semester_names:
    Semester.objects.get_or_create(
        course=course,
        name=name
    )

print("Semesters created")

# Create Exam Types
exam_types = ['Internal Exam', 'Midterm Exam', 'Practical Exam', 'Main Exam']
for et in exam_types:
    ExamType.objects.get_or_create(name=et)

print("Exam Types created")
