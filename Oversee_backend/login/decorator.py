from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.contrib import messages
import logging
from login.models import UserRole

logger = logging.getLogger(__name__)

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                # Get user role
                user_role_obj = UserRole.objects.get(user=request.user)
                user_role = user_role_obj.role
                
                if user_role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    logger.warning(f"Access denied for user {request.user.username} with role {user_role}")
                    # Return 403 page instead of redirecting
                    return render(request, 'login/errors/403.html', status=403)
            except UserRole.DoesNotExist:
                logger.error(f"Role not found for user {request.user.username}")
                return render(request, 'login/errors/403.html', status=403)
            except Exception as e:
                logger.error(f"Role check failed for user {request.user.username}: {str(e)}")
                return render(request, 'login/errors/403.html', status=403)
        return wrapper
    return decorator