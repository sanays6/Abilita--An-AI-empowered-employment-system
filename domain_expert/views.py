from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DomainExpert, InterviewQuestion
from users.models import TestResult
from InterviewSystem.decorators import role_required
from admin_panel.models import AptitudeQuestion
from .groq_service import generate_aptitude_questions
import json

def expert_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            expert = DomainExpert.objects.get(email=email)
            if expert.password == password:
                request.session['role'] = 'expert'
                request.session['expert_id'] = expert.id
                request.session['expert_name'] = expert.name
                return redirect('expert_dashboard')
            else:
                messages.error(request, 'Invalid password')
        except DomainExpert.DoesNotExist:
            messages.error(request, 'Domain Expert does not exist')
            
    return render(request, 'domain_expert/login.html')

@role_required('expert')
def expert_dashboard(request):
    expert_id = request.session.get('expert_id')
    expert = DomainExpert.objects.get(id=expert_id)
    questions = InterviewQuestion.objects.filter(domain=expert.domain)
    test_results = TestResult.objects.filter(domain=expert.domain).order_by('-created_at')
    
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        if question_text:
            InterviewQuestion.objects.create(
                domain=expert.domain,
                question_text=question_text
            )
            return redirect('expert_dashboard')

    return render(request, 'domain_expert/dashboard.html', {
        'expert': expert,
        'questions': questions,
        'test_results': test_results
    })

@role_required('expert')
def expert_view_performance(request, result_id):
    expert_id = request.session.get('expert_id')
    expert = DomainExpert.objects.get(id=expert_id)
    
    try:
        result = TestResult.objects.get(id=result_id, domain=expert.domain)
    except TestResult.DoesNotExist:
        messages.error(request, 'Performance record not found or unauthorized.')
        return redirect('expert_dashboard')
        
    details = []
    if result.result_json:
        try:
            rj = json.loads(result.result_json)
            details = rj.get('interview_evaluation', [])
        except json.JSONDecodeError:
            pass

    return render(request, 'domain_expert/view_performance.html', {
        'result': result,
        'details': details
    })

def expert_logout(request):
    if 'role' in request.session:
        del request.session['role']
    if 'expert_id' in request.session:
        del request.session['expert_id']
    if 'expert_name' in request.session:
        del request.session['expert_name']
    return redirect('expert_login')

@role_required('expert')
def delete_question(request, q_id):
    expert_id = request.session.get('expert_id')
    expert = DomainExpert.objects.get(id=expert_id)
    try:
        q = InterviewQuestion.objects.get(id=q_id, domain=expert.domain)
        q.delete()
        messages.success(request, "Question deleted successfully.")
    except InterviewQuestion.DoesNotExist:
        messages.error(request, "Question not found.")
        pass
    return redirect('expert_dashboard')

@role_required('expert')
def edit_question(request, q_id):
    expert_id = request.session.get('expert_id')
    expert = DomainExpert.objects.get(id=expert_id)
    if request.method == 'POST':
        try:
            q = InterviewQuestion.objects.get(id=q_id, domain=expert.domain)
            q.question_text = request.POST.get('question_text')
            q.save()
            messages.success(request, "Question updated successfully.")
        except InterviewQuestion.DoesNotExist:
            messages.error(request, "Question not found.")
            pass
    return redirect('expert_dashboard')

# --- APTITUDE GENERATION ---
@role_required('expert')
def expert_generate_aptitude(request):
    expert_id = request.session.get('expert_id')
    expert = DomainExpert.objects.get(id=expert_id)
    
    if request.method == 'POST':
        distributions = []
        for i in range(1, 4):
            topic = request.POST.get(f'topic_{i}')
            count = request.POST.get(f'count_{i}')
            if topic and count:
                try:
                    count_int = int(count)
                    if count_int > 0:
                        distributions.append({'topic': topic, 'count': count_int})
                except ValueError:
                    pass
                    
        success = generate_aptitude_questions(expert.domain, distributions)
        if success:
            messages.success(request, f'Successfully generated customized aptitude questions for {expert.domain}')
        else:
            messages.error(request, 'Failed to generate questions. Check API configuration or formatting.')
        
        return redirect('expert_list_aptitude')
    
    return render(request, 'domain_expert/generate_aptitude.html', {'expert_domain': expert.domain})

@role_required('expert')
def expert_list_aptitude(request):
    expert_id = request.session.get('expert_id')
    expert = DomainExpert.objects.get(id=expert_id)
    questions = AptitudeQuestion.objects.filter(domain=expert.domain).order_by('-id')
    return render(request, 'domain_expert/list_aptitude.html', {'questions': questions, 'expert_domain': expert.domain})

@role_required('expert')
def expert_delete_aptitude(request, q_id):
    expert_id = request.session.get('expert_id')
    expert = DomainExpert.objects.get(id=expert_id)
    try:
        q = AptitudeQuestion.objects.get(id=q_id, domain=expert.domain)
        q.delete()
        messages.success(request, 'Aptitude question deleted layout.')
    except AptitudeQuestion.DoesNotExist:
        messages.error(request, 'Question does not exist or unauthorized.')
    return redirect('expert_list_aptitude')

@role_required('expert')
def expert_edit_aptitude(request, q_id):
    expert_id = request.session.get('expert_id')
    expert = DomainExpert.objects.get(id=expert_id)
    if request.method == 'POST':
        try:
            q = AptitudeQuestion.objects.get(id=q_id, domain=expert.domain)
            q.question = request.POST.get('question', q.question)
            q.option1 = request.POST.get('option1', q.option1)
            q.option2 = request.POST.get('option2', q.option2)
            q.option3 = request.POST.get('option3', q.option3)
            q.option4 = request.POST.get('option4', q.option4)
            q.correct_answer = request.POST.get('correct_answer', q.correct_answer)
            q.save()
            messages.success(request, 'Question updated successfully.')
        except AptitudeQuestion.DoesNotExist:
            messages.error(request, 'Question not found or unauthorized.')
    return redirect('expert_list_aptitude')

@role_required('expert')
def expert_bulk_delete_aptitude(request):
    expert_id = request.session.get('expert_id')
    expert = DomainExpert.objects.get(id=expert_id)
    if request.method == 'POST':
        question_ids = request.POST.getlist('question_ids')
        if question_ids:
            count, _ = AptitudeQuestion.objects.filter(id__in=question_ids, domain=expert.domain).delete()
            messages.success(request, f'Successfully purged {count} Aptitude questions from repository.')
        else:
            messages.warning(request, 'No questions were selected for deletion.')
    return redirect('expert_list_aptitude')
