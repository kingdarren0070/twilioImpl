import jwt
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime

def verify_jwt_token(token):
    """
    Verify and decode JWT token.
    
    Args:
        token (str): JWT token string
    
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_jwt_auth(view_func):
    """
    Decorator to require JWT authentication for views.
    
    Usage:
        @require_jwt_auth
        def my_view(request):
            # Access user info from request.user_info
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                'message': 'Authorization header required',
                'error': 'Missing or invalid Authorization header'
            }, status=401)
        
        token = auth_header.split(' ')[1]
        payload = verify_jwt_token(token)
        
        if not payload:
            return JsonResponse({
                'message': 'Invalid or expired token',
                'error': 'Authentication failed'
            }, status=401)
        
        # Add user info to request
        request.user_info = payload
        
        return view_func(request, *args, **kwargs)
    
    return wrapper 