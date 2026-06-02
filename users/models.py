from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('shop', 'Магазин'),
        ('buyer', 'Покупатель'),
    )
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    type = models.CharField(max_length=5, choices=USER_TYPE_CHOICES, default='buyer')
    company = models.CharField(max_length=40, blank=True)
    position = models.CharField(max_length=40, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.email} ({self.type})"
