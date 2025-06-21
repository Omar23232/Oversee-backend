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
from .models import DeviceCPU, DeviceInfo, NetworkAlert, NetworkThreshold, DDoSAlert
from login.services.cpu_client import fetch_and_store_cpu_stats
from login.services.execute_command import CiscoCommandExecutor
from login.services.switch_command_executer import switch_command_executor
from login.services.interface_client import InterfaceMonitor
import json
from django.shortcuts import render, redirect, get_object_or_404
from login.models import LoginAttempt, UserRole
from django.core.paginator import Paginator
from .decorator import role_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from .services.ddos_detection_service import DDoSDetectionService
import datetime

# view for the login page

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Get client info
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user) # uses django's built-in login function
            
            # Log successful login attempt
            LoginAttempt.objects.create(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            
            return redirect('dashboard')
        else:
            # Log failed login attempt
            LoginAttempt.objects.create(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False
            )
            
            messages.error(request, 'Invalid credentials!')
    
    return render(request, 'login/login.html')

@login_required
def explore_view(request):
    """
    View for the explore/about page that explains what the OverSee application does
    """
    return render(request, 'login/explore.html', {'active_tab': 'explore'})

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
    
    device = DeviceInfo.objects.filter(device_type='router', hostname='Main Router').first()
    if device:
        device_ip = device.device_ip
    else:
        return JsonResponse({'status': 'error', 'message': 'Device not found'}, status=404)
    try:
        latest_stat = DeviceMemory.objects.order_by('-timestamp').first()
        
        if not latest_stat or (timezone.now() - latest_stat.timestamp).total_seconds() > 2:
            fetch_and_store_memory_stats(device_ip=device_ip)
            latest_stat = DeviceMemory.objects.order_by('-timestamp').first()
        
        if latest_stat:
            used_percentage = (latest_stat.used_memory / latest_stat.total_memory) * 100
            
            # Check memory thresholds
            thresholds = NetworkThreshold.objects.filter(metric='memory')
            for threshold in thresholds:
                if used_percentage >= threshold.threshold_value:
                    # Check if an unacknowledged alert already exists for this metric and severity
                    existing_alert = NetworkAlert.objects.filter(
                        device_ip=latest_stat.device_ip,
                        metric_name='Memory Usage',
                        severity=threshold.severity,
                        is_acknowledged=False
                    ).first()
                    
                    if not existing_alert:
                        # Create new alert only if no unacknowledged alert exists
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
    
    device = DeviceInfo.objects.filter(device_type='router', hostname='Main Router').first()
    if device:
        device_ip = device.device_ip
    else:
        return JsonResponse({'status': 'error', 'message': 'Device not found'}, status=404)
    
    try:
        latest_stat = DeviceCPU.objects.order_by('-timestamp').first()
        
        if not latest_stat or (timezone.now() - latest_stat.timestamp).total_seconds() > 2:
            fetch_and_store_cpu_stats(device_ip=device_ip)
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
                        # Check if an unacknowledged alert already exists for this metric and severity
                        existing_alert = NetworkAlert.objects.filter(
                            device_ip=latest_stat.device_ip,
                            metric_name=f"CPU Usage ({metric_name})",
                            severity=threshold.severity,
                            is_acknowledged=False
                        ).first()
                        
                        if not existing_alert:
                            # Create new alert only if no unacknowledged alert exists
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
    # Fetch the device IP from the DeviceInfo model
    device = DeviceInfo.objects.filter(device_type='router', hostname='Main Router').first()
    if device :
        device_ip = device.device_ip
    else:
        return JsonResponse({'status': 'error', 'message': 'Device not found'}, status=404)
    
    # Use the correct command to fetch uptime
    executor = CiscoCommandExecutor(device_ip=device_ip)
    result = executor.execute(cli_command="show version | include uptime")  # Fixed command
    
    return JsonResponse({
        'status': result['status'],
        'output': result.get('output', ''),
        'timestamp': timezone.now().strftime("%H:%M:%S")
    })


# Api endpoint to get interface status of the device
@login_required
def interface_api(request):
    
    device = DeviceInfo.objects.filter(device_type='router', hostname='Main Router').first()
    if device :
        device_ip = device.device_ip
    else:
        return JsonResponse({'status': 'error', 'message': 'Device not found'}, status=404)
    
    monitor = InterfaceMonitor(device_ip=device_ip)
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
                    'mac': i.mac_address,
                    # Add bandwidth metrics
                    'in_bandwidth': round(i.in_bandwidth, 2),
                    'out_bandwidth': round(i.out_bandwidth, 2),
                    # Add error metrics
                    'error_rate': round(i.error_rate, 3),
                    'packet_loss': round(i.packet_loss, 3),
                    'in_errors': i.in_errors,
                    'out_errors': i.out_errors,
                    'in_discards': i.in_discards,
                    'out_discards': i.out_discards
                } for i in interfaces
            ]
        })
    return JsonResponse(result, status=500)

@login_required
def interfaces_view(request):
    interfaces = InterfaceStatus.objects.filter(device_ip="192.168.47.131").order_by('name', '-timestamp')
    return render(request, 'login/interfaces.html', {
        'active_tab': 'dashboard',
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
    # Get the 'show_acknowledged' parameter from the request
    show_acknowledged = request.GET.get('show_acknowledged', 'false').lower() == 'true'
    
    # Filter alerts based on acknowledgment status
    if not show_acknowledged:
        alerts_queryset = NetworkAlert.objects.filter(is_acknowledged=False).order_by('-created_at')
    else:
        alerts_queryset = NetworkAlert.objects.all().order_by('-created_at')
    
    data = [{
        'id': alert.id,
        'metric_name': alert.metric_name,
        'metric_value': alert.metric_value,
        'threshold_value': alert.threshold_value,
        'severity': alert.severity,
        'device_ip': alert.device_ip,
        'created_at': alert.created_at.isoformat(),
        'is_acknowledged': alert.is_acknowledged
    } for alert in alerts_queryset]
    
    return JsonResponse({'status': 'success', 'alerts': data})



# API endpoint to manage network thresholds
@login_required
def thresholds_api(request):
    """API endpoint for managing network thresholds"""
    if request.method == 'GET':
        # Get all thresholds
        thresholds = NetworkThreshold.objects.all()
        return JsonResponse({
            'status': 'success',
            'thresholds': [
                {
                    'id': t.id,
                    'metric': t.metric,
                    'metric_display': t.get_metric_display(),
                    'threshold_value': t.threshold_value,
                    'severity': t.severity,
                    'severity_display': t.get_severity_display(),
                    'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S')
                } for t in thresholds
            ]
        })
    
    elif request.method == 'POST':
        # Create a new threshold
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['metric', 'threshold_value', 'severity']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'status': 'error', 'message': f'Missing required field: {field}'}, status=400)
            
            # Create new threshold
            threshold = NetworkThreshold.objects.create(
                metric=data['metric'],
                threshold_value=data['threshold_value'],
                severity=data['severity']
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Threshold created successfully',
                'threshold': {
                    'id': threshold.id,
                    'metric': threshold.metric,
                    'metric_display': threshold.get_metric_display(),
                    'threshold_value': threshold.threshold_value,
                    'severity': threshold.severity,
                    'severity_display': threshold.get_severity_display(),
                    'created_at': threshold.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    elif request.method == 'PUT':
        # Update existing threshold
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'id' not in data:
                return JsonResponse({'status': 'error', 'message': 'Missing threshold ID'}, status=400)
            
            # Get threshold
            try:
                threshold = NetworkThreshold.objects.get(id=data['id'])
            except NetworkThreshold.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Threshold not found'}, status=404)
            
            # Update fields
            if 'metric' in data:
                threshold.metric = data['metric']
            if 'threshold_value' in data:
                threshold.threshold_value = data['threshold_value']
            if 'severity' in data:
                threshold.severity = data['severity']
            
            threshold.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Threshold updated successfully',
                'threshold': {
                    'id': threshold.id,
                    'metric': threshold.metric,
                    'metric_display': threshold.get_metric_display(),
                    'threshold_value': threshold.threshold_value,
                    'severity': threshold.severity,
                    'severity_display': threshold.get_severity_display(),
                    'created_at': threshold.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    elif request.method == 'DELETE':
        # Delete threshold
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'id' not in data:
                return JsonResponse({'status': 'error', 'message': 'Missing threshold ID'}, status=400)
            
            # Get threshold
            try:
                threshold = NetworkThreshold.objects.get(id=data['id'])
            except NetworkThreshold.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Threshold not found'}, status=404)
            
            # Delete threshold
            threshold.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Threshold deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
        
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
        device_ip = data.get('device_ip')
        
        if not device_ip :
            return JsonResponse({'status': 'error', 'message': 'Device IP is required'})
        
        device = DeviceInfo.objects.filter(device_ip=device_ip).first()
        device_type = device.device_type if device else None
        
        if device_type == 'router':
            executor = CiscoCommandExecutor(device_ip=device_ip)
            result = executor.execute(command, user=request.user)  # Pass user to executor
        elif device_type == 'switch':
            executor = switch_command_executor(device_ip=device_ip)
            result = executor.execute(cli_command=command, user=request.user)  # Pass user to executor
        else:
            return JsonResponse({'status': 'error', 'message': 'Unsupported device type'})
        return JsonResponse(result)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# View for device details page
@login_required
def device_details_view(request, device_id):
    device = get_object_or_404(DeviceInfo, id=device_id)
    
    if device.device_type =='router':
        fetch_and_store_memory_stats(device_ip=device.device_ip)
        fetch_and_store_cpu_stats(device_ip=device.device_ip)
    elif device.device_type == 'switch':
        switch_monitor = switch_command_executor(device_ip=device.device_ip)
        switch_monitor.get_memory_stats()
        switch_monitor.get_cpu_stats()
        switch_monitor.get_interface_stats()
    # Get latest metrics for this specific device
    memory_stats = DeviceMemory.objects.filter(device_ip=device.device_ip).order_by('-timestamp').first()
    cpu_stats = DeviceCPU.objects.filter(device_ip=device.device_ip).order_by('-timestamp').first()
    
    # Calculate memory percentage if available
    memory_percentage = 0
    if memory_stats:
        memory_percentage = round((memory_stats.used_memory / memory_stats.total_memory) * 100, 2)
    
    # Get interfaces for this device
    try:
        interfaces = InterfaceStatus.objects.filter(
            device_ip=device.device_ip
        ).distinct('name').order_by('name', '-timestamp')
    except:
        # Handle case where distinct on field is not supported
        interfaces = []
        interface_names = set()
        for interface in InterfaceStatus.objects.filter(
            device_ip=device.device_ip
        ).order_by('name', '-timestamp'):
            if interface.name not in interface_names:
                interface_names.add(interface.name)
                interfaces.append(interface)
    
    # Get recent alerts for this device
    alerts = NetworkAlert.objects.filter(
        device_ip=device.device_ip
    ).order_by('-created_at')[:5]
    
    return render(request, 'login/partials/device_details.html', {
        'device': device,
        'memory_stats': memory_stats,
        'memory_percentage': memory_percentage,
        'cpu_stats': cpu_stats,
        'interfaces': interfaces,
        'alerts': alerts,
        'active_tab': 'devices'
    })
      
# view for login logs for admin users

@login_required
@role_required(['admin'])
def login_logs_view(request):
    # Get the selected log type from query params, default to login logs
    log_type = request.GET.get('log_type', 'login')
    
    if log_type == 'commands':
        # Get command logs
        logs = ExecutedCommand.objects.all().filter(user__isnull=False).order_by('-timestamp')
        paginator = Paginator(logs, 10)
        page = request.GET.get('page')
        commands = paginator.get_page(page)
        
        context = {
            'active_tab': 'logs',
            'log_type': 'commands',
            'commands': commands
        }
    else:
        # Get login logs (default)
        login_attempts = LoginAttempt.objects.all()
        paginator = Paginator(login_attempts, 10)
        page = request.GET.get('page')
        attempts = paginator.get_page(page)
        
        context = {
            'active_tab': 'logs',
            'log_type': 'login',
            'attempts': attempts
        }
        
    return render(request, 'login/logs.html', context)

# API endpoint to fetch command details from the logs page 
@login_required
def command_details(request, command_id):
    try:
        command = ExecutedCommand.objects.get(id=command_id)
        return JsonResponse({
            'status': 'success',
            'command': command.command,
            'output': command.output,
            'user': command.user.username if command.user else None,
            'device_ip': command.device_ip,
            'timestamp': command.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    except ExecutedCommand.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Command not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
        


# 403 Forbidden view handler

def custom_403(request, exception=None):
    """
    Custom 403 Forbidden view
    """
    return render(request, 'login/403.html', status=403)


# view to acknowledge an alert
@login_required
def acknowledge_alert(request, alert_id):
    try:
        alert = NetworkAlert.objects.get(id=alert_id)
        alert.is_acknowledged = True
        alert.save()
        return JsonResponse({'status': 'success'})
    except NetworkAlert.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Alert not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def settings_view(request):
    # Get current user
    user = request.user
    
    # Try to get user role
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        user_role = None
    
    # Get all thresholds for network alerts
    thresholds = NetworkThreshold.objects.all()
    
    # Get all users for admin panel
    users = []
    if user_role and user_role.role == 'admin':
        users_data = User.objects.all().select_related('userrole')
        for u in users_data:
            try:
                role = u.userrole.role
            except UserRole.DoesNotExist:
                role = "user"
                
            users.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'role': role,
                'last_login': u.last_login
            })
    
    context = {
        'active_tab': 'settings',
        'user': user,
        'user_role': user_role,
        'thresholds': thresholds,
        'users': users,
        'now': timezone.now()  # Add current time for cache busting
    }
    
    return render(request, 'login/settings.html', context)

@login_required
@csrf_exempt
def update_profile_api(request):
    """API endpoint for updating user profile information"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Update user information
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Profile updated successfully',
            'user': {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@csrf_exempt
def change_password_api(request):
    """API endpoint for changing user password"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Verify current password
        if not user.check_password(current_password):
            return JsonResponse({'status': 'error', 'message': 'Current password is incorrect'}, status=400)
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Update session to prevent logout
        update_session_auth_hash(request, user)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Password changed successfully'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@role_required('admin')
@csrf_exempt
def users_api(request):
    """API endpoint for managing users (admin only)"""
    if request.method == 'GET':
        # Get all users
        users_data = User.objects.all().select_related('userrole')
        users = []
        
        for u in users_data:
            try:
                role = u.userrole.role
            except UserRole.DoesNotExist:
                role = "user"
                
            users.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'role': role,
                'last_login': u.last_login.strftime('%Y-%m-%d %H:%M:%S') if u.last_login else None
            })
        
        return JsonResponse({
            'status': 'success',
            'users': users
        })
    
    elif request.method == 'POST':
        # Create a new user
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['username', 'email', 'password', 'role']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'status': 'error', 'message': f'Missing required field: {field}'}, status=400)
            
            # Check if username already exists
            if User.objects.filter(username=data['username']).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already exists'}, status=400)
            
            # Create new user
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )
            
            # Create user role
            UserRole.objects.create(
                user=user,
                role=data['role']
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'User created successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': data['role']
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    elif request.method == 'PUT':
        # Update existing user
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'id' not in data:
                return JsonResponse({'status': 'error', 'message': 'Missing user ID'}, status=400)
            
            # Get user
            try:
                user = User.objects.get(id=data['id'])
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
            
            # Update fields
            if 'email' in data:
                user.email = data['email']
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'password' in data:
                user.set_password(data['password'])
            
            user.save()
            
            # Update role if provided
            if 'role' in data:
                try:
                    user_role = UserRole.objects.get(user=user)
                    user_role.role = data['role']
                    user_role.save()
                except UserRole.DoesNotExist:
                    UserRole.objects.create(
                        user=user,
                        role=data['role']
                    )
            
            return JsonResponse({
                'status': 'success',
                'message': 'User updated successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': UserRole.objects.get(user=user).role if hasattr(user, 'userrole') else 'user'
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    elif request.method == 'DELETE':
        # Delete user
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'id' not in data:
                return JsonResponse({'status': 'error', 'message': 'Missing user ID'}, status=400)
            
            # Get user
            try:
                user = User.objects.get(id=data['id'])
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
            
            # Check if trying to delete self
            if user.id == request.user.id:
                return JsonResponse({'status': 'error', 'message': 'Cannot delete your own account'}, status=400)
            
            # Delete user
            user.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'User deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@login_required
@csrf_exempt
def user_preferences_api(request):
    """API endpoint for managing user preferences"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        # In a real application, you would store these in a UserPreferences model
        # For now, we'll just return success to simulate storage
        preference_type = data.get('type', '')
        
        if preference_type == 'notification':
            # Handle notification preferences
            browser_notifications = data.get('browser_notifications', True)
            email_notifications = data.get('email_notifications', True)
            notification_frequency = data.get('notification_frequency', 'immediately')
            
            # In a real application, save these preferences to a database
            
            return JsonResponse({
                'status': 'success',
                'message': 'Notification preferences saved successfully',
                'preferences': {
                    'browser_notifications': browser_notifications,
                    'email_notifications': email_notifications,
                    'notification_frequency': notification_frequency
                }
            })
            
        elif preference_type == 'appearance':
            # Handle appearance preferences
            theme = data.get('theme', 'light')
            dashboard_refresh = data.get('dashboard_refresh', 30)
            
            # In a real application, save these preferences to a database
            
            return JsonResponse({
                'status': 'success',
                'message': 'Appearance preferences saved successfully',
                'preferences': {
                    'theme': theme,
                    'dashboard_refresh': dashboard_refresh
                }
            })
            
        elif preference_type == 'system':
            # Handle system settings (admin only)
            # Check if user is admin
            try:
                user_role = UserRole.objects.get(user=user)
                if user_role.role != 'admin':
                    return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
            except UserRole.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
            
            backup_frequency = data.get('backup_frequency', 'weekly')
            log_retention = data.get('log_retention', 90)
            
            # In a real application, save these preferences to a database
            
            return JsonResponse({
                'status': 'success',
                'message': 'System settings saved successfully',
                'preferences': {
                    'backup_frequency': backup_frequency,
                    'log_retention': log_retention
                }
            })
            
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid preference type'}, status=400)
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def ddos_model_api(request):
   
    # Create an instance of the DDoS detection service
    ddos_service = DDoSDetectionService()
    
    # Get the  response
    response_data = ddos_service.check_for_attacks()
    
    # Return the result directly as JSON
    return JsonResponse(response_data)

# DDoS Alerts view
@login_required
def ddos_alerts_view(request):
    # Create an instance of the DDoS detection service
    ddos_service = DDoSDetectionService()
    
    # Get recent alerts (last 24 hours)
    recent_alerts = DDoSAlert.objects.filter(
        detection_time__gte=timezone.now() - datetime.timedelta(hours=24)
    ).order_by('-detection_time')[:10]
    
    # Format alert data for the template
    alert_data = []
    now = timezone.now()
    
    for alert in recent_alerts:
        # Calculate duration
        if alert.duration:
            duration_str = str(alert.duration).split('.')[0]  # Remove microseconds

        else:
            duration = now - alert.detection_time
            duration_str = str(duration).split('.')[0]
            
        alert_data.append({
            'id': alert.id,
            'attack_type': dict(DDoSAlert.ATTACK_TYPE_CHOICES).get(alert.attack_type, alert.attack_type),
            'source_ip': alert.source_ip,
            'target_ip': alert.target_ip,
            'target_service': getattr(alert, 'target_service', 'Unknown'),
            'severity': alert.severity,
            'status': alert.status,
            'detection_time': alert.detection_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': duration_str,
            'ai_confidence': round(alert.ai_confidence * 100, 2),  # Convert to percentage
            'blocked': alert.blocked
        })
    
    # Get statistics
    stats = {
        'total_attacks_today': DDoSAlert.objects.filter(
            detection_time__gte=now.replace(hour=0, minute=0, second=0)
        ).count(),
        'active_attacks': DDoSAlert.objects.filter(status='active').count(),
        'mitigated_attacks': DDoSAlert.objects.filter(status='mitigated').count(),
        'resolved_attacks': DDoSAlert.objects.filter(status='resolved').count(),
        'protection_status': 'Active'  # This could be dynamic in a real app
    }
    
    # Check if we have any sample data from the AI model
    try:
        model_response = ddos_service.check_for_attacks()
        model_data = {
            'status': model_response.get('status', 'Unknown'),
            'source_ip': model_response.get('source_ip', 'Unknown'),
            'result': model_response.get('result', 'Unknown')
        }
    except:
        model_data = {
            'status': 'error',
            'source_ip': 'Unknown',
            'result': 'Unknown'
        }
    
    return render(request, 'login/ddos_alerts.html', {
        'active_tab': 'ddos_alerts',
        'alerts': alert_data,
        'stats': stats,
        'model_data': model_data
    })

