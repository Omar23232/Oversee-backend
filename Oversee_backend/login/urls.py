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
    path('settings/', views.settings_view, name='settings'),
    path('explore/', views.explore_view, name='explore'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('memory-stats/', views.memory_stats_api, name='memory-stats'),
    path('cpu-stats/', views.cpu_stats_api, name='cpu-stats'),
    path('uptime-api/', views.uptime_api, name='uptime-api'),
    path('interface-api/', views.interface_api, name='interface-api'),
    path('interfaces/', views.interfaces_view, name='interfaces'),
    path('add-device-auto/', views.add_device_auto, name='add_device_auto'),
    path('add-device-manual/', views.add_device_manual, name='add_device_manual'),
    path('alerts-api/', views.alerts_api, name='alerts_api'),
    path('thresholds/', views.thresholds_view, name='thresholds'),
    path('thresholds-api/', views.thresholds_api, name='thresholds_api'),
    path('device/<int:device_id>/command/', views.device_command_view, name='device_command'),
    path('execute-command/', views.execute_command_view, name='execute_command'),
    path('logs/', views.login_logs_view, name='login_logs'),
    path('command-details/<int:command_id>/', views.command_details, name='command_details'),
    path('devices/<int:device_id>/details/', views.device_details_view, name='device_details'),
    path('acknowledge-alert/<int:alert_id>/', views.acknowledge_alert, name='acknowledge_alert'),
    
    path('api/update-profile/', views.update_profile_api, name='update_profile_api'),
    path('api/change-password/', views.change_password_api, name='change_password_api'),
    path('api/thresholds/', views.thresholds_api, name='thresholds_api'),
    path('api/users/', views.users_api, name='users_api'),    path('api/user-preferences/', views.user_preferences_api, name='user_preferences_api'),

    path('ddos-alerts/', views.ddos_alerts_view, name='ddos_alerts'),
    path('ddos-model/', views.ddos_model_api, name='ddos_model_api'),
    ]