def exam_page(request):
    from .models import ExamTimeTable
    exams = ExamTimeTable.objects.all().order_by('date', 'start_time')
    return render(request, 'core/exam.html', {'exams': exams})


def result_search(request):
    # Generate captcha
    if 'captcha_answer' not in request.session or request.method == 'GET':
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        request.session['captcha_answer'] = num1 + num2
        captcha_text = f"{num1} + {num2}"
    