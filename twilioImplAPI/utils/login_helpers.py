import hashlib
import secrets
import base64
import re

from datetime import datetime, timedelta, timezone
from django.conf import settings
from twilioImplAPI.models import Login, User, Phone
from twilioImplAPI.utils.jwt_helpers import generate_jwt


def validate_phone_number(phone_number):
    """
    Validate phone number format.
    
    Args:
        phone_number (str): Phone number to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Basic phone number validation (E.164 format)
    pattern = r'^\+[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone_number))


def generate_salt():
    """
    Generate a new random salt.
    
    Returns:
        str: A base64 encoded random salt
    """
    salt = secrets.token_bytes(16)
    return base64.b64encode(salt).decode('utf-8') 

def password_hasher(password, salt=None, iterations=100000):
    """
    Hash a password using PBKDF2 with SHA-256.
    
    Args:
        password (str): The plain text password to hash
        salt (str, optional): Salt to use for hashing. If None, generates a new salt.
        iterations (int): Number of iterations for PBKDF2 (default: 100000)
    
    Returns:
        tuple: (hashed_password, salt) where both are base64 encoded strings
    """
    if salt is None:
        # Generate a new random salt
        salt = base64.b64decode(generate_salt())
    else:
        # Decode salt from base64 if provided
        salt = base64.b64decode(salt)
    
    # Hash the password using PBKDF2 with SHA-256
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    
    # Encode both hash and salt as base64 for storage
    hashed_b64 = base64.b64encode(hashed).decode('utf-8')
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    
    return hashed_b64, salt_b64


def verify_password(password, hashed_password, salt, iterations=100000):
    """
    Verify a password against its hash and salt.
    
    Args:
        password (str): The plain text password to verify
        hashed_password (str): The stored hash (base64 encoded)
        salt (str): The stored salt (base64 encoded)
        iterations (int): Number of iterations for PBKDF2 (default: 100000)
    
    Returns:
        bool: True if password matches, False otherwise
    """
    # Hash the provided password with the stored salt
    test_hash, _ = password_hasher(password, salt, iterations)
    
    # Compare the hashes
    return test_hash == hashed_password

def username_verification(username):
    """
    Check if username already exists.
    
    Args:
        username (str): Username to check
    
    Returns:
        bool: True if username exists, False otherwise
    """
    if not username or not isinstance(username, str):
        return False
    
    # Basic sanitization - remove whitespace and limit length
    username = username.strip()
    if len(username) > 100 or len(username) < 1:
        return False
    
    return Login.objects.filter(username=username).exists()

def get_or_create_phone(phone_number):
    """
    Create or get a phone number record.
    
    Args:
        phone_number (str): The phone number
    
    Returns:
        Phone: The phone instance
    """
    phone, created = Phone.objects.get_or_create(phone_number=phone_number)
    return phone

def create_user(data):
    """
    Create a new user with associated phone number.
    """
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    communication_preference = data.get('communication_preference')
    
    # Validate phone number format
    if not validate_phone_number(phone_number):
        raise ValueError("Invalid phone number format. Use E.164 format (e.g., +1234567890)")
    
    # Create or get the phone number first
    phone = get_or_create_phone(phone_number)
    
    # Create the user with the phone foreign key
    user = User.objects.create(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone,
        communication_preference=communication_preference
    )
    
    return user

def verify_login(username, password):
    """
    Verify login credentials using stored salt.
    """
    try:
        login = Login.objects.get(username=username)
        # Verify password using stored salt
        is_valid = verify_password(password, login.password, login.salt)
        return is_valid, login
    except Login.DoesNotExist:
        return False, None

def create_login(data):
    username = data.get('username')
    password = data.get('password')
    user_id = data.get('user_id')
    
    # Hash the password before storing
    hashed_password, salt = password_hasher(password)
    
    login = Login.objects.create(
        username=username,
        password=hashed_password,
        salt=salt,
        user_id=user_id
    )
    
    return login
