from django.shortcuts import redirect
from functools import wraps

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.session.get('role') != role:
                if role == 'admin':
                    return redirect('admin_login')
                elif role == 'expert':
                    return redirect('expert_login')
                else:
                    return redirect('user_login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
