from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Uses Django's built-in login()
            return redirect('dashboard')  # Ensure 'dashboard' URL name exists
        else:
            messages.error(request, 'Invalid credentials!')
    
    return render(request, 'login/login.html')

@login_required  # Ensures only logged-in users can access
def dashboard_view(request):
    return render(request, 'login/dashboard.html', {'active_tab': 'dashboard'})
@login_required
def devices_view(request):
    return render(request, 'login/devices.html', {'active_tab': 'devices'})

@login_required
def alerts_view(request):
    return render(request, 'login/alerts.html', {'active_tab': 'alerts'})