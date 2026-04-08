from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Public URLs
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('admission/', views.admission, name='admission'),
    path('courses/', views.courses_page, name='courses'),
    path('events/', views.events_page, name='events'),
    path('notifications/', views.notifications_page, name='notifications'),
    path('timetable/', views.timetable_page, name='timetable_page'),
    path('exam/', views.exam_page, name='exam'),
    path('result-search/', views.result_search, name='result_search'),
    path('admit-card-search/', views.admit_card_search, name='admit_card_search'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('student/login/', views.student_login, name='student_login'),
    path('professor/login/', views.professor_login, name='professor_login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),

    # Admin URLs
    path('admin/', views.admin_dashboard, name='admin_home'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/admissions/', views.manage_admissions, name='manage_admissions'),
    path('admin/courses/', views.manage_courses, name='manage_courses'),
    path('admin/courses/<int:pk>/update/', views.update_course, name='update_course'),
    path('admin/courses/<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('admin/subjects/', views.manage_subjects, name='manage_subjects'),
    path('admin/subjects/<int:pk>/update/', views.update_subject, name='update_subject'),
    path('admin/subjects/<int:pk>/delete/', views.delete_subject, name='delete_subject'),
    path('admin/students/', views.manage_students, name='manage_students'),
    path('admin/students/create/', views.create_student, name='create_student'),
    path('admin/students/<int:pk>/update/', views.update_student, name='update_student'),
    path('admin/students/<int:pk>/detail/', views.student_detail, name='student_detail'),
    path('admin/students/<int:pk>/delete/', views.delete_student, name='delete_student'),
    path('admin/professors/', views.manage_professors, name='manage_professors'),
    path('admin/professors/create/', views.create_professor, name='create_professor'),
    path('admin/professors/<int:pk>/update/', views.update_professor, name='update_professor'),
    path('admin/professors/<int:pk>/detail/', views.professor_detail, name='professor_detail'),
    path('admin/professors/<int:pk>/delete/', views.delete_professor, name='delete_professor'),
    path('admin/streams/', views.manage_streams, name='manage_streams'),
    path('admin/streams/<int:pk>/update/', views.update_stream, name='update_stream'),
    path('admin/streams/<int:pk>/delete/', views.delete_stream, name='delete_stream'),
    path('admin/events/', views.manage_events, name='manage_events'),
    path('admin/events/<int:pk>/update/', views.update_event, name='update_event'),
    path('admin/events/<int:pk>/delete/', views.delete_event, name='delete_event'),
    path('admin/notifications/', views.manage_notifications, name='manage_notifications'),
    path('admin/notifications/<int:pk>/update/', views.update_notification, name='update_notification'),
    path('admin/notifications/<int:pk>/delete/', views.delete_notification, name='delete_notification'),
    path('admin/exams/', views.manage_exams, name='manage_exams'),
    path('admin/exams/create/', views.create_exam, name='create_exam'),
    path('admin/exams/<int:pk>/update/', views.update_exam, name='update_exam'),
    path('admin/exams/<int:pk>/delete/', views.delete_exam, name='delete_exam'),
    
    # Timetable Management
    path('admin/timetable/', views.manage_timetable, name='manage_timetable'),
    path('admin/timetable/create/', views.create_timetable, name='create_timetable'),
    path('admin/timetable/<int:pk>/update/', views.update_timetable, name='update_timetable'),
    path('admin/timetable/<int:pk>/delete/', views.delete_timetable, name='delete_timetable'),
    path('admin/results/', views.manage_subject_results, name='manage_results'),
    path('admin/results/create/', views.create_result, name='create_result'),
    path('admin/results/<int:pk>/update/', views.update_result, name='update_result'),
    path('admin/results/<int:pk>/delete/', views.delete_subject_result, name='delete_result'),

    # Subject Results Management
    path('admin/subject-results/', views.manage_subject_results, name='manage_subject_results'),
    path('admin/subject-results/<int:pk>/delete/', views.delete_subject_result, name='delete_subject_result'),
    path('admin/assignments/', views.manage_assignments, name='manage_assignments'),
    path('admin/assignments/create/', views.create_assignment, name='create_assignment'),
    path('admin/assignments/<int:pk>/update/', views.update_assignment, name='update_assignment'),
    path('admin/assignments/<int:pk>/delete/', views.delete_assignment, name='delete_assignment'),
    path('admin/attendance/', views.manage_attendance, name='manage_attendance'),
    path('admin/attendance/save/', views.save_attendance, name='save_attendance'),
    path('admin/allotment/', views.manage_allotment, name='manage_allotment'),
    path('admin/allotment/assign/', views.assign_professor, name='assign_professor'),
    path('admin/allotment/enroll/', views.enroll_student, name='enroll_student'),

    # AJAX URLs
    path('admin/ajax/get-semesters/', views.ajax_get_semesters, name='ajax_get_semesters'),
    path('admin/ajax/get-subjects/', views.ajax_get_subjects, name='ajax_get_subjects'),
    path('admin/ajax/get-students/', views.ajax_get_students, name='ajax_get_students'),

    # Dynamic Result Form
    path('admin/dynamic-result/', views.dynamic_result_form, name='dynamic_result_form'),

    # Professor URLs
    path('professor/dashboard/', views.professor_dashboard, name='professor_dashboard'),
    path('professor/subjects/', views.professor_subjects, name='professor_subjects'),
    path('professor/students/', views.professor_students, name='professor_students'),
    path('professor/attendance/', views.professor_attendance, name='professor_attendance'),
    path('professor/attendance/students/<int:subject_id>/', views.get_students_for_attendance, name='get_students_for_attendance'),
    path('professor/assignments/', views.professor_assignments, name='professor_assignments'),
    path('professor/assignments/<int:assignment_id>/submissions/', views.assignment_submissions, name='assignment_submissions'),
    path('professor/notifications/', views.professor_notifications, name='professor_notifications'),
    path('professor/events/', views.professor_events, name='professor_events'),
    path('professor/exams/', views.professor_exams, name='professor_exams'),
    path('professor/results/', views.professor_results_list, name='professor_results_list'),
    path('professor/results/<int:exam_id>/add-marks/', views.add_marks, name='add_marks'),

    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/subjects/', views.student_subjects, name='student_subjects'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    path('student/notifications/', views.student_notifications, name='student_notifications'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('student/exams/', views.student_exams, name='student_exams'),
    path('student/results/', views.student_results, name='student_results'),
    path('student/subject-results/', views.student_subject_results, name='student_subject_results'),
]
