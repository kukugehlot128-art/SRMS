from core.models import Timetable
import datetime

bca_timetable_data = [
    {
        'course_name': 'BCA',
        'subject_name': 'Introduction to Programming (C)',
        'day': 'Monday',
        'start_time': datetime.time(9, 0),
        'end_time': datetime.time(10, 0),
        'faculty_name': 'A. Sharma',
        'room_number': 'Lab 1'
    },
    {
        'course_name': 'BCA',
        'subject_name': 'Mathematics I',
        'day': 'Monday',
        'start_time': datetime.time(10, 0),
        'end_time': datetime.time(11, 0),
        'faculty_name': 'R. Verma',
        'room_number': 'Room 101'
    },
    {
        'course_name': 'BCA',
        'subject_name': 'Computer Fundamentals',
        'day': 'Tuesday',
        'start_time': datetime.time(9, 30),
        'end_time': datetime.time(11, 30),
        'faculty_name': 'K. Singh',
        'room_number': 'Room 102'
    },
    {
        'course_name': 'BCA',
        'subject_name': 'Digital Electronics',
        'day': 'Wednesday',
        'start_time': datetime.time(11, 0),
        'end_time': datetime.time(12, 30),
        'faculty_name': 'S. Gupta',
        'room_number': 'Room 103'
    },
    {
        'course_name': 'BCA',
        'subject_name': 'Communication Skills',
        'day': 'Thursday',
        'start_time': datetime.time(14, 0),
        'end_time': datetime.time(15, 0),
        'faculty_name': 'T. Patel',
        'room_number': 'Room 104'
    },
    {
        'course_name': 'BCA',
        'subject_name': 'Programming Lab',
        'day': 'Friday',
        'start_time': datetime.time(10, 0),
        'end_time': datetime.time(13, 0),
        'faculty_name': 'A. Sharma',
        'room_number': 'Lab 2'
    }
]

for data in bca_timetable_data:
    Timetable.objects.get_or_create(**data)

print("BCA Dummy Timetable Data Created Successfully!")
