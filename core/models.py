from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


class Course(models.Model):
    course_name = models.CharField(max_length=100)
    # Keeping some old fields if needed by templates, but making them optional
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    category = models.CharField(max_length=50, default='Other')
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=50, default='3 Years')
    total_semesters = models.IntegerField(default=6, help_text="Total number of semesters for this course")
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def name(self):
        return self.course_name

    def __str__(self):
        return self.course_name


class Stream(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='streams')
    stream_name = models.CharField(max_length=100)
    
    @property
    def name(self):
        return self.stream_name

    def __str__(self):
        return f"{self.course.course_name} - {self.stream_name}"


class AdmissionYear(models.Model):
    year = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.year)


class Semester(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='semesters')
    semester_name = models.CharField(max_length=100)
    
    @property
    def name(self):
        return self.semester_name

    def __str__(self):
        return f"{self.stream.stream_name} - {self.semester_name}"


class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    subject_name = models.CharField(max_length=200)
    
    theory_max = models.IntegerField(default=100)
    theory_min = models.IntegerField(default=35)
    practical_max = models.IntegerField(default=50)
    practical_min = models.IntegerField(default=15)
    
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    professor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='teaching_subjects', limit_choices_to={'role': 'professor'}
    )
    credits = models.IntegerField(default=3)
    image = models.ImageField(upload_to='subject_images/', blank=True, null=True)
    description = models.TextField(blank=True)
    
    @property
    def name(self):
        return self.subject_name

    def __str__(self):
        return f"{self.subject_name} ({self.semester.semester_name})"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='students')
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, related_name='students')
    admission_year = models.ForeignKey(AdmissionYear, on_delete=models.SET_NULL, null=True, related_name='students')
    
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True)
    enrolled_subjects = models.ManyToManyField(Subject, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    admission_date = models.DateField(auto_now_add=True)
    
    enrollment_number = models.CharField(max_length=50, blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name()}"


class Marks(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')
    theory_marks = models.IntegerField(default=0)
    practical_marks = models.IntegerField(default=0)
    internal_marks = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject')
        verbose_name_plural = "Marks"

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.subject_name}"


class ProfessorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professor_profile')
    department = models.CharField(max_length=100, blank=True)
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    passing_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'), 
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Leave', 'Leave')
    ]
    attendance_id = models.CharField(max_length=20, unique=True, blank=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    lecture_no = models.CharField(max_length=50, default="1st lecture")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present')
    remarks = models.CharField(max_length=255, blank=True, null=True)
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='attendance_marked'
    )

    class Meta:
        unique_together = ['student', 'subject', 'date', 'lecture_no']

    def save(self, *args, **kwargs):
        if not self.attendance_id:
            # We'll generate it after saving by updating it or using a transaction.
            # But simpler: just prefix 'ATT' to the ID after first save.
            pass
        super().save(*args, **kwargs)
        if not self.attendance_id:
            self.attendance_id = f"ATT{self.id:04d}"
            # Use update to avoid recursive save()
            Attendance.objects.filter(id=self.id).update(attendance_id=self.attendance_id)

    def __str__(self):
        return f"{self.attendance_id} - {self.student} - {self.subject} - {self.date} - {self.status}"


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    due_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    max_marks = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.title} - {self.subject.name}"


class ExamType(models.Model):
    name = models.CharField(max_length=100) # e.g. Internal Exam, Main Exam
    
    def __str__(self):
        return self.name

class ExamTimeTable(models.Model):
    name = models.CharField(max_length=200, blank=True, default='')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_marks = models.IntegerField(default=100)
    room = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def duration_hours(self):
        from datetime import datetime, date
        start = datetime.combine(date.today(), self.start_time)
        end = datetime.combine(date.today(), self.end_time)
        diff = end - start
        hours = diff.total_seconds() / 3600
        if hours <= 0:
            return "0 Hours"
        if hours.is_integer():
            return f"{int(hours)} Hours"
        return f"{hours:.1f} Hours"

    def __str__(self):
        return f"{self.exam_type.name} - {self.subject.name} ({self.date})"


class Result(models.Model):
    GRADE_CHOICES = [
        ('O', 'Outstanding'), ('A+', 'Excellent'), ('A', 'Very Good'),
        ('B+', 'Good'), ('B', 'Above Average'), ('C', 'Average'),
        ('F', 'Fail'),
    ]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='results')
    exam = models.ForeignKey(ExamTimeTable, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True)
    remarks = models.TextField(blank=True)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'exam']

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.marks_obtained}"


class Notification(models.Model):
    NOTIF_TYPE = [
        ('general', 'General'),
        ('exam', 'Exam'),
        ('result', 'Result'),
        ('assignment', 'Assignment'),
        ('event', 'Event'),
    ]
    title = models.CharField(max_length=200)
    message = models.TextField()
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE, default='general')
    target_role = models.CharField(
        max_length=20,
        choices=[('all', 'All'), ('student', 'Students'), ('professor', 'Professors')],
        default='all'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateField()
    venue = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='submissions')
    submission_file = models.FileField(upload_to='submissions/', null=True, blank=True)
    submission_text = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.assignment.title}"

class StudentResult(models.Model):
    COURSE_CHOICES = [
        ('BCA', 'Bachelor of Computer Applications (BCA)'),
        ('MCA', 'Master of Computer Applications (MCA)'),
        ('MBA', 'Master of Business Administration (MBA)'),
    ]
    STATUS_CHOICES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
    ]
    EXAM_CHOICES = [
        ('SEP 2025 Special Exam', 'SEP 2025 Special Exam'),
        ('APR 2025 Regular Exam', 'APR 2025 Regular Exam'),
        ('DEC 2024 Arrear Exam', 'DEC 2024 Arrear Exam'),
    ]
    
    exam_name = models.CharField(max_length=100, choices=EXAM_CHOICES, default='APR 2025 Regular Exam')
    student_name = models.CharField(max_length=200)
    roll_number = models.CharField(max_length=50, unique=True)
    course = models.CharField(max_length=10, choices=COURSE_CHOICES)
    centre_code = models.CharField(max_length=50, blank=True, null=True, help_text="Study Centre Code (Optional)")
    
    # Store marks as formatted text. Example:
    # C Programming: 85
    # DBMS: 90
    subject_marks = models.TextField(
        help_text="Enter marks one per line in format 'Subject Name: Marks'. E.g., 'Java: 85'"
    )
    
    total_marks = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.roll_number} - {self.student_name} ({self.course})"


class Timetable(models.Model):
    COURSE_CHOICES = [
        ('BCA', 'BCA'),
        ('MCA', 'MCA'),
        ('MBA', 'MBA'),
    ]
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    course_name = models.CharField(max_length=10, choices=COURSE_CHOICES)
    subject_name = models.CharField(max_length=100)
    day = models.CharField(max_length=15, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. 2 Hours")
    faculty_name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=50)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.course_name} - {self.subject_name} ({self.day} {self.start_time})"


class ExamSchedule(models.Model):
    COURSE_CHOICES = [
        ('BCA', 'BCA'),
        ('MCA', 'MCA'),
        ('MBA', 'MBA'),
    ]
    EXAM_CHOICES = [
        ('Mid Term', 'Mid Term'),
        ('Final Exam', 'Final Exam'),
    ]
    course_name = models.CharField(max_length=10, choices=COURSE_CHOICES)
    exam_name = models.CharField(max_length=50, choices=EXAM_CHOICES)
    subject_name = models.CharField(max_length=100)
    exam_date = models.DateField()
    exam_time = models.TimeField()
    duration = models.CharField(max_length=50, help_text="e.g. 2 Hours, 3 Hours")
    room_number = models.CharField(max_length=50)

    class Meta:
        ordering = ['exam_date', 'exam_time']

    def __str__(self):
        return f"{self.course_name} - {self.exam_name} - {self.subject_name}"


class AdmissionEnquiry(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    
    full_name = models.CharField(max_length=200)
    dob = models.DateField()
    father_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    mobile = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    
    qualification = models.CharField(max_length=100)
    passing_year = models.IntegerField()
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    previous_school = models.CharField(max_length=200)
    
    course = models.CharField(max_length=100)
    admission_year = models.CharField(max_length=20)
    
    photo = models.ImageField(upload_to='admission_docs/', blank=True, null=True)
    marksheet = models.FileField(upload_to='admission_docs/', blank=True, null=True)
    id_proof = models.FileField(upload_to='admission_docs/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.course}"


class SubjectResult(models.Model):
    STATUS_CHOICES = [('Pass', 'Pass'), ('Fail', 'Fail'), ('Backlog', 'Backlog')]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='subject_results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_results')
    
    # Theory Marks
    theory_max = models.IntegerField(default=100)
    theory_min = models.IntegerField(default=35)
    theory_marks = models.IntegerField(default=0)
    
    # Practical Marks
    practical_max = models.IntegerField(default=50)
    practical_min = models.IntegerField(default=15)
    practical_marks = models.IntegerField(default=0)
    
    # Internal Marks
    internal_marks = models.IntegerField(default=0)
    
    # Calculated
    total_marks = models.IntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    result_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pass')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject')

    def save(self, *args, **kwargs):
        # Calculate total marks
        self.total_marks = self.theory_marks + self.practical_marks + self.internal_marks
        
        # Calculate percentage
        max_total = self.theory_max + self.practical_max + 25  # Assuming internal max is 25
        if max_total > 0:
            self.percentage = (self.total_marks / max_total) * 100
        else:
            self.percentage = 0
            
        # Auto-determine result status if not manually set
        if not self.result_status or self.result_status == 'Auto':
            if self.theory_marks >= self.theory_min and self.practical_marks >= self.practical_min:
                self.result_status = 'Pass'
            elif self.theory_marks >= self.theory_min and self.practical_marks < self.practical_min:
                self.result_status = 'Backlog'
            else:
                self.result_status = 'Fail'
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} - {self.result_status}"