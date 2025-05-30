from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import memory_stats_api, cpu_stats_api , uptime_api, interface_api
from .views import interfaces_view

urlpatterns = [
    path('',views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('devices/', views.devices_view, name='devices'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('memory-stats/', views.memory_stats_api, name='memory-stats'),
    path('cpu-stats/', views.cpu_stats_api, name='cpu-stats'),
    path('uptime-api/', views.uptime_api, name='uptime-api'),
    path('interface-api/', views.interface_api, name='interface-api'),
    path('interfaces/', views.interfaces_view, name='interfaces')
    
    ]