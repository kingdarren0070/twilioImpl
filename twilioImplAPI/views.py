from django.http import JsonResponse
from django.views import View
from django.conf import settings

from twilioImplAPI.utils.login_helpers import create_login, create_user, generate_jwt, username_verification, verify_login
from twilioImplAPI.utils.twilio_helpers import send_sms, make_voice_call

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

        token = generate_jwt(user, username)

        return JsonResponse({'message': 'User created successfully', 'token': token}, status=201)

class LoginView(View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        is_valid, login = verify_login(username, password)
        
        if is_valid:
            user = login.user_id
            
            token = generate_jwt(user, username)
            
            return JsonResponse({
                'message': 'Login successful',
                'token': token,
            }, status=200)
        else:
            return JsonResponse({'message': 'Invalid username or password'}, status=401)
    
class SMSView(View):
    def post(self, request):
        to_number = request.POST.get('to_number')
        message = request.POST.get('message')

        try:
            result = send_sms(to_number, message)
            if result['success']:
                return JsonResponse({'message': 'SMS sent successfully'}, status=200)
            else:
                return JsonResponse({'message': 'Failed to send SMS', 'error': result['error']}, status=500)
        except Exception as e:
            return JsonResponse({'message': 'Failed to send SMS', 'error': str(e)}, status=500)

class VoiceCallView(View):
    def post(self, request):
        to_phone = request.POST.get('to_phone')
        message = request.POST.get('message')

        try:
            result = make_voice_call(to_phone, message)
            if result['success']:
                return JsonResponse({'message': 'Voice call initiated successfully'}, status=200)
            else:
                return JsonResponse({'message': 'Failed to make voice call', 'error': result['error']}, status=500)
        except Exception as e:
            return JsonResponse({'message': 'Failed to make voice call', 'error': str(e)}, status=500)
