def exam_page(request):
    exams = ExamSchedule.objects.all().order_by('exam_date', 'exam_time')
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
 