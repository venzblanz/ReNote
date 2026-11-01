"""
URL configuration for renote project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.register import views as register_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.home.urls')),
    path('login/', include('apps.login.urls')),
    path('register/', include('apps.register.urls')),
    path('terms/', register_views.terms_view, name='terms'),
    path('privacy/', register_views.privacy_view, name='privacy'),
    path('profile/', include('apps.user_profile.urls')),
    path('settings/', include('apps.user_settings.urls')),
    path('library/', include('apps.library.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
