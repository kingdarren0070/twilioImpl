from django.db import models

# Create your models here.

class Phone(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.phone_number
    
    class Meta:
        db_table = 'phone'

class User(models.Model):
    COMMUNICATION_CHOICES = [
        ('SMS', 'SMS'),
        ('Voice', 'Voice'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.ForeignKey(Phone, on_delete=models.CASCADE, related_name='users')
    communication_preference = models.CharField(
        max_length=5,
        choices=COMMUNICATION_CHOICES,
        default='SMS'
    )
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        db_table = 'user'

class Login(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    salt = models.CharField(max_length=255, default='')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logins')
    
    def __str__(self):
        return f"{self.username} (User: {self.user_id})"
    
    class Meta:
        db_table = 'login'
