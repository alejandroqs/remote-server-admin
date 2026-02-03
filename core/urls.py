"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include

# Custom error handlers for better UX
handler404 = 'monitor.views.custom_page_not_found'
handler500 = 'monitor.views.custom_server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Built-in auth urls (login, logout, password reset)
    path('accounts/', include('django.contrib.auth.urls')),
    # API endpoints
    path('api/', include('monitor.urls')),
    # Internationalization
    path('i18n/', include('django.conf.urls.i18n')),
    # Main application routes
    path('', include('monitor.urls')),
]