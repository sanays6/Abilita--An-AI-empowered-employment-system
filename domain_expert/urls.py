from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.expert_login, name='expert_login'),
    path('logout/', views.expert_logout, name='expert_logout'),
    path('dashboard/', views.expert_dashboard, name='expert_dashboard'),
    path('performance/<int:result_id>/', views.expert_view_performance, name='expert_view_performance'),
    path('question/delete/<int:q_id>/', views.delete_question, name='delete_question'),
    path('question/edit/<int:q_id>/', views.edit_question, name='edit_question'),
    
    path('aptitude/generate/', views.expert_generate_aptitude, name='expert_generate_aptitude'),
    path('aptitude/list/', views.expert_list_aptitude, name='expert_list_aptitude'),
    path('aptitude/delete/<int:q_id>/', views.expert_delete_aptitude, name='expert_delete_aptitude'),
    path('aptitude/edit/<int:q_id>/', views.expert_edit_aptitude, name='expert_edit_aptitude'),
    path('aptitude/bulk_delete/', views.expert_bulk_delete_aptitude, name='expert_bulk_delete_aptitude'),
]
