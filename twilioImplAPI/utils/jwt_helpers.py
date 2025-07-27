import jwt
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime, timezone, timedelta

def generate_jwt(user, username):
    """
    Generate JWT token for user authentication.
    
    Args:
        user (User): User object
        username (str): Username
    
    Returns:
        str: JWT token
    """
    try:
        payload = {
            'user_id': user.id,
            'username': username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number.phone_number,
            'communication_preference': user.communication_preference,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24),  # 24 hour expiration
            'iat': datetime.now(timezone.utc)
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token
    except Exception as e:
        raise ValueError(f"Failed to generate JWT token: {str(e)}")
