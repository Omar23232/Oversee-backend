# # login/middleware.py
# from django.shortcuts import redirect

# class InternalNavMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Skip middleware for:
#         # 1. Admin URLs
#         # 2. Static files
#         # 3. Unresolved routes
#         if (request.path.startswith('/admin/') or 
#             request.path.startswith('/static/') or 
#             not hasattr(request, 'resolver_match') or 
#             not request.resolver_match):
#             return self.get_response(request)
            
#         protected_routes = ['dashboard', 'devices', 'alerts']
#         current_route = request.resolver_match.url_name
        
#         if current_route in protected_routes:
#             referer = request.META.get('HTTP_REFERER', '')
#             if not referer.startswith(request.build_absolute_uri('/')):
#                 return redirect('dashboard')
        
#         return self.get_response(request)