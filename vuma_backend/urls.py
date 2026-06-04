from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    # Admin CRUD APIs
    path('api/users/', include('users.admin_urls')),
    # In vuma_backend/urls.py
    path('api/projects/', include('projects.urls')),
    path('api/events/', include('events.admin_urls')),
    # In vuma_backend/urls.py
    path('api/partners/', include('partners.urls')),
    path('api/volunteers/', include('volunteers.admin_urls')),
    # In vuma_backend/urls.py
    path('api/news/', include('news.urls')),
    path('api/programs/', include('programs.urls')),
    path('', include('leadership.urls')),
    path('api/', include('contacts.urls')),
    path('api/',include('donate.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)