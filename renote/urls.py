"""
URL configuration for renote project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.register import views as register_views
from apps.home import views as home_views

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

    # SEO & Search Engine Crawlers
    path('robots.txt', home_views.robots_txt_view, name='robots_txt'),
    path('sitemap.xml', home_views.sitemap_xml_view, name='sitemap_xml'),

    # Dedicated error preview routes (convenient in development)
    path('404/', home_views.custom_404_view, name='preview_404'),
    path('500/', home_views.custom_500_view, name='preview_500'),
    path('403/', home_views.custom_403_view, name='preview_403'),
    path('400/', home_views.custom_400_view, name='preview_400'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Production error handlers (activated when DEBUG = False)
handler404 = 'apps.home.views.custom_404_view'
handler500 = 'apps.home.views.custom_500_view'
handler403 = 'apps.home.views.custom_403_view'
handler400 = 'apps.home.views.custom_400_view'
