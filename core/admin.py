from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.db import models
from .models import (
    User, Course, Semester, Subject, StudentProfile, ProfessorProfile,
    Attendance, Assignment, ExamType, ExamTimeTable, Result,
    Notification, Event, AssignmentSubmission, AdmissionEnquiry, SubjectResult
)

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'code', 'category', 'duration')
    list_filter = ('category',)
    search_fields = ('course_name', 'code')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('semester_name', 'stream')
    list_filter = ('stream',)
    search_fields = ('semester_name', 'stream__stream_name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'code', 'semester', 'professor', 'credits')
    list_filter = ('semester__stream__course', 'professor')
    search_fields = ('subject_name', 'code', 'semester__semester_name')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'user', 'course', 'semester', 'admission_year', 'enrollment_number', 'view_profile_photo')
    list_filter = ('course', 'semester', 'admission_year', 'admission_date')
    search_fields = ('roll_number', 'user__username', 'user__first_name', 'user__last_name',
                     'user__email', 'enrollment_number', 'father_name', 'mother_name')
    readonly_fields = ('admission_date', 'user')
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'roll_number', 'enrollment_number', 'admission_year')
        }),
        ('Academic Details', {
            'fields': ('course', 'semester', 'enrolled_subjects')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'father_name', 'mother_name', 'address', 'description')
        }),
        ('Admission Details', {
            'fields': ('admission_date',)
        }),
    )
    filter_horizontal = ('enrolled_subjects',)

    def view_profile_photo(self, obj):
        if obj.user.profile_photo:
            return format_html('<a href="{}" target="_blank" class="btn btn-sm btn-outline-primary">📷 View Photo</a>', obj.user.profile_photo.url)
        return "No photo"

    view_profile_photo.short_description = "Profile Photo"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('student-search/', self.admin_site.admin_view(self.student_search), name='student_search'),
            path('<int:student_id>/details/', self.admin_site.admin_view(self.student_details), name='student_details'),
        ]
        return custom_urls + urls

    def student_details(self, request, student_id):
        student = get_object_or_404(StudentProfile.objects.select_related('user', 'course', 'semester'), pk=student_id)

        data = {
            'roll_number': student.roll_number,
            'full_name': student.user.get_full_name(),
            'email': student.user.email,
            'phone': student.user.phone,
            'enrollment_number': student.enrollment_number,
            'course': f"{student.course.name} ({student.course.code})" if student.course else None,
            'semester': student.semester.name if student.semester else None,
            'admission_year': student.admission_year,
            'admission_date': student.admission_date.strftime('%Y-%m-%d') if student.admission_date else None,
            'date_of_birth': student.date_of_birth.strftime('%Y-%m-%d') if student.date_of_birth else None,
            'father_name': student.father_name,
            'mother_name': student.mother_name,
            'address': student.address,
            'profile_photo': student.user.profile_photo.url if student.user.profile_photo else None,
            'enrolled_subjects': [subject.name for subject in student.enrolled_subjects.all()]
        }

        return JsonResponse(data)

    def student_search(self, request):
        query = request.GET.get('q', '')
        students = StudentProfile.objects.select_related('user', 'course', 'semester')

        if query:
            students = students.filter(
                models.Q(roll_number__icontains=query) |
                models.Q(user__first_name__icontains=query) |
                models.Q(user__last_name__icontains=query) |
                models.Q(user__email__icontains=query) |
                models.Q(enrollment_number__icontains=query) |
                models.Q(father_name__icontains=query) |
                models.Q(mother_name__icontains=query)
            )

        context = {
            'students': students[:50],  # Limit to 50 results
            'query': query,
            'title': 'Student Search',
        }
        return render(request, 'admin/core/studentprofile/student_search.html', context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['student_search_url'] = 'student-search/'
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(ProfessorProfile)
class ProfessorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'date_of_joining')
    list_filter = ('department',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status', 'marked_by')
    list_filter = ('status', 'date', 'subject__semester__stream__course')
    search_fields = ('student__user__username', 'student__roll_number', 'subject__subject_name')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'due_date', 'created_by', 'max_marks')
    list_filter = ('subject__semester__stream__course', 'due_date')
    search_fields = ('title', 'subject__subject_name')

@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ExamTimeTable)
class ExamTimeTableAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester', 'subject', 'exam_type', 'date', 'total_marks')
    list_filter = ('exam_type', 'date', 'semester__stream__course')
    search_fields = ('name', 'subject__subject_name', 'semester__semester_name')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'grade')
    list_filter = ('exam__exam_type', 'grade', 'exam__date')
    search_fields = ('student__user__username', 'student__roll_number', 'exam__subject__subject_name')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notif_type', 'target_role', 'created_by', 'is_active')
    list_filter = ('notif_type', 'target_role', 'is_active')
    search_fields = ('title', 'message')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'venue', 'created_by')
    list_filter = ('event_date',)
    search_fields = ('title', 'description', 'venue')

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'marks_obtained')
    list_filter = ('submitted_at', 'assignment__subject')
    search_fields = ('assignment__title', 'student__user__username')

@admin.register(AdmissionEnquiry)
class AdmissionEnquiryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'mobile', 'course', 'status', 'submitted_at', 'view_documents')
    list_filter = ('status', 'course', 'admission_year', 'submitted_at', 'gender')
    search_fields = ('full_name', 'email', 'mobile', 'course', 'father_name', 'mother_name',
                     'previous_school', 'qualification')
    readonly_fields = ('submitted_at',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'dob', 'gender', 'father_name', 'mother_name')
        }),
        ('Contact Details', {
            'fields': ('mobile', 'email', 'address')
        }),
        ('Academic Qualification', {
            'fields': ('qualification', 'passing_year', 'marks', 'previous_school')
        }),
        ('Course Information', {
            'fields': ('course', 'admission_year')
        }),
        ('Documents', {
            'fields': ('photo', 'marksheet', 'id_proof')
        }),
        ('Status', {
            'fields': ('status', 'submitted_at')
        }),
    )

    def view_documents(self, obj):
        documents = []
        if obj.photo:
            documents.append(f'<a href="{obj.photo.url}" target="_blank" class="btn btn-sm btn-outline-primary" style="margin: 2px;">📷 Photo</a>')
        if obj.marksheet:
            documents.append(f'<a href="{obj.marksheet.url}" target="_blank" class="btn btn-sm btn-outline-success" style="margin: 2px;">📄 Marksheet</a>')
        if obj.id_proof:
            documents.append(f'<a href="{obj.id_proof.url}" target="_blank" class="btn btn-sm btn-outline-warning" style="margin: 2px;">🆔 ID Proof</a>')

        if documents:
            return format_html(' '.join(documents))
        return "No documents"

    view_documents.short_description = "Documents"

@admin.register(SubjectResult)
class SubjectResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'total_marks', 'percentage', 'result_status')
    list_filter = ('result_status', 'subject__semester__stream__course', 'created_at')
    search_fields = ('student__user__username', 'student__roll_number', 'subject__subject_name')
    readonly_fields = ('total_marks', 'percentage', 'created_at')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['bulk_entry_url'] = 'bulk-entry/'
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-entry/', self.admin_site.admin_view(self.bulk_result_entry), name='subjectresult_bulk_entry'),
            path('get-semesters/<int:course_id>/', self.admin_site.admin_view(self.get_semesters), name='get_semesters'),
            path('get-subjects/<int:semester_id>/', self.admin_site.admin_view(self.get_subjects), name='get_subjects'),
            path('get-students/<int:subject_id>/', self.admin_site.admin_view(self.get_students), name='get_students'),
            path('save-results/', self.admin_site.admin_view(self.save_results), name='save_results'),
        ]
        return custom_urls + urls

    def bulk_result_entry(self, request):
        courses = Course.objects.all()
        context = {
            'courses': courses,
            'title': 'Bulk Result Entry',
        }
        return render(request, 'admin/core/subjectresult/bulk_entry.html', context)

    def get_semesters(self, request, course_id):
        semesters = Semester.objects.filter(course_id=course_id).values('id', 'name')
        return JsonResponse(list(semesters), safe=False)

    def get_subjects(self, request, semester_id):
        subjects = Subject.objects.filter(semester_id=semester_id).values('id', 'name', 'code')
        return JsonResponse(list(subjects), safe=False)

    def get_students(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        students = StudentProfile.objects.filter(
            course=subject.semester.course,
            enrolled_subjects=subject
        ).select_related('user')

        student_data = []
        for student in students:
            # Check if result already exists
            existing_result = SubjectResult.objects.filter(
                student=student, subject=subject
            ).first()

            student_data.append({
                'id': student.id,
                'roll_number': student.roll_number,
                'name': student.user.get_full_name(),
                'existing_result': {
                    'theory_marks': existing_result.theory_marks if existing_result else 0,
                    'theory_max': existing_result.theory_max if existing_result else 100,
                    'theory_min': existing_result.theory_min if existing_result else 35,
                    'practical_marks': existing_result.practical_marks if existing_result else 0,
                    'practical_max': existing_result.practical_max if existing_result else 50,
                    'practical_min': existing_result.practical_min if existing_result else 15,
                    'internal_marks': existing_result.internal_marks if existing_result else 0,
                    'result_status': existing_result.result_status if existing_result else 'Pass',
                } if existing_result else None
            })

        return JsonResponse({
            'students': student_data,
            'subject_name': subject.name
        })

    @method_decorator(csrf_exempt)
    def save_results(self, request):
        if request.method == 'POST':
            import json
            data = json.loads(request.body)
            subject_id = data['subject_id']
            results = data['results']

            subject = get_object_or_404(Subject, id=subject_id)

            for result_data in results:
                student_id = result_data['student_id']
                student = get_object_or_404(StudentProfile, id=student_id)

                theory_marks = int(result_data['theory_marks'])
                practical_marks = int(result_data['practical_marks'])
                internal_marks = int(result_data['internal_marks'])
                theory_max = int(result_data['theory_max'])
                practical_max = int(result_data['practical_max'])
                theory_min = int(result_data['theory_min'])
                practical_min = int(result_data['practical_min'])
                result_status = result_data['result_status']

                # Save or update result
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
                    subject_result.save()  # This will trigger the save method to calculate totals

            return JsonResponse({'success': True, 'message': 'Results saved successfully'})

        return JsonResponse({'success': False, 'message': 'Invalid request method'})

admin.site.site_header = "SRMS Result"
admin.site.site_title = "SRMS Result Admin Portal"
admin.site.index_title = "Welcome to SRMS Result Portal"