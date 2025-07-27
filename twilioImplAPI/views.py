from django.shortcuts import render
from django.http import JsonResponse

from twilioImplAPI.utils.login_helpers import create_login, create_user, username_verification
from .models import Login, User

# Create your views here.
def create_user_and_login(request):
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
    