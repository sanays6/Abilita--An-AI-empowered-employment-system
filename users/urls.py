from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('signup/', views.user_signup, name='user_signup'),
    path('logout/', views.user_logout, name='user_logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    
    
    # Test Flows
    path('analyse-cv/', views.analyse_cv, name='analyse_cv'),
    path('history/', views.user_history, name='user_history'),
    path('aptitude/', views.start_aptitude, name='start_aptitude'),
    path('interview/', views.start_interview, name='start_interview'),
    path('interview/submit/', views.submit_interview_answer, name='submit_interview_answer'),
    path('interview/finish/', views.finish_interview, name='finish_interview'),
    path('result/<int:result_id>/', views.user_result, name='user_result'),
]
