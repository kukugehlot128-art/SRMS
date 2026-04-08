import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_sys.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import (
    Course, Subject, StudentProfile, Attendance, 
    Assignment, Notification, Event, Exam, Result
)

User = get_user_model()

def seed_data():
    print("Clearing existing data...")
    User.objects.exclude(is_superuser=True).delete()
    Course.objects.all().delete()
    Subject.objects.all().delete()
    Notification.objects.all().delete()
    Event.objects.all().delete()

    print("Creating users...")
    admin, _ = User.objects.get_or_create(username='admin', defaults={'role': 'admin', 'is_staff': True, 'is_superuser': True, 'first_name': 'Super', 'last_name': 'Admin'})
    admin.set_password('admin123')
    admin.save()
    
    prof1 = User.objects.create_user(username='prof1', password='password123', role='professor', first_name='John', last_name='Doe')
    prof2 = User.objects.create_user(username='prof2', password='password123', role='professor', first_name='Jane', last_name='Smith')
    
    student1_user = User.objects.create_user(username='student1', password='password123', role='student', first_name='Alice', last_name='Johnson')
    student2_user = User.objects.create_user(username='student2', password='password123', role='student', first_name='Bob', last_name='Williams')

    print("Creating courses & subjects...")
    course1 = Course.objects.create(name='Computer Science', code='CS101', duration_years=4)
    course2 = Course.objects.create(name='Information Technology', code='IT101', duration_years=4)

    subj1 = Subject.objects.create(name='Data Structures', code='DS201', course=course1, credit_hours=3, professor=prof1)
    subj2 = Subject.objects.create(name='Algorithms', code='AL202', course=course1, credit_hours=4, professor=prof2)
    subj3 = Subject.objects.create(name='Web Development', code='WD301', course=course2, credit_hours=3, professor=prof1)

    print("Creating student profiles...")
    student1 = StudentProfile.objects.create(user=student1_user, roll_number='CS2023001', course=course1, date_of_birth='2000-01-01', phone_number='1234567890', address='123 Main St')
    student1.enrolled_subjects.set([subj1, subj2])
    
    student2 = StudentProfile.objects.create(user=student2_user, roll_number='IT2023001', course=course2, date_of_birth='2001-02-02', phone_number='0987654321', address='456 Oak Ave')
    student2.enrolled_subjects.set([subj3])

    print("Creating attendance records...")
    today = date.today()
    for i in range(10):
        d = today - timedelta(days=i)
        Attendance.objects.create(student=student1, subject=subj1, date=d, status=random.choice(['present', 'present', 'present', 'absent']))
        Attendance.objects.create(student=student1, subject=subj2, date=d, status=random.choice(['present', 'present', 'absent']))
        Attendance.objects.create(student=student2, subject=subj3, date=d, status=random.choice(['present', 'present', 'present', 'absent']))

    print("Creating assignments...")
    Assignment.objects.create(subject=subj1, title='Linked List Implementation', description='Implement a singly linked list in Python. Submit the .py file.', due_date=today + timedelta(days=5), max_marks=10, created_by=prof1)
    Assignment.objects.create(subject=subj2, title='Graph Traversal', description='Write BFS and DFS algorithms.', due_date=today + timedelta(days=7), max_marks=20, created_by=prof2)

    print("Creating notifications...")
    Notification.objects.create(title='Welcome to the new Semester', message='Classes start next Monday.', notif_type='general', target_role='all', created_by=admin)
    Notification.objects.create(title='Assignment 1 Due', message='Please submit your data structures assignment on time.', notif_type='assignment', target_role='student', created_by=prof1)

    print("Creating events...")
    Event.objects.create(title='Tech Innovators Summit 2026', description='Annual tech summit for all engineering students.', event_date=today + timedelta(days=14), venue='Main Auditorium', created_by=admin)

    print("Creating exams & results...")
    exam1 = Exam.objects.create(subject=subj1, course=course1, title='Midterm: Data Structures', date=today - timedelta(days=5), start_time='10:00:00', end_time='12:00:00', total_marks=100)
    Result.objects.create(student=student1, exam=exam1, marks_obtained=85, grade='A+', remarks='Excellent work!')

    print("Data seeded successfully!")
    print("\nCredentials:")
    print("Admin: admin / admin123")
    print("Professors: prof1 / password123, prof2 / password123")
    print("Students: student1 / password123, student2 / password123")

if __name__ == '__main__':
    seed_data()
