from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Admin
from users.models import User
from domain_expert.models import DomainExpert
from InterviewSystem.decorators import role_required

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            admin_user = Admin.objects.get(email=email)
            if admin_user.password == password:
                request.session['role'] = 'admin'
                request.session['admin_id'] = admin_user.id
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid password')
        except Admin.DoesNotExist:
            messages.error(request, 'Admin does not exist')
            
    return render(request, 'admin_panel/login.html')

@role_required('admin')
def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html')

@role_required('admin')
def admin_logout(request):
    if 'role' in request.session:
        del request.session['role']
    if 'admin_id' in request.session:
        del request.session['admin_id']
    return redirect('admin_login')

# --- USER MANAGEMENT ---
@role_required('admin')
def admin_list_users(request):
    users = User.objects.all()
    return render(request, 'admin_panel/users_list.html', {'users': users})

@role_required('admin')
def admin_view_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        # Could also fetch user's TestResults here to pass to template
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_list_users')
    return render(request, 'admin_panel/user_details.html', {'user': user})

# --- DOMAIN EXPERT MANAGEMENT ---
@role_required('admin')
def admin_list_experts(request):
    experts = DomainExpert.objects.all()
    return render(request, 'admin_panel/experts_list.html', {'experts': experts})

@role_required('admin')
def admin_add_expert(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        domain = request.POST.get('domain')
        
        if DomainExpert.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        else:
            DomainExpert.objects.create(name=name, email=email, password=password, domain=domain)
            messages.success(request, 'Domain Expert Added Successfuly')
            return redirect('admin_list_experts')

    return render(request, 'admin_panel/add_expert.html')

@role_required('admin')
def admin_edit_expert(request, expert_id):
    try:
        expert = DomainExpert.objects.get(id=expert_id)
    except DomainExpert.DoesNotExist:
        messages.error(request, 'Expert not found.')
        return redirect('admin_list_experts')
        
    if request.method == 'POST':
        expert.name = request.POST.get('name')
        expert.email = request.POST.get('email')
        if request.POST.get('password'):
            expert.password = request.POST.get('password')
        expert.domain = request.POST.get('domain')
        expert.save()
        messages.success(request, 'Expert updated successfully')
        return redirect('admin_list_experts')

    return render(request, 'admin_panel/edit_expert.html', {'expert': expert})

@role_required('admin')
def admin_delete_expert(request, expert_id):
    try:
        expert = DomainExpert.objects.get(id=expert_id)
        expert.delete()
        messages.success(request, 'Expert deleted successfully')
    except DomainExpert.DoesNotExist:
        messages.error(request, 'Expert not found.')
    return redirect('admin_list_experts')

# --- SYSTEM CONFIGURATION ---
@role_required('admin')
def admin_ai_settings(request):
    from .models import AIConfiguration
    config, created = AIConfiguration.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        api_key = request.POST.get('api_key')
        model_name = request.POST.get('model_name')
        
        config.api_key = api_key if api_key else ""
        if model_name:
            config.model_name = model_name
        config.save()
        messages.success(request, 'AI Configuration updated successfully.')
        return redirect('admin_ai_settings')
        
    # We shouldn't send the full API key back to the template for security reasons unless needed,
    # but the admin might want to see if it's set. We send a masked version.
    masked_key = ""
    if config.api_key and len(config.api_key) > 8:
        masked_key = config.api_key[:4] + "*" * (len(config.api_key) - 8) + config.api_key[-4:]
    elif config.api_key:
        masked_key = "****"
        
    return render(request, 'admin_panel/ai_settings.html', {
        'config': config,
        'masked_key': masked_key
    })

# --- APTITUDE GENERATION MOVED TO DOMAIN EXPERT ---
