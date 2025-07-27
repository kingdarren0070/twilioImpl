from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.db import transaction

from twilioImplAPI.utils.login_helpers import create_login, create_user, generate_jwt, username_verification, verify_login
from twilioImplAPI.utils.twilio_helpers import send_sms, make_voice_call
from twilioImplAPI.utils.jwt_helpers import require_jwt_auth
from twilioImplAPI.models import User

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
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'phone_number', 'username', 'password']
        for field in required_fields:
            if not request.POST.get(field):
                return JsonResponse({'message': f'{field} is required'}, status=400)

        # Validate communication preference
        communication_preference = request.POST.get('communication_preference', 'SMS')  # Default to SMS
        valid_preferences = ['SMS', 'Voice']
        if communication_preference not in valid_preferences:
            return JsonResponse({'message': 'communication_preference must be SMS or Voice'}, status=400)

        if username_verification(username):
            return JsonResponse({'message': 'Username already exists'}, status=400)
        
        # Update user_data with validated communication_preference
        user_data['communication_preference'] = communication_preference
        
        try:
            with transaction.atomic():
                user = create_user(user_data)
                
                login_data = {
                    'username': username,
                    'password': password,
                    'user_id': user,
                }
                
                login = create_login(login_data)
                
                token = generate_jwt(user, username)
        except ValueError as e:
            return JsonResponse({'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'message': 'Failed to create user account'}, status=500)

        return JsonResponse({'message': 'User created successfully', 'token': token}, status=201)

class LoginView(View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validate required fields
        if not username or not password:
            return JsonResponse({'message': 'Username and password are required'}, status=400)
        
        is_valid, login = verify_login(username, password)
        
        if is_valid:
            user = login.user_id
            
            try:
                token = generate_jwt(user, username)
            except ValueError as e:
                return JsonResponse({'message': str(e)}, status=500)
            
            return JsonResponse({
                'message': 'Login successful',
                'token': token,
            }, status=200)
        else:
            return JsonResponse({'message': 'Invalid username or password'}, status=401)
    
class NotificationView(View):
    def sms_notification(self, user, message):
        try:
            result = send_sms(user.phone_number.phone_number, message)
            if result['success']:
                return {'success': True, 'message': 'SMS sent successfully'}
            else:
                return {'success': False, 'message': 'Failed to send SMS', 'error': result['error']}
        except Exception as e:
            return {'success': False, 'message': 'Failed to send SMS', 'error': str(e)}

    def voice_notification(self, user, message):
        try:
            result = make_voice_call(user.phone_number.phone_number, message)
            if result['success']:
                return {'success': True, 'message': 'Voice call initiated successfully'}
            else:
                return {'success': False, 'message': 'Failed to make voice call', 'error': result['error']}
        except Exception as e:
            return {'success': False, 'message': 'Failed to make voice call', 'error': str(e)}

    @require_jwt_auth
    def post(self, request):
        message = request.POST.get('message')

        if not message or not message.strip():
            return JsonResponse({'message': 'Message is required and cannot be empty'}, status=400)
        
        # Validate message length (Twilio SMS limit is 1600 characters)
        if len(message) > 1600:
            return JsonResponse({'message': 'Message too long (max 1600 characters)'}, status=400)
        
        user_info = request.user_info
        user_id = user_info['user_id']
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User not found'}, status=404)
        except AttributeError:
            return JsonResponse({'message': 'User has no phone number'}, status=400)

        if user.communication_preference == 'SMS':
            result = self.sms_notification(user, message)
        elif user.communication_preference == 'Voice':
            result = self.voice_notification(user, message)
        else:
            return JsonResponse({'message': 'Invalid communication preference'}, status=400)
        
        # Return appropriate response based on result
        if result['success']:
            return JsonResponse({'message': result['message']}, status=200)
        else:
            return JsonResponse({'message': result['message'], 'error': result['error']}, status=500)

