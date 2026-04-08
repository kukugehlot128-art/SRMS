from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import models
from .models import (
    Course, Subject, Event, Notification, ExamTimeTable, Result, StudentProfile,
    User, Attendance, Assignment, Semester, ExamType, ProfessorProfile, AssignmentSubmission,
    StudentResult, SubjectResult, ExamSchedule, Timetable, AdmissionEnquiry
)
import random


def home(request):
    courses = Course.objects.all().order_by('-id')[:3]
    events = Event.objects.all().order_by('-event_date')[:3]
    notifications = Notification.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]
    from datetime import date
    exams = ExamTimeTable.objects.filter(date__gte=date.today()).order_by('date')[:1]
    return render(request, 'core/home.html', {
        'courses': courses,
        'events': events,
        'notifications': notifications,
        'exams': exams,
    })


def about(request):
    return render(request, 'core/about.html')

def admission(request):
    if request.method == 'POST':
        # Create AdmissionEnquiry object
        AdmissionEnquiry.objects.create(
            full_name=request.POST.get('full_name'),
            dob=request.POST.get('dob'),
            father_name=request.POST.get('father_name'),
            mother_name=request.POST.get('mother_name'),
            gender=request.POST.get('gender'),
            mobile=request.POST.get('mobile'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            qualification=request.POST.get('qualification'),
            passing_year=request.POST.get('passing_year'),
            marks=request.POST.get('marks'),
            previous_school=request.POST.get('previous_school'),
            course=request.POST.get('course'),
            admission_year=request.POST.get('admission_year'),
            photo=request.FILES.get('photo'),
            marksheet=request.FILES.get('marksheet'),
            id_proof=request.FILES.get('id_proof'),
        )
        messages.success(request, 'Your admission request has been submitted successfully! We will contact you soon.')
        return redirect('core:admission')
    return render(request, 'core/admission.html')


def courses_page(request):
    courses = Course.objects.all().order_by('category', 'name')
    return render(request, 'core/courses.html', {'courses': courses})


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # A course has semesters, and semesters have subjects. Let's fetch subjects under this course.
    subjects = Subject.objects.filter(semester__course=course)
    return render(request, 'core/course_detail.html', {'course': course, 'subjects': subjects})


def events_page(request):
    events = Event.objects.all().order_by('-event_date')
    return render(request, 'core/events.html', {'events': events})


def notifications_page(request):
    notifications = Notification.objects.filter(
        is_active=True
    ).order_by('-created_at')
    return render(request, 'core/notifications.html', {
        'notifications': notifications
    })


def timetable_page(request):
    courses = Timetable.objects.values_list('course_name', flat=True).distinct()
    timetables = Timetable.objects.all().order_by('day', 'start_time')
    return render(request, 'core/timetable.html', {'courses': courses, 'timetables': timetables})


def exam_page(request):
    exams = ExamTimeTable.objects.all().order_by('date', 'start_time')
    return render(request, 'core/exam.html', {'exams': exams})


def result_search(request):
    # Generate captcha
    if 'captcha_answer' not in request.session or request.method == 'GET':
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        request.session['captcha_answer'] = num1 + num2
        captcha_text = f"{num1} + {num2}"
        request.session['captcha_text'] = captcha_text
    else:
        captcha_text = request.session['captcha_text']

    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        captcha_input = request.POST.get('captcha_input')
        
        try:
            if int(captcha_input) != request.session.get('captcha_answer'):
                messages.error(request, 'Incorrect captcha. Please try again.')
                return redirect('core:result_search')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid captcha input.')
            return redirect('core:result_search')
            
        if roll_number:
            try:
                student_result = StudentResult.objects.get(roll_number=roll_number)
                
                subjects = []
                total_max = 0
                total_obt = student_result.total_marks
                lines = student_result.subject_marks.strip().split('\n')
                for i, line in enumerate(lines):
                    if ':' in line:
                        name, marks = line.split(':', 1)
                        obt = int(marks.strip()) if marks.strip().isdigit() else 0
                        max_mark = 100
                        total_max += max_mark
                        result_status = 'PASS' if obt >= 35 else 'FAIL'
                        subjects.append({
                            'code': f'SUB{i+1:03d}',
                            'name': name.strip(),
                            'max': max_mark,
                            'obt': obt,
                            'result': result_status
                        })
                
                if total_max == 0:
                    total_max = 100
                    
                percentage = round((total_obt / total_max) * 100, 2)
                division = 'FIRST CLASS' if percentage >= 60 else 'SECOND CLASS' if percentage >= 45 else 'THIRD CLASS' if percentage >= 35 else 'FAIL'
                
                class DummyStudent:
                    pass
                student_obj = DummyStudent()
                student_obj.student_name = student_result.student_name
                student_obj.roll_number = student_result.roll_number
                student_obj.course_name = student_result.get_course_display()
                student_obj.father_name = 'N/A'
                
                return render(request, 'core/result_display.html', {
                    'student': student_obj,
                    'exam_name': student_result.exam_name,
                    'subjects': subjects,
                    'total_max': total_max,
                    'total_obt': total_obt,
                    'percentage': percentage,
                    'division': division,
                    'overall_result': student_result.status,
                })
            except StudentResult.DoesNotExist:
                messages.error(request, 'Result not found for this Roll Number.')
                return redirect('core:result_search')
        else:
            messages.error(request, 'Please provide Roll Number.')
            return redirect('core:result_search')
            
    return render(request, 'core/result_search.html', {'captcha_text': captcha_text})

def admit_card_search(request):
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        enrollment_number = request.POST.get('enrollment_number')  # Get newly added field
        dob = request.POST.get('dob')  # Get newly added field
        
        if roll_number:
            try:
                student = StudentProfile.objects.get(roll_number=roll_number)
                exams = ExamTimeTable.objects.filter(semester=student.semester).order_by('date')
                return render(request, 'core/admit_card_display.html', {
                    'student': student,
                    'exams': exams,
                    'enrollment_number': enrollment_number, # Pass dummy value to template
                    'dob': dob # Pass dummy value to template
                })
            except StudentProfile.DoesNotExist:
                messages.error(request, 'Student with this Roll Number not found.')
                return redirect('core:admit_card_search')
    return render(request, 'core/admit_card_search.html')


# ---- LOGIN VIEWS ----

def student_login(request):
    if request.user.is_authenticated and request.user.role == 'student':
        return redirect('core:student_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.role == 'student':
            login(request, user)
            return redirect('core:student_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a student account.')
    return render(request, 'core/student_login.html')


def professor_login(request):
    if request.user.is_authenticated and request.user.role == 'professor':
        return redirect('core:professor_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.role == 'professor':
            login(request, user)
            return redirect('core:professor_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a professor account.')
    return render(request, 'core/professor_login.html')


def admin_login(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('core:admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and (user.role == 'admin' or user.is_superuser):
            if not user.role == 'admin':
                user.role = 'admin'
                user.save()
            login(request, user)
            return redirect('core:admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin account.')
    return render(request, 'core/admin_login.html')


def logout_view(request):
    logout(request)
    return redirect('core:home')


# ---- ADMIN VIEWS ----

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def admin_required(view_func):
    return user_passes_test(is_admin, login_url='core:admin_login')(view_func)

@admin_required
def admin_dashboard(request):
    data = {
        'total_students': StudentProfile.objects.count(),
        'total_professors': User.objects.filter(role='professor').count(),
        'total_courses': Course.objects.count(),
        'total_subjects': Subject.objects.count(),
        'recent_events': Event.objects.order_by('-created_at')[:3],
    }
    return render(request, 'core/admin/dashboard.html', data)

@admin_required
def manage_courses(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        duration = request.POST.get('duration')
        category = request.POST.get('category', 'Other')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        Course.objects.create(name=name, code=code, category=category, duration=duration, description=description, image=image)
        messages.success(request, 'Course added successfully!')
        return redirect('core:manage_courses')
        
    courses = Course.objects.all()
    return render(request, 'core/admin/courses.html', {'courses': courses})

@admin_required
def manage_subjects(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        semester_id = request.POST.get('semester_id')
        professor_id = request.POST.get('professor_id')
        credits = request.POST.get('credits', 3)
        
        semester_obj = Semester.objects.get(id=semester_id)
        professor = User.objects.get(id=professor_id) if professor_id else None
        
        Subject.objects.create(
            name=name, code=code, semester=semester_obj, professor=professor,
            credits=credits
        )
        messages.success(request, 'Subject added successfully!')
        return redirect('core:manage_subjects')
        
    subjects = Subject.objects.all()
    semesters = Semester.objects.all()
    professors = User.objects.filter(role='professor')
    courses = Course.objects.all()
    return render(request, 'core/admin/subjects.html', {
        'subjects': subjects, 'semesters': semesters, 'professors': professors, 'courses': courses
    })

@admin_required
def manage_students(request):
    query = request.GET.get('q', '').strip()
    students = StudentProfile.objects.select_related('user', 'course').all()

    if query:
        students = students.filter(
            models.Q(user__first_name__icontains=query) |
            models.Q(user__last_name__icontains=query) |
            models.Q(user__email__icontains=query) |
            models.Q(roll_number__icontains=query) |
            models.Q(enrollment_number__icontains=query)
        )

    return render(request, 'core/admin/students.html', {'students': students, 'query': query})

@admin_required
def manage_admissions(request):
    if request.method == 'POST':
        enquiry_id = request.POST.get('enquiry_id')
        status = request.POST.get('status')
        if enquiry_id and status in dict(AdmissionEnquiry.STATUS_CHOICES):
            try:
                enquiry = AdmissionEnquiry.objects.get(pk=enquiry_id)
                enquiry.status = status
                enquiry.save()
                messages.success(request, 'Admission status updated successfully.')
            except AdmissionEnquiry.DoesNotExist:
                messages.error(request, 'Admission request not found.')
        else:
            messages.error(request, 'Invalid admission update request.')
        return redirect('core:manage_admissions')

    query = request.GET.get('q', '').strip()
    admissions = AdmissionEnquiry.objects.order_by('-submitted_at')
    if query:
        admissions = admissions.filter(
            models.Q(full_name__icontains=query) |
            models.Q(email__icontains=query) |
            models.Q(mobile__icontains=query) |
            models.Q(course__icontains=query)
        )

    return render(request, 'core/admin/admissions.html', {'admissions': admissions, 'query': query})

@admin_required
def manage_streams(request):
    streams = Semester.objects.select_related('course').all()
    courses = Course.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        course_id = request.POST.get('course_id')
        if name and course_id:
            course = get_object_or_404(Course, pk=course_id)
            Semester.objects.create(name=name, course=course)
            messages.success(request, 'Stream added successfully!')
            return redirect('core:manage_streams')
            
    return render(request, 'core/admin/streams.html', {'streams': streams, 'courses': courses})

@admin_required
def update_stream(request, pk):
    stream = get_object_or_404(Semester, pk=pk)
    if request.method == 'POST':
        stream.name = request.POST.get('name')
        course_id = request.POST.get('course_id')
        if course_id:
            stream.course = get_object_or_404(Course, pk=course_id)
        stream.save()
        messages.success(request, 'Stream updated successfully!')
        return redirect('core:manage_streams')
    courses = Course.objects.all()
    return render(request, 'core/admin/stream_form.html', {'stream': stream, 'courses': courses})

@admin_required
def delete_stream(request, pk):
    stream = get_object_or_404(Semester, pk=pk)
    if request.method == 'POST':
        stream.delete()
        messages.success(request, 'Stream deleted successfully!')
        return redirect('core:manage_streams')
    return render(request, 'core/admin/confirm_delete.html', {'obj': stream, 'cancel_url': 'core:manage_streams'})

@admin_required
def manage_events(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')
        venue = request.POST.get('venue')
        image = request.FILES.get('image')
        
        Event.objects.create(
            title=title, description=description, event_date=event_date,
            venue=venue, image=image, created_by=request.user
        )
        messages.success(request, 'Event added successfully!')
        return redirect('core:manage_events')
        
    events = Event.objects.order_by('-event_date')
    return render(request, 'core/admin/events.html', {'events': events})

@admin_required
def manage_notifications(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        notif_type = request.POST.get('notif_type')
        target_role = request.POST.get('target_role')
        
        Notification.objects.create(
            title=title, message=message, notif_type=notif_type,
            target_role=target_role, created_by=request.user
        )
        messages.success(request, 'Notification sent successfully!')
        return redirect('core:manage_notifications')
        
    notifications = Notification.objects.order_by('-created_at')
    return render(request, 'core/admin/notifications.html', {'notifications': notifications})

@admin_required
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.name = request.POST.get('name')
        course.code = request.POST.get('code')
        course.category = request.POST.get('category', 'Other')
        course.duration = request.POST.get('duration')
        course.description = request.POST.get('description', '')
        if 'image' in request.FILES:
            course.image = request.FILES['image']
        course.save()
        messages.success(request, 'Course updated successfully!')
        return redirect('core:manage_courses')
    return render(request, 'core/admin/course_form.html', {'course': course})

@admin_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('core:manage_courses')
    return render(request, 'core/admin/confirm_delete.html', {'obj': course, 'cancel_url': 'core:manage_courses'})

@admin_required
def update_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.name = request.POST.get('name')
        subject.code = request.POST.get('code')
        subject.semester_id = request.POST.get('semester_id')
        subject.professor_id = request.POST.get('professor_id') or None
        subject.credits = request.POST.get('credits', 3)
        subject.save()
        messages.success(request, 'Subject updated successfully!')
        return redirect('core:manage_subjects')
    
    semesters = Semester.objects.all()
    professors = User.objects.filter(role='professor')
    courses = Course.objects.all()
    return render(request, 'core/admin/subject_form.html', {
        'subject': subject, 'semesters': semesters, 'professors': professors, 'courses': courses
    })

@admin_required
def delete_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully!')
        return redirect('core:manage_subjects')
    return render(request, 'core/admin/confirm_delete.html', {'obj': subject, 'cancel_url': 'core:manage_subjects'})

@admin_required
def create_student(request):
    if request.method == 'POST':
        # Get data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        username = request.POST.get('username')
        password = request.POST.get('password')
        roll_number = request.POST.get('roll_number')
        enrollment_number = request.POST.get('enrollment_number')
        admission_year = request.POST.get('admission_year') or None
        father_name = request.POST.get('father_name', '')
        mother_name = request.POST.get('mother_name', '')
        description = request.POST.get('description', '')
        semester_id = request.POST.get('semester_id')
        date_of_birth = request.POST.get('date_of_birth') or None
        address = request.POST.get('address')
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('core:manage_students')
            
        # Create User
        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name, role='student', phone=phone
        )
        
        # Create Profile
        semester_obj = get_object_or_404(Semester, pk=semester_id)
        StudentProfile.objects.create(
            user=user, roll_number=roll_number, course=semester_obj.course,
            semester=semester_obj, date_of_birth=date_of_birth, address=address,
            enrollment_number=enrollment_number, admission_year=admission_year, 
            father_name=father_name, mother_name=mother_name, description=description
        )
        messages.success(request, 'Student created successfully!')
        return redirect('core:manage_students')
        
    semesters = Semester.objects.all()
    courses = Course.objects.all()
    return render(request, 'core/admin/student_form.html', {'semesters': semesters, 'courses': courses, 'is_update': False})

@admin_required
def update_student(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    user_obj = student.user
    
    if request.method == 'POST':
        # Update User
        user_obj.first_name = request.POST.get('first_name')
        user_obj.last_name = request.POST.get('last_name')
        user_obj.email = request.POST.get('email')
        user_obj.phone = request.POST.get('phone', '')
        user_obj.save()
        
        # Update Profile
        student.roll_number = request.POST.get('roll_number')
        student.enrollment_number = request.POST.get('enrollment_number')
        student.admission_year = request.POST.get('admission_year') or None
        student.father_name = request.POST.get('father_name', '')
        student.mother_name = request.POST.get('mother_name', '')
        student.description = request.POST.get('description', '')
        
        semester_id = request.POST.get('semester_id')
        if semester_id:
            semester_obj = get_object_or_404(Semester, pk=semester_id)
            student.semester = semester_obj
            student.course = semester_obj.course
            
        student.date_of_birth = request.POST.get('date_of_birth') or None
        student.address = request.POST.get('address')
        student.save()
        
        messages.success(request, 'Student updated successfully!')
        return redirect('core:manage_students')
    
    semesters = Semester.objects.all()
    courses = Course.objects.all()
    return render(request, 'core/admin/student_form.html', {
        'student': student, 'user_obj': user_obj, 'semesters': semesters, 'courses': courses, 'is_update': True
    })

@admin_required
def student_detail(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    return render(request, 'core/admin/student_detail.html', {'student': student})

@admin_required
def delete_student(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    user_obj = student.user
    if request.method == 'POST':
        user_obj.delete() # Profile will be deleted automatically due to CASCADE
        messages.success(request, 'Student deleted successfully!')
        return redirect('core:manage_students')
    return render(request, 'core/admin/confirm_delete.html', {'obj': student, 'cancel_url': 'core:manage_students'})

@admin_required
def manage_professors(request):
    professors = ProfessorProfile.objects.select_related('user').all()
    return render(request, 'core/admin/professors.html', {'professors': professors})

@admin_required
def create_professor(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        username = request.POST.get('username')
        password = request.POST.get('password')
        department = request.POST.get('department')
        father_name = request.POST.get('father_name', '')
        mother_name = request.POST.get('mother_name', '')
        address = request.POST.get('address')
        date_of_joining = request.POST.get('date_of_joining') or None
        passing_year = request.POST.get('passing_year') or None
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('core:manage_professors')
            
        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name, role='professor', phone=phone
        )
        
        ProfessorProfile.objects.create(
            user=user, department=department, father_name=father_name,
            mother_name=mother_name, address=address, date_of_joining=date_of_joining,
            passing_year=passing_year
        )
        messages.success(request, 'Professor added successfully!')
        return redirect('core:manage_professors')
        
    return render(request, 'core/admin/professor_form.html', {'is_update': False})

@admin_required
def update_professor(request, pk):
    professor = get_object_or_404(ProfessorProfile, pk=pk)
    user_obj = professor.user
    
    if request.method == 'POST':
        user_obj.first_name = request.POST.get('first_name')
        user_obj.last_name = request.POST.get('last_name')
        user_obj.email = request.POST.get('email')
        user_obj.phone = request.POST.get('phone', '')
        user_obj.save()
        
        professor.department = request.POST.get('department')
        professor.father_name = request.POST.get('father_name', '')
        professor.mother_name = request.POST.get('mother_name', '')
        professor.address = request.POST.get('address')
        professor.date_of_joining = request.POST.get('date_of_joining') or None
        professor.passing_year = request.POST.get('passing_year') or None
        professor.save()
        
        messages.success(request, 'Professor updated successfully!')
        return redirect('core:manage_professors')
    
    return render(request, 'core/admin/professor_form.html', {
        'professor': professor, 'user_obj': user_obj, 'is_update': True
    })

@admin_required
def professor_detail(request, pk):
    professor = get_object_or_404(ProfessorProfile, pk=pk)
    return render(request, 'core/admin/professor_detail.html', {'professor': professor})

@admin_required
def delete_professor(request, pk):
    professor = get_object_or_404(ProfessorProfile, pk=pk)
    user_obj = professor.user
    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, 'Professor deleted successfully!')
        return redirect('core:manage_professors')
    return render(request, 'core/admin/confirm_delete.html', {'obj': professor, 'cancel_url': 'core:manage_professors'})

@admin_required
def update_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notif.title = request.POST.get('title')
        notif.message = request.POST.get('message')
        notif.notif_type = request.POST.get('notif_type')
        notif.target_role = request.POST.get('target_role')
        notif.is_active = request.POST.get('is_active') == 'on'
        notif.save()
        messages.success(request, 'Notification updated successfully!')
        return redirect('core:manage_notifications')
    return render(request, 'core/admin/notification_form.html', {'notif': notif})

@admin_required
def delete_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notif.delete()
        messages.success(request, 'Notification deleted successfully!')
        return redirect('core:manage_notifications')
    return render(request, 'core/admin/confirm_delete.html', {'obj': notif, 'cancel_url': 'core:manage_notifications'})

@admin_required
def update_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.event_date = request.POST.get('event_date')
        event.venue = request.POST.get('venue')
        
        if 'image' in request.FILES:
            event.image = request.FILES['image']
            
        event.save()
        messages.success(request, 'Event updated successfully!')
        return redirect('core:manage_events')
    return render(request, 'core/admin/event_form.html', {'event': event})

@admin_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('core:manage_events')
    return render(request, 'core/admin/confirm_delete.html', {'obj': event, 'cancel_url': 'core:manage_events'})

@admin_required
def manage_exams(request):
    exams = ExamTimeTable.objects.select_related('subject').order_by('-date', '-start_time')
    return render(request, 'core/admin/exams.html', {'exams': exams})

@admin_required
def create_exam(request):
    if request.method == 'POST':
        exam_type_ids = request.POST.getlist('exam_type_id[]')
        exam_type_id = exam_type_ids[0] if exam_type_ids else request.POST.get('exam_type_id[]')
        exam_type_obj = get_object_or_404(ExamType, pk=exam_type_id)

        subject_ids = request.POST.getlist('subject_id[]')
        dates = request.POST.getlist('date[]')
        start_times = request.POST.getlist('start_time[]')
        end_times = request.POST.getlist('end_time[]')
        total_marks_list = request.POST.getlist('total_marks[]')
        rooms = request.POST.getlist('room[]')
        
        for i in range(len(subject_ids)):
            s_id = subject_ids[i]
            if not s_id: continue
            
            subject = get_object_or_404(Subject, pk=s_id)
            d = dates[i] if len(dates) > i else dates[0]
            st = start_times[i] if len(start_times) > i else start_times[0]
            et = end_times[i] if len(end_times) > i else end_times[0]
            tm = total_marks_list[i] if len(total_marks_list) > i else 100
            rm = rooms[i] if len(rooms) > i else rooms[0]
            
            ExamTimeTable.objects.create(
                semester=subject.semester, subject=subject, exam_type=exam_type_obj,
                date=d, start_time=st, end_time=et,
                total_marks=tm, room=rm
            )
            
        messages.success(request, 'Exam(s) scheduled successfully!')
        return redirect('core:manage_exams')
        
    subjects = Subject.objects.select_related('semester').all()
    exam_types = ExamType.objects.all()
    streams = Semester.objects.select_related('course').all()
    return render(request, 'core/admin/exam_form.html', {'subjects': subjects, 'exam_types': exam_types, 'streams': streams, 'is_update': False})

@admin_required
def update_exam(request, pk):
    exam = get_object_or_404(ExamTimeTable, pk=pk)
    if request.method == 'POST':
        exam_type_ids = request.POST.getlist('exam_type_id[]')
        exam_type_id = exam_type_ids[0] if exam_type_ids else request.POST.get('exam_type_id[]')
        if exam_type_id:
            exam.exam_type_id = exam_type_id
        
        # In update, we might still get arrays but they only have one item
        subjects = request.POST.getlist('subject_id[]')
        exam.subject_id = subjects[0] if subjects else request.POST.get('subject_id')
        if exam.subject:
            exam.semester_id = exam.subject.semester_id
            
        dates = request.POST.getlist('date[]')
        exam.date = dates[0] if dates else request.POST.get('date')
        
        starts = request.POST.getlist('start_time[]')
        exam.start_time = starts[0] if starts else request.POST.get('start_time')
        
        ends = request.POST.getlist('end_time[]')
        exam.end_time = ends[0] if ends else request.POST.get('end_time')
        
        marks = request.POST.getlist('total_marks[]')
        exam.total_marks = marks[0] if marks else request.POST.get('total_marks', 100)
        
        rooms = request.POST.getlist('room[]')
        exam.room = rooms[0] if rooms else request.POST.get('room')
        
        exam.save()
        messages.success(request, 'Exam updated successfully!')
        return redirect('core:manage_exams')
        
    subjects = Subject.objects.select_related('semester').all()
    exam_types = ExamType.objects.all()
    streams = Semester.objects.select_related('course').all()
    return render(request, 'core/admin/exam_form.html', {'exam': exam, 'subjects': subjects, 'exam_types': exam_types, 'streams': streams, 'is_update': True})

@admin_required
def delete_exam(request, pk):
    exam = get_object_or_404(ExamTimeTable, pk=pk)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, 'Exam deleted successfully!')
        return redirect('core:manage_exams')
    return render(request, 'core/admin/confirm_delete.html', {'obj': exam, 'cancel_url': 'core:manage_exams'})

@admin_required
def manage_timetable(request):
    timetables = Timetable.objects.all().order_by('day', 'start_time')
    courses = Timetable.objects.values_list('course_name', flat=True).distinct()
    return render(request, 'core/admin/timetable.html', {'timetables': timetables, 'courses': courses})

@admin_required
def create_timetable(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        subject_name = request.POST.get('subject_name')
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        duration = request.POST.get('duration')
        faculty_name = request.POST.get('faculty_name')
        room_number = request.POST.get('room_number')
        
        Timetable.objects.create(
            course_name=course_name, subject_name=subject_name, day=day,
            start_time=start_time, end_time=end_time, duration=duration,
            faculty_name=faculty_name, room_number=room_number
        )
        messages.success(request, 'Timetable entry created successfully!')
        return redirect('core:manage_timetable')
    
    courses = ['BCA', 'MCA', 'MBA']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return render(request, 'core/admin/timetable_form.html', {'courses': courses, 'days': days, 'is_update': False})

@admin_required
def update_timetable(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    if request.method == 'POST':
        timetable.course_name = request.POST.get('course_name')
        timetable.subject_name = request.POST.get('subject_name')
        timetable.day = request.POST.get('day')
        timetable.start_time = request.POST.get('start_time')
        timetable.end_time = request.POST.get('end_time')
        timetable.duration = request.POST.get('duration')
        timetable.faculty_name = request.POST.get('faculty_name')
        timetable.room_number = request.POST.get('room_number')
        timetable.save()
        messages.success(request, 'Timetable entry updated successfully!')
        return redirect('core:manage_timetable')
    
    courses = ['BCA', 'MCA', 'MBA']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return render(request, 'core/admin/timetable_form.html', {'timetable': timetable, 'courses': courses, 'days': days, 'is_update': True})

@admin_required
def delete_timetable(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    if request.method == 'POST':
        timetable.delete()
        messages.success(request, 'Timetable entry deleted successfully!')
        return redirect('core:manage_timetable')
    return render(request, 'core/admin/confirm_delete.html', {'obj': timetable, 'cancel_url': 'core:manage_timetable'})

@admin_required
def manage_subject_results(request):
    subject_results = SubjectResult.objects.select_related('student__user', 'subject').order_by('-created_at')
    
    # Filter options
    courses = Course.objects.all()
    semesters = Semester.objects.all()
    subjects = Subject.objects.all()
    
    # Apply filters
    course_id = request.GET.get('course')
    semester_id = request.GET.get('semester')
    subject_id = request.GET.get('subject')
    status_filter = request.GET.get('status')
    
    if course_id:
        subject_results = subject_results.filter(student__course_id=course_id)
    if semester_id:
        subject_results = subject_results.filter(student__semester_id=semester_id)
    if subject_id:
        subject_results = subject_results.filter(subject_id=subject_id)
    if status_filter:
        subject_results = subject_results.filter(result_status=status_filter)
    
    context = {
        'subject_results': subject_results,
        'courses': courses,
        'semesters': semesters,
        'subjects': subjects,
        'selected_course': course_id,
        'selected_semester': semester_id,
        'selected_subject': subject_id,
        'selected_status': status_filter,
    }
    return render(request, 'core/admin/subject_results.html', context)

@admin_required
def create_result(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        roll_number = request.POST.get('roll_number')
        course = request.POST.get('course')
        exam_name = request.POST.get('exam_name')
        subject_marks = request.POST.get('subject_marks')
        total_marks = request.POST.get('total_marks', 0)
        status = request.POST.get('status')
        centre_code = request.POST.get('centre_code')
        
        if StudentResult.objects.filter(roll_number=roll_number, exam_name=exam_name).exists():
            messages.error(request, 'Result for this student and exam already exists!')
            return redirect('core:create_result')
            
        StudentResult.objects.create(
            student_name=student_name, roll_number=roll_number, course=course,
            exam_name=exam_name, subject_marks=subject_marks, total_marks=total_marks,
            status=status, centre_code=centre_code
        )
        messages.success(request, 'Result published successfully!')
        return redirect('core:manage_results')
        
    return render(request, 'core/admin/result_form.html', {'is_update': False})

@admin_required
def update_result(request, pk):
    result = get_object_or_404(StudentResult, pk=pk)
    if request.method == 'POST':
        result.student_name = request.POST.get('student_name')
        result.roll_number = request.POST.get('roll_number')
        result.course = request.POST.get('course')
        result.exam_name = request.POST.get('exam_name')
        result.subject_marks = request.POST.get('subject_marks')
        result.total_marks = request.POST.get('total_marks', 0)
        result.status = request.POST.get('status')
        result.centre_code = request.POST.get('centre_code')
        result.save()
        messages.success(request, 'Result updated successfully!')
        return redirect('core:manage_results')
        
    return render(request, 'core/admin/result_form.html', {'result': result, 'is_update': True})

@admin_required
def delete_subject_result(request, pk):
    result = get_object_or_404(SubjectResult, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.success(request, 'Subject result deleted successfully!')
        return redirect('core:manage_subject_results')
    return render(request, 'core/admin/confirm_delete.html', {'obj': result, 'cancel_url': 'core:manage_subject_results'})

@admin_required
def manage_allotment(request):
    subjects = Subject.objects.select_related('professor').prefetch_related('studentprofile_set').all()
    professors = User.objects.filter(role='professor')
    students = StudentProfile.objects.select_related('user').all()
    
    return render(request, 'core/admin/subject_allotment.html', {
        'subjects': subjects, 'professors': professors, 'students': students
    })

@admin_required
def assign_professor(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        professor_id = request.POST.get('professor_id')
        
        subject = get_object_or_404(Subject, pk=subject_id)
        professor = get_object_or_404(User, pk=professor_id, role='professor')
        
        subject.professor = professor
        subject.save()
        messages.success(request, f'Assigned {professor.get_full_name()} to {subject.name}')
        
    return redirect('core:manage_allotment')

@admin_required
def enroll_student(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        student_id = request.POST.get('student_id')
        action = request.POST.get('enroll_action')
        
        subject = get_object_or_404(Subject, pk=subject_id)
        student = get_object_or_404(StudentProfile, pk=student_id)
        
        if action == 'add':
            student.enrolled_subjects.add(subject)
            messages.success(request, f'Enrolled {student.user.get_full_name()} in {subject.name}')
        elif action == 'remove':
            student.enrolled_subjects.remove(subject)
            messages.success(request, f'Removed {student.user.get_full_name()} from {subject.name}')
            
    return redirect('core:manage_allotment')

from datetime import date as dt_date, datetime

@admin_required
def manage_attendance(request):
    subjects = Subject.objects.all().order_by('semester', 'name')
    
    selected_subject = None
    students_attendance = []
    current_date_str = request.GET.get('date', dt_date.today().strftime('%Y-%m-%d'))
    
    try:
        current_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()
    except ValueError:
        current_date = dt_date.today()
        
    subject_id = request.GET.get('subject')
    
    if subject_id:
        selected_subject = get_object_or_404(Subject, pk=subject_id)
        
        # Get all enrolled students
        enrolled_students = selected_subject.studentprofile_set.select_related('user', 'course').order_by('roll_number')
        
        # Get existing attendance records for the date
        existing_records = {
            att.student_id: att.status 
            for att in Attendance.objects.filter(subject=selected_subject, date=current_date)
        }
        
        # Build attendance matrix
        for student in enrolled_students:
            students_attendance.append({
                'student': student,
                'status': existing_records.get(student.id, None)
            })
            
    context = {
        'subjects': subjects,
        'selected_subject': selected_subject,
        'current_date': current_date,
        'students_attendance': students_attendance,
        'is_today': current_date == dt_date.today(),
        'is_past': current_date < dt_date.today()
    }
    
    return render(request, 'core/admin/attendance.html', context)

@admin_required
def save_attendance(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        date_str = request.POST.get('date')
        
        subject = get_object_or_404(Subject, pk=subject_id)
        
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('core:manage_attendance')
        
        if attendance_date > dt_date.today():
            messages.error(request, 'Cannot mark attendance for future dates.')
            return redirect('core:manage_attendance')
            
        enrolled_students = subject.studentprofile_set.all()
        records_updated = 0
        records_created = 0
        
        # Process bulk updates/creates
        for student in enrolled_students:
            status_key = f'status_{student.id}'
            status = request.POST.get(status_key)
            
            if status in ['present', 'absent']:
                obj, created = Attendance.objects.update_or_create(
                    student=student,
                    subject=subject,
                    date=attendance_date,
                    defaults={'status': status, 'marked_by': request.user}
                )
                if created:
                    records_created += 1
                else:
                    records_updated += 1
                    
        messages.success(request, f'Attendance saved successfully. ({records_created} new, {records_updated} updated)')
        return redirect(f"/admin/attendance/?subject={subject_id}&date={date_str}")
        
    return redirect('core:manage_attendance')

@admin_required
def manage_assignments(request):
    assignments = Assignment.objects.select_related('subject').order_by('-created_at')
    return render(request, 'core/admin/assignments.html', {'assignments': assignments, 'today': dt_date.today()})

@admin_required
def create_assignment(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        subject_id = request.POST.get('subject_id')
        due_date = request.POST.get('due_date')
        max_marks = request.POST.get('max_marks', 10)
        
        subject = get_object_or_404(Subject, pk=subject_id)
        
        Assignment.objects.create(
            title=title, description=description, subject=subject,
            due_date=due_date, created_by=request.user, max_marks=max_marks
        )
        messages.success(request, 'Assignment created successfully!')
        return redirect('core:manage_assignments')
        
    subjects = Subject.objects.all()
    return render(request, 'core/admin/assignment_form.html', {'subjects': subjects, 'is_update': False})

@admin_required
def update_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        assignment.title = request.POST.get('title')
        assignment.description = request.POST.get('description')
        assignment.subject_id = request.POST.get('subject_id')
        assignment.due_date = request.POST.get('due_date')
        assignment.max_marks = request.POST.get('max_marks', 10)
        assignment.save()
        messages.success(request, 'Assignment updated successfully!')
        return redirect('core:manage_assignments')
        
    subjects = Subject.objects.all()
    return render(request, 'core/admin/assignment_form.html', {'assignment': assignment, 'subjects': subjects, 'is_update': True})

@admin_required
def delete_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully!')
        return redirect('core:manage_assignments')
    return render(request, 'core/admin/confirm_delete.html', {'obj': assignment, 'cancel_url': 'core:manage_assignments'})


# ---- PROFESSOR VIEWS ----

def professor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:professor_login')
        if request.user.role != 'professor':
            return redirect('core:professor_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

@professor_required
def professor_dashboard(request):
    subjects = Subject.objects.filter(professor=request.user)
    assignments = Assignment.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    total_students = StudentProfile.objects.filter(enrolled_subjects__in=subjects).distinct().count()
    
    return render(request, 'core/professor/dashboard.html', {
        'subjects': subjects,
        'assignments': assignments,
        'total_students': total_students,
        'username': request.user.get_full_name() or request.user.username,
    })

@professor_required
def professor_subjects(request):
    subjects = Subject.objects.filter(professor=request.user)
    return render(request, 'core/professor/subjects.html', {
        'subjects': subjects,
    })

@professor_required
def professor_students(request):
    subjects = Subject.objects.filter(professor=request.user)
    student_qs = StudentProfile.objects.filter(enrolled_subjects__in=subjects).distinct().select_related('user', 'course')
    
    subject_filter = request.GET.get('subject')
    if subject_filter:
        student_qs = student_qs.filter(enrolled_subjects__id=subject_filter)
        
    return render(request, 'core/professor/students.html', {
        'students': student_qs,
        'subjects': subjects,
    })

@professor_required
def professor_attendance(request):
    subjects = Subject.objects.filter(professor=request.user)
    selected_subject_id = request.GET.get('subject') or ''
    selected_subject = None
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        date = request.POST.get('date')
        
        try:
            subject = Subject.objects.get(id=subject_id, professor=request.user)
            students = StudentProfile.objects.filter(enrolled_subjects=subject)
            
            for student in students:
                status = request.POST.get(f'status_{student.id}', 'absent')
                Attendance.objects.update_or_create(
                    student=student, 
                    subject=subject, 
                    date=date,
                    defaults={'status': status, 'marked_by': request.user}
                )
            messages.success(request, 'Attendance marked successfully!')
            return redirect(f"{reverse('core:professor_attendance')}?subject={subject_id}")
        except Subject.DoesNotExist:
            messages.error(request, 'Invalid subject.')
    else:
        if selected_subject_id:
            try:
                selected_subject = Subject.objects.get(id=selected_subject_id, professor=request.user)
            except Subject.DoesNotExist:
                selected_subject = None
                selected_subject_id = ''
            
    return render(request, 'core/professor/attendance.html', {
        'subjects': subjects,
        'selected_subject_id': selected_subject_id,
        'selected_subject': selected_subject,
    })

@professor_required
def get_students_for_attendance(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id, professor=request.user)
        students = StudentProfile.objects.filter(enrolled_subjects=subject)
        return render(request, 'core/professor/partials/student_list.html', {'students': students})
    except Subject.DoesNotExist:
        return render(request, 'core/professor/partials/error.html', {'message': 'Subject not found'})

@professor_required
def professor_assignments(request):
    subjects = Subject.objects.filter(professor=request.user)
    assignments_list = Assignment.objects.filter(created_by=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        subject_id = request.POST.get('subject_id')
        due_date = request.POST.get('due_date')
        max_marks = request.POST.get('max_marks', 10)
        
        try:
            subject = Subject.objects.get(id=subject_id, professor=request.user)
            Assignment.objects.create(
                title=title,
                description=description,
                subject=subject,
                due_date=due_date,
                created_by=request.user,
                max_marks=max_marks
            )
            messages.success(request, 'Assignment created successfully!')
            return redirect('core:professor_assignments')
        except Subject.DoesNotExist:
            messages.error(request, 'Invalid subject.')
            
    return render(request, 'core/professor/assignments.html', {
        'subjects': subjects,
        'assignments': assignments_list,
    })

@professor_required
def professor_notifications(request):
    notifs = Notification.objects.filter(created_by=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        message_text = request.POST.get('message')
        notif_type = request.POST.get('notif_type', 'general')
        
        Notification.objects.create(
            title=title,
            message=message_text,
            notif_type=notif_type,
            target_role='student',
            created_by=request.user
        )
        messages.success(request, 'Notification sent to students successfully!')
        return redirect('core:professor_notifications')
        
    return render(request, 'core/professor/notifications.html', {
        'notifications': notifs,
    })

@professor_required
def assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=request.user)
    submissions = assignment.submissions.select_related('student__user').all()
    
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        marks = request.POST.get('marks')
        feedback = request.POST.get('feedback')
        
        try:
            submission = AssignmentSubmission.objects.get(id=submission_id, assignment=assignment)
            submission.marks_obtained = marks
            submission.feedback = feedback
            submission.save()
            messages.success(request, f'Graded submission for {submission.student.user.get_full_name()} successfully.')
        except AssignmentSubmission.DoesNotExist:
            messages.error(request, 'Submission not found.')
            
        return redirect('core:assignment_submissions', assignment_id=assignment.id)
        
    return render(request, 'core/professor/assignment_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
    })

@professor_required
def professor_events(request):
    events_list = Event.objects.all().order_by('-event_date')
    return render(request, 'core/professor/events.html', {'events': events_list})

@professor_required
def professor_exams(request):
    my_subjects = Subject.objects.filter(professor=request.user)
    exams_list = ExamTimeTable.objects.filter(subject__in=my_subjects).order_by('date', 'start_time')
    return render(request, 'core/professor/exams.html', {'exams': exams_list})

@professor_required
def professor_results_list(request):
    my_subjects = Subject.objects.filter(professor=request.user)
    my_exams = ExamTimeTable.objects.filter(subject__in=my_subjects).order_by('-date')
    return render(request, 'core/professor/results_list.html', {'exams': my_exams})

@professor_required
def add_marks(request, exam_id):
    exam = get_object_or_404(ExamTimeTable, id=exam_id, subject__professor=request.user)
    
    students = StudentProfile.objects.filter(enrolled_subjects=exam.subject).select_related('user')
    
    if request.method == 'POST':
        for student in students:
            marks = request.POST.get(f'marks_{student.id}')
            remarks = request.POST.get(f'remarks_{student.id}')
            
            if marks:
                result, created = Result.objects.get_or_create(
                    student=student, 
                    exam=exam,
                    defaults={'marks_obtained': marks, 'remarks': remarks}
                )
                if not created:
                    result.marks_obtained = marks
                    result.remarks = remarks
                    try:
                        m = float(marks)
                        if m >= 90: grade = 'O'
                        elif m >= 80: grade = 'A+'
                        elif m >= 70: grade = 'A'
                        elif m >= 60: grade = 'B+'
                        elif m >= 50: grade = 'B'
                        elif m >= 40: grade = 'C'
                        else: grade = 'F'
                        result.grade = grade
                    except ValueError:
                        pass
                    result.save()
                    
        messages.success(request, 'Marks saved successfully.')
        return redirect('core:professor_results_list')
        
    existing_results = {r.student_id: r for r in Result.objects.filter(exam=exam)}
    
    context = {
        'exam': exam,
        'students': students,
        'existing_results': existing_results,
    }
    return render(request, 'core/professor/add_marks.html', context)


# ---- STUDENT VIEWS ----

def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:student_login')
        if request.user.role != 'student':
            return redirect('core:student_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

@student_required
def student_dashboard(request):
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('core:logout')

    subjects = profile.enrolled_subjects.all()
    total_classes = 0
    present_classes = 0
    for subj in subjects:
        att = Attendance.objects.filter(student=profile, subject=subj)
        total_classes += att.count()
        present_classes += att.filter(status='present').count()

    attendance_pct = 0
    if total_classes > 0:
        attendance_pct = round((present_classes / total_classes) * 100, 1)

    recent_results = Result.objects.filter(student=profile).order_by(
        '-published_at'
    )[:5]
    notifications = Notification.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]

    return render(request, 'core/student/dashboard.html', {
        'profile': profile,
        'subjects': subjects,
        'attendance_pct': attendance_pct,
        'total_classes': total_classes,
        'present_classes': present_classes,
        'recent_results': recent_results,
        'notifications': notifications,
    })

@student_required
def student_subjects(request):
    profile = request.user.student_profile
    subj_list = profile.enrolled_subjects.all()
    return render(request, 'core/student/subjects.html', {
        'profile': profile,
        'subjects': subj_list,
    })

@student_required
def student_attendance(request):
    profile = request.user.student_profile
    filter_subj = request.GET.get('subject')
    subj_list = profile.enrolled_subjects.all()
    att_data = []
    for subj in subj_list:
        if filter_subj and str(subj.id) != filter_subj:
            continue
        records = Attendance.objects.filter(
            student=profile, subject=subj
        ).order_by('-date')
        total = records.count()
        present = records.filter(status='present').count()
        pct = round((present / total * 100), 1) if total > 0 else 0
        att_data.append({
            'subject': subj,
            'records': records,
            'total': total,
            'present': present,
            'absent': total - present,
            'percentage': pct,
        })
    return render(request, 'core/student/attendance.html', {
        'profile': profile,
        'att_data': att_data,
        'subjects': subj_list,
        'filter_subj': filter_subj,
    })

@student_required
def student_notifications(request):
    profile = request.user.student_profile
    notifs = Notification.objects.filter(
        is_active=True
    ).order_by('-created_at')
    return render(request, 'core/student/notifications.html', {
        'profile': profile,
        'notifications': notifs,
    })

@student_required
def student_assignments(request):
    profile = request.user.student_profile
    subj_ids = profile.enrolled_subjects.values_list('id', flat=True)
    assigns = Assignment.objects.filter(
        subject__in=subj_ids
    ).order_by('-created_at')
    
    my_submissions = AssignmentSubmission.objects.filter(student=profile).values_list('assignment_id', flat=True)
    
    return render(request, 'core/student/assignments.html', {
        'profile': profile,
        'assignments': assigns,
        'my_submissions': my_submissions,
    })

@student_required
def submit_assignment(request, assignment_id):
    profile = request.user.student_profile
    assignment = get_object_or_404(Assignment, id=assignment_id, subject__in=profile.enrolled_subjects.all())
    
    try:
        submission = AssignmentSubmission.objects.get(assignment=assignment, student=profile)
        is_submitted = True
    except AssignmentSubmission.DoesNotExist:
        submission = None
        is_submitted = False
        
    if request.method == 'POST' and not is_submitted:
        text = request.POST.get('submission_text')
        file = request.FILES.get('submission_file')
        
        AssignmentSubmission.objects.create(
            assignment=assignment,
            student=profile,
            submission_text=text,
            submission_file=file
        )
        messages.success(request, 'Assignment submitted successfully!')
        return redirect('core:student_assignments')
        
    return render(request, 'core/student/submit_assignment.html', {
        'profile': profile,
        'assignment': assignment,
        'submission': submission,
        'is_submitted': is_submitted,
    })

@student_required
def student_exams(request):
    profile = request.user.student_profile
    subj_ids = profile.enrolled_subjects.values_list('id', flat=True)
    exam_list = ExamTimeTable.objects.filter(
        subject__in=subj_ids
    ).order_by('date')
    return render(request, 'core/student/exams.html', {
        'profile': profile,
        'exams': exam_list,
    })

@student_required
def student_results(request):
    profile = request.user.student_profile
    result_list = Result.objects.filter(
        student=profile
    ).select_related('exam', 'exam__subject').order_by('-published_at')
    total_marks = sum(r.marks_obtained for r in result_list)
    avg_marks = round(
        total_marks / len(result_list), 2
    ) if result_list else 0
    return render(request, 'core/student/results.html', {
        'profile': profile,
        'results': result_list,
        'avg_marks': avg_marks,
    })

@student_required
def student_subject_results(request):
    profile = request.user.student_profile
    subject_results = SubjectResult.objects.filter(student=profile).select_related('subject').order_by('subject__name')
    
    # Calculate overall statistics
    total_results = subject_results.count()
    passed_results = subject_results.filter(result_status='Pass').count()
    failed_results = subject_results.filter(result_status='Fail').count()
    backlog_results = subject_results.filter(result_status='Backlog').count()
    
    # Calculate GPA-like score (simplified)
    total_percentage = sum(result.percentage for result in subject_results)
    overall_percentage = round(total_percentage / total_results, 2) if total_results > 0 else 0
    
    context = {
        'profile': profile,
        'subject_results': subject_results,
        'total_results': total_results,
        'passed_results': passed_results,
        'failed_results': failed_results,
        'backlog_results': backlog_results,
        'overall_percentage': overall_percentage,
    }
    return render(request, 'core/student/subject_results.html', context)


# ---- AJAX VIEWS FOR DYNAMIC RESULT FORM ----

from django.http import JsonResponse

@admin_required
def ajax_get_semesters(request):
    course_id = request.GET.get('course_id')
    if course_id:
        semesters = Semester.objects.filter(course_id=course_id).values('id', 'name')
        return JsonResponse(list(semesters), safe=False)
    return JsonResponse([], safe=False)

@admin_required
def ajax_get_subjects(request):
    semester_id = request.GET.get('semester_id')
    if semester_id:
        subjects = Subject.objects.filter(semester_id=semester_id).values('id', 'name', 'code')
        return JsonResponse(list(subjects), safe=False)
    return JsonResponse([], safe=False)

@admin_required
def ajax_get_students(request):
    course_id = request.GET.get('course_id')
    semester_id = request.GET.get('semester_id')
    if course_id and semester_id:
        students = StudentProfile.objects.filter(
            course_id=course_id, semester_id=semester_id
        ).select_related('user').values('id', 'roll_number', name=models.F('user__first_name') + ' ' + models.F('user__last_name'))
        student_list = []
        for student in students:
            student_list.append({
                'id': student['id'],
                'name': f"{student['roll_number']} - {student['name']}"
            })
        return JsonResponse(student_list, safe=False)
    return JsonResponse([], safe=False)


# ---- DYNAMIC RESULT FORM VIEW ----

@admin_required
def dynamic_result_form(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject_id = request.POST.get('subject_id')
        theory_max = request.POST.get('theory_max')
        theory_min = request.POST.get('theory_min')
        theory_marks = request.POST.get('theory_marks')
        practical_max = request.POST.get('practical_max')
        practical_min = request.POST.get('practical_min')
        practical_marks = request.POST.get('practical_marks')
        internal_marks = request.POST.get('internal_marks')
        result_status = request.POST.get('result_status')
        
        student = get_object_or_404(StudentProfile, pk=student_id)
        subject = get_object_or_404(Subject, pk=subject_id)
        
        # Create or update SubjectResult
        subject_result, created = SubjectResult.objects.get_or_create(
            student=student,
            subject=subject,
            defaults={
                'theory_max': theory_max,
                'theory_min': theory_min,
                'theory_marks': theory_marks,
                'practical_max': practical_max,
                'practical_min': practical_min,
                'practical_marks': practical_marks,
                'internal_marks': internal_marks,
                'result_status': result_status,
            }
        )
        
        if not created:
            subject_result.theory_max = theory_max
            subject_result.theory_min = theory_min
            subject_result.theory_marks = theory_marks
            subject_result.practical_max = practical_max
            subject_result.practical_min = practical_min
            subject_result.practical_marks = practical_marks
            subject_result.internal_marks = internal_marks
            subject_result.result_status = result_status
            subject_result.save()
        
        messages.success(request, f'Result {"created" if created else "updated"} successfully!')
        return redirect('core:dynamic_result_form')
    
    courses = Course.objects.all()
    return render(request, 'core/admin/dynamic_result_form.html', {
        'courses': courses,
    })
