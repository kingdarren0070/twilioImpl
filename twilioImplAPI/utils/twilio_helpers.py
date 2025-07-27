from twilio.rest import Client
from django.conf import settings
import os

def get_twilio_client():
    """Get Twilio client instance."""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        raise ValueError("Twilio credentials not found in environment variables")
    
    return Client(account_sid, auth_token)

def send_sms(to_number, message, from_number=None):
    """
    Send SMS message using Twilio.
    """
    try:
        client = get_twilio_client()
        from_number = from_number or os.getenv('TWILIO_PHONE_NUMBER')
        
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        return {
            'success': True,
            'message_sid': message.sid,
            'status': message.status
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def make_voice_call(to_number, twiml_url, from_number=None):
    """
    Make voice call using Twilio.
    """
    try:
        client = get_twilio_client()
        from_number = from_number or os.getenv('TWILIO_PHONE_NUMBER')
        
        call = client.calls.create(
            twiml=f'<Response><Say>{twiml_url}</Say></Response>',
            from_=from_number,
            to=to_number
        )
        
        return {
            'success': True,
            'call_sid': call.sid,
            'status': call.status
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
