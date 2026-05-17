from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Users
    path('users/', views.admin_list_users, name='admin_list_users'),
    path('users/<int:user_id>/', views.admin_view_user, name='admin_view_user'),
    
    # Domain Experts
    path('experts/', views.admin_list_experts, name='admin_list_experts'),
    path('experts/add/', views.admin_add_expert, name='admin_add_expert'),
    path('experts/delete/<int:expert_id>/', views.admin_delete_expert, name='admin_delete_expert'),
     path('experts/edit/<int:expert_id>/', views.admin_edit_expert, name='admin_edit_expert'),
    path('ai-settings/', views.admin_ai_settings, name='admin_ai_settings'),
]   

