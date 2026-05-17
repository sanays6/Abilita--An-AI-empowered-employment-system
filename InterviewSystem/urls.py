from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Home Page
    path('', views.home, name='home'),
    
    # Built-in django admin just in case
    path('django-admin/', admin.site.urls),
    
    # Custom apps
    path('users/', include('users.urls')),
    path('expert/', include('domain_expert.urls')),
    path('admin/', include('admin_panel.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
