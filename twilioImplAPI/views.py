from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings

from twilioImplAPI.utils.login_helpers import create_login, create_user, username_verification, verify_login
from .models import Login, User

# Create your views here.
class CreateUserView(View):
    def post(self, request):
        user_data = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone_number': request.POST.get('phone_number'),
            'communication_preference': request.POST.get('communication_preference'),
        }

        
        username = request.POST.get('username')
        password = request.POST.get('password')
        

        if username_verification(username):
            return JsonResponse({'message': 'Username already exists'}, status=400)
        
        user = create_user(user_data)

        login_data = {
            'username': username,
            'password': password,
            'user_id': user,
        }

        login = create_login(login_data)

        return JsonResponse({'message': 'User created successfully'}, status=201)

class LoginView(View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        is_valid, login = verify_login(username, password)
        
        if is_valid:
            user = login.user_id
            
            # Create JWT payload
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
            
            # Generate JWT token (you'll need to set SECRET_KEY in settings)
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            
            return JsonResponse({
                'message': 'Login successful',
                'token': token,
            }, status=200)
        else:
            return JsonResponse({'message': 'Invalid username or password'}, status=401)
    