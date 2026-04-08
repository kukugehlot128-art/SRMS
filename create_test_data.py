#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_rms.settings')
django.setup()

from core.models import AdmissionEnquiry

def create_test_data():
    # Check existing admissions
    existing_count = AdmissionEnquiry.objects.count()
    print(f'Existing admission enquiries: {existing_count}')

    # Create test admissions if none exist
    if existing_count == 0:
        admissions = [
            {
                'full_name': 'Rahul Sharma',
                'dob': date(2000, 5, 15),
                'father_name': 'Rajesh Sharma',
                'mother_name': 'Priya Sharma',
                'gender': 'Male',
                'mobile': '9876543210',
                'email': 'rahul@example.com',
                'address': 'Delhi, India',
                'qualification': '12th Grade',
                'passing_year': 2018,
                'marks': 85.5,
                'previous_school': 'Delhi Public School',
                'course': 'BCA',
                'admission_year': '2024',
                'status': 'Approved'
            },
            {
                'full_name': 'Priya Singh',
                'dob': date(2001, 3, 20),
                'father_name': 'Amit Singh',
                'mother_name': 'Kavita Singh',
                'gender': 'Female',
                'mobile': '9876543211',
                'email': 'priya@example.com',
                'address': 'Mumbai, India',
                'qualification': '12th Grade',
                'passing_year': 2019,
                'marks': 92.0,
                'previous_school': 'St. Mary School',
                'course': 'MCA',
                'admission_year': '2024',
                'status': 'Pending'
            }
        ]

        for admission_data in admissions:
            admission, created = AdmissionEnquiry.objects.get_or_create(
                email=admission_data['email'],
                defaults=admission_data
            )
            if created:
                print(f'Created admission enquiry for {admission_data["full_name"]}')
            else:
                print(f'Admission enquiry for {admission_data["full_name"]} already exists')

    print(f'Total admission enquiries: {AdmissionEnquiry.objects.count()}')

if __name__ == '__main__':
    create_test_data()