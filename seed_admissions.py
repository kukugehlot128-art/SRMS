import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_rms.settings')
django.setup()

from core.models import AdmissionEnquiry

AdmissionEnquiry.objects.get_or_create(
    full_name='Rahul Kumar', dob='2002-05-15', father_name='Ramesh Kumar', 
    mother_name='Sita Devi', gender='Male', mobile='9876543210', 
    email='rahul@example.com', address='Delhi', qualification='12th Pass', 
    passing_year=2020, marks=85.5, previous_school='DPS', 
    course='BCA', admission_year='2025'
)
AdmissionEnquiry.objects.get_or_create(
    full_name='Priya Sharma', dob='2003-08-20', father_name='Vinod Sharma', 
    mother_name='Meena Sharma', gender='Female', mobile='9876543211', 
    email='priya@example.com', address='Mumbai', qualification='12th Pass', 
    passing_year=2021, marks=92.0, previous_school='KV', 
    course='MCA', admission_year='2025'
)
print('Seeded dynamically.')
