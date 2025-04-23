from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('',views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('devices/', views.devices_view, name='devices'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    ]