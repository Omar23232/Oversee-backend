from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from login.models import DeviceMemory,ExecutedCommand, InterfaceStatus
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import logging
from login.services.network_client import fetch_and_store_memory_stats
from django.conf import settings
from .models import DeviceCPU, DeviceInfo, NetworkAlert, NetworkThreshold
from login.services.cpu_client import fetch_and_store_cpu_stats
from login.services.execute_command import CiscoCommandExecutor
from login.services.interface_client import InterfaceMonitor
import json
from django.shortcuts import render, redirect, get_object_or_404  

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

@login_required
def dashboard_view(request):
    # Get only the most recent record
    latest_stat = DeviceMemory.objects.order_by('-timestamp').first()
    
    if latest_stat:
        used_percentage = (latest_stat.used_memory / latest_stat.total_memory) * 100
        used_percentage = round(used_percentage, 2)
    else:
        latest_stat = None
        used_percentage = 0
    
    context = {
        'active_tab': 'dashboard',
        'current_memory': latest_stat,
        'used_percentage': used_percentage,
    }
    return render(request, 'login/dashboard.html', context)

@login_required
def devices_view(request):
    return render(request, 'login/devices.html', {'active_tab': 'devices'})

@login_required
def alerts_view(request):
    return render(request, 'login/alerts.html', {'active_tab': 'alerts'})


 # API endpoint to fetch memory statistics
 
@login_required
def memory_stats_api(request):
    try:
        latest_stat = DeviceMemory.objects.order_by('-timestamp').first()
        
        if not latest_stat or (timezone.now() - latest_stat.timestamp).total_seconds() > 2:
            fetch_and_store_memory_stats()
            latest_stat = DeviceMemory.objects.order_by('-timestamp').first()
        
        if latest_stat:
            used_percentage = (latest_stat.used_memory / latest_stat.total_memory) * 100
            
            # Check memory thresholds
            thresholds = NetworkThreshold.objects.filter(metric='memory')
            for threshold in thresholds:
                if used_percentage >= threshold.threshold_value:
                    NetworkAlert.objects.create(
                        device_ip=latest_stat.device_ip,
                        metric_name='Memory Usage',
                        metric_value=used_percentage,
                        threshold_value=threshold.threshold_value,
                        severity=threshold.severity
                    )
            
            data = {
                'used_percentage': round(used_percentage, 2),
                'total': latest_stat.total_memory,
                'used': latest_stat.used_memory,
                'timestamp': latest_stat.timestamp.strftime("%H:%M:%S"),
                'status': 'success'
            }
        else:
            data = {
                'status': 'error',
                'message': 'No data available'
            }
            
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
        
        
# api endpoint to fetch CPU statistics

@login_required
def cpu_stats_api(request):
    try:
        latest_stat = DeviceCPU.objects.order_by('-timestamp').first()
        
        if not latest_stat or (timezone.now() - latest_stat.timestamp).total_seconds() > 2:
            fetch_and_store_cpu_stats()
            latest_stat = DeviceCPU.objects.order_by('-timestamp').first()
        
        if latest_stat:
            # Check CPU thresholds
            cpu_metrics = {
                'cpu_5s': latest_stat.five_seconds,
                'cpu_1m': latest_stat.one_minute,
                'cpu_5m': latest_stat.five_minutes
            }
            
            for metric_name, value in cpu_metrics.items():
                thresholds = NetworkThreshold.objects.filter(metric=metric_name)
                for threshold in thresholds:
                    if value >= threshold.threshold_value:
                        NetworkAlert.objects.create(
                            device_ip=latest_stat.device_ip,
                            metric_name=f"CPU Usage ({metric_name})",
                            metric_value=value,
                            threshold_value=threshold.threshold_value,
                            severity=threshold.severity
                        )
            
            data = {
                'five_seconds': latest_stat.five_seconds,
                'one_minute': latest_stat.one_minute,
                'five_minutes': latest_stat.five_minutes,
                'timestamp': latest_stat.timestamp.strftime("%H:%M:%S"),
                'status': 'success'
            }
        else:
            data = {
                'status': 'error',
                'message': 'No data available'
            }
            
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
    
@login_required
def uptime_api(request):
    executor = CiscoCommandExecutor()
    result = executor.execute("show version | include uptime")  # Fixed command
    
    return JsonResponse({
        'status': result['status'],
        'output': result.get('output', ''),
        'timestamp': timezone.now().strftime("%H:%M:%S")
    })


# Api endpoint to get interface status of the device
@login_required
def interface_api(request):
    monitor = InterfaceMonitor()
    result = monitor.fetch_interfaces()
    
    if result['status'] == 'success':
        # Get latest status for all interfaces
        interfaces = InterfaceStatus.objects.filter(
            device_ip="192.168.47.131"
        ).distinct('name').order_by('name', '-timestamp')
        
        return JsonResponse({
            'status': 'success',
            'interfaces': [
                {
                    'name': i.name,
                    'status': i.oper_status,
                    'last_change': i.last_change,
                    'mac': i.mac_address
                } for i in interfaces
            ]
        })
    return JsonResponse(result, status=500)

@login_required
def interfaces_view(request):
    interfaces = InterfaceStatus.objects.filter(device_ip="192.168.47.131").order_by('name', '-timestamp')
    return render(request, 'login/interfaces.html', {
        'active_tab': 'devices',
    })
    
    
    
    
@login_required
def devices_view(request):
    devices = DeviceInfo.objects.all()
    return render(request, 'login/devices.html', {
        'active_tab': 'devices',
        'devices': devices
    })

@login_required
def add_device_auto(request):
    # Placeholder for automatic device addition
    return redirect('devices')

@login_required
def add_device_manual(request):
    if request.method == 'POST':
        device = DeviceInfo.objects.create(
            hostname=request.POST['hostname'],
            uptime="New Device",
            system_description=request.POST['system_description'],
            location=request.POST['location'],
            status=request.POST['status'],
            device_ip=request.POST['device_ip']
        )
        return redirect('devices')
    return render(request, 'login/partials/add-device-manual.html', {'active_tab': 'devices'})



# API endpoint to fetch network alerts
@login_required
def alerts_api(request):
    alerts = NetworkAlert.objects.all().order_by('-created_at')
    data = [{
        'id': alert.id,
        'metric_name': alert.metric_name,
        'metric_value': alert.metric_value,
        'threshold_value': alert.threshold_value,
        'severity': alert.severity,
        'device_ip': alert.device_ip,
        'created_at': alert.created_at.isoformat(),
        'is_acknowledged': alert.is_acknowledged
    } for alert in alerts]
    return JsonResponse({'status': 'success', 'alerts': data})



# API endpoint to manage network thresholds
@login_required
def thresholds_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        threshold = NetworkThreshold.objects.create(
            metric=data['metric'],
            threshold_value=data['threshold_value'],
            severity=data['severity']
        )
        return JsonResponse({'status': 'success', 'id': threshold.id})
    
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            threshold_id = data.get('id')
            threshold = NetworkThreshold.objects.get(id=threshold_id)
            threshold.delete()
            return JsonResponse({'status': 'success'})
        except NetworkThreshold.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Threshold not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    # GET method
    thresholds = NetworkThreshold.objects.all()
    data = [{
        'id': t.id,
        'metric': t.metric,
        'threshold_value': t.threshold_value,
        'severity': t.severity
    } for t in thresholds]
    return JsonResponse({'status': 'success', 'thresholds': data})

# API endpoint to render the thresholds page
@login_required
def thresholds_view(request):
    return render(request, 'login/partials/thresholds.html')


# view for device command execution
@login_required
def device_command_view(request, device_id):
    device = get_object_or_404(DeviceInfo, id=device_id)
    return render(request, 'login/partials/device_command.html', {
        'device': device,
        'active_tab': 'devices'
    })

# API endpoint to execute commands on the device
@login_required
def execute_command_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        command = data.get('command')
        
        executor = CiscoCommandExecutor()
        result = executor.execute(command)
        
        return JsonResponse(result)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})