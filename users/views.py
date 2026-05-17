import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password  # ✅ ADDED
from .models import User, TestResult
from domain_expert.models import DomainExpert, InterviewQuestion
from admin_panel.models import AptitudeQuestion
from InterviewSystem.decorators import role_required
from .groq_service import evaluate_resume, evaluate_interview
import pypdf
import time


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)

            # ✅ CHECK HASHED PASSWORD
            if user.password.startswith('pbkdf2_'):
                if not check_password(password, user.password):
                    messages.error(request, 'Invalid password')
                    return render(request, 'users/login.html')

            # ✅ OLD PLAIN TEXT PASSWORD
            else:
                if user.password == password:
                    # 🔄 AUTO-CONVERT TO HASHED
                    user.password = make_password(password)
                    user.save()
                else:
                    messages.error(request, 'Invalid password')
                    return render(request, 'users/login.html')

            # ✅ LOGIN SUCCESS (UNCHANGED)
            request.session['role'] = 'user'
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name

            # Check for incomplete test
            latest_test = TestResult.objects.filter(user=user).order_by('-created_at').first()
            if latest_test:
                try:
                    rj = json.loads(latest_test.result_json) if latest_test.result_json else {}

                    if 'aptitude_evaluation' in rj and 'interview_evaluation' not in rj:
                        request.session['current_test_id'] = latest_test.id
                        messages.info(request, 'Resuming your incomplete interview test.')
                        return redirect('start_interview')

                    elif 'ats_evaluation' in rj and 'aptitude_evaluation' not in rj:
                        request.session['current_test_id'] = latest_test.id
                        messages.info(request, 'Resuming your incomplete aptitude test.')
                        return redirect('start_aptitude')
                except Exception:
                    pass

            return redirect('user_dashboard')

        except User.DoesNotExist:
            messages.error(request, 'User does not exist')

    return render(request, 'users/login.html')


def user_signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        else:
            user = User.objects.create(
                name=name,
                email=email,
                password=make_password(password)  # ✅ HASHED PASSWORD
            )
            request.session['role'] = 'user'
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            return redirect('user_dashboard')

    return render(request, 'users/signup.html')


@role_required('user')
def user_dashboard(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    domains = DomainExpert.objects.values_list('domain', flat=True).distinct()
    recent_results = TestResult.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST':
        domain = request.POST.get('domain')
        resume = request.FILES.get('resume')

        if domain and resume:
            user.selected_domain = domain
            user.resume = resume
            user.save()

            text = ""
            try:
                reader = pypdf.PdfReader(user.resume.file)
                for page in reader.pages:
                    text += page.extract_text()
            except Exception as e:
                text = "Error parsing PDF."

            ats_res = evaluate_resume(text, domain)

            tr = TestResult.objects.create(
                user=user,
                domain=domain,
                result_json=json.dumps({"ats_evaluation": ats_res})
            )
            request.session['current_test_id'] = tr.id
            messages.success(request, 'Resume uploaded and evaluated by ATS! Proceed to the test.')
            return redirect('start_aptitude')

    return render(request, 'users/dashboard.html', {'user': user, 'domains': domains, 'recent_results': recent_results})


def user_logout(request):
    for key in ['role', 'user_id', 'user_name', 'current_test_id']:
        if key in request.session:
            del request.session[key]
    return redirect('user_login')


@role_required('user')
def start_aptitude(request):
    test_id = request.session.get('current_test_id')
    if not test_id:
        return redirect('user_dashboard')

    tr = TestResult.objects.get(id=test_id)
    questions = AptitudeQuestion.objects.filter(domain=tr.domain).order_by('?')[:20]

    if 'aptitude_start_time' not in request.session:
        request.session['aptitude_start_time'] = time.time()

    elapsed = time.time() - request.session['aptitude_start_time']
    remaining_time = int(max(0, (30 * 60) - elapsed))

    if request.method == 'POST' or remaining_time <= 0:
        score = 0
        apt_eval = []

        for q in questions:
            user_ans = request.POST.get(f'q_{q.id}', '')
            is_correct = (user_ans == q.correct_answer)
            if is_correct:
                score += 1

            apt_eval.append({
                'question': q.question,
                'user_answer': user_ans,
                'correct_answer': q.correct_answer,
                'is_correct': is_correct
            })

        tr.aptitude_score = score
        rj = json.loads(tr.result_json) if tr.result_json else {}
        rj['aptitude_evaluation'] = apt_eval
        tr.result_json = json.dumps(rj)
        tr.save()

        return redirect('start_interview')

    return render(request, 'users/aptitude_test.html', {'questions': questions, 'remaining_time': remaining_time})


@role_required('user')
def start_interview(request):
    test_id = request.session.get('current_test_id')
    if not test_id:
        return redirect('user_dashboard')

    tr = TestResult.objects.get(id=test_id)

    if 'interview_questions' not in request.session:
        qs = list(InterviewQuestion.objects.filter(domain=tr.domain).values('id', 'question_text'))
        request.session['interview_questions'] = qs
        request.session['current_q_index'] = 0
        request.session['interview_answers'] = []

    if 'interview_start_time' not in request.session:
        request.session['interview_start_time'] = time.time()

    elapsed = time.time() - request.session['interview_start_time']
    remaining_time = int(max(0, (30 * 60) - elapsed))

    qs = request.session['interview_questions']
    idx = request.session.get('current_q_index', 0)

    if idx >= len(qs) or len(qs) == 0 or remaining_time <= 0:
        return redirect('finish_interview')

    current_q = qs[idx]

    return render(request, 'users/interview.html', {
        'question': current_q,
        'q_num': idx + 1,
        'total_q': len(qs),
        'remaining_time': remaining_time
    })


@role_required('user')
def submit_interview_answer(request):
    if request.method == 'POST':
        answer_text = request.POST.get('answer_text')

        qs = request.session.get('interview_questions', [])
        idx = request.session.get('current_q_index', 0)
        answers = request.session.get('interview_answers', [])

        if idx < len(qs):
            answers.append({
                'question': qs[idx]['question_text'],
                'answer': answer_text
            })

            request.session['interview_answers'] = answers
            request.session['current_q_index'] = idx + 1

    return redirect('start_interview')


@role_required('user')
def finish_interview(request):
    test_id = request.session.get('current_test_id')
    if not test_id:
        return redirect('user_dashboard')

    tr = TestResult.objects.get(id=test_id)
    answers = request.session.get('interview_answers', [])

    evaluations = evaluate_interview(answers, tr.domain)

    avg_score = sum(ev.get('score', 0) for ev in evaluations) / len(evaluations) if evaluations else 0

    tr.interview_score = round(avg_score, 2)
    tr.total_score = round(((tr.aptitude_score / 20.0 * 100) + (tr.interview_score / 10.0 * 100)) / 2, 2) if len(answers) > 0 else 0

    rj = json.loads(tr.result_json) if tr.result_json else {}
    rj['interview_evaluation'] = evaluations
    tr.result_json = json.dumps(rj)
    tr.save()

    for key in ['interview_questions', 'current_q_index', 'interview_answers', 'current_test_id', 'aptitude_start_time', 'interview_start_time']:
        if key in request.session:
            del request.session[key]

    return redirect('user_result', result_id=tr.id)


@role_required('user')
def user_result(request, result_id):
    tr = TestResult.objects.get(id=result_id)

    rj = json.loads(tr.result_json) if tr.result_json else {}

    return render(request, 'users/result.html', {
        'result': tr,
        'details': rj.get('interview_evaluation', []),
        'ats_evaluation': rj.get('ats_evaluation', {}),
        'aptitude_eval': rj.get('aptitude_evaluation', [])
    })


@role_required('user')
def analyse_cv(request):
    from .groq_service import analyze_general_cv

    report = None
    if request.method == 'POST':
        resume_file = request.FILES.get('resume')
        if not resume_file:
            messages.error(request, 'Please upload a PDF resume.')
        else:
            text = ""
            try:
                reader = pypdf.PdfReader(resume_file.file)
                for page in reader.pages:
                    text += page.extract_text()
            except:
                messages.error(request, 'Error parsing PDF.')

            if text:
                report = analyze_general_cv(text)

    return render(request, 'users/analyse_cv.html', {'report': report})


@role_required('user')
def user_history(request):
    user = User.objects.get(id=request.session.get('user_id'))
    history = TestResult.objects.filter(user=user).order_by('-created_at')
    return render(request, 'users/history.html', {'history': history})# test github update