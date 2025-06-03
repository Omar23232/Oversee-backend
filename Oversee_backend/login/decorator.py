from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
import logging
from login.models import UserRole

logger = logging.getLogger(__name__)

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                print(f"Checking role for user: {request.user.username}")  # Debugging line
                # Try to get the role directly from the database as fallback
                try:
                    user_role = request.user.userrole.role
                except:
                    # Manual lookup if the relationship isn't working
                    user_role_obj = UserRole.objects.filter(user_id=request.user.id).first()
                    if not user_role_obj:
                        raise Exception("No role found for user")
                    user_role = user_role_obj.role
                
                print(f"User {request.user.username} role: {user_role}")  # Debugging line
                logger.debug(f"User {request.user.username} has role: {user_role}")
                
                if user_role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    logger.warning(f"Access denied for user {request.user.username} with role {user_role}")
                    messages.error(request, f"Access denied. Your role ({user_role}) does not have permission.")
                    return redirect('dashboard')
            except Exception as e:
                logger.error(f"Role check failed for user {request.user.username}: {str(e)}")
                messages.error(request, "Role not assigned. Please contact administrator.")
                return redirect('dashboard')
        return wrapper
    return decorator