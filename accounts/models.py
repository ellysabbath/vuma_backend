from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('volunteer', 'Volunteer'),
        ('innovator', 'Innovator'),
        ('partner', 'Partner'),
    )
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    )
    
    # Make email unique and the username field
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='volunteer')
    is_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True)
    profile_picture = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    availability = models.CharField(max_length=100, blank=True)
    total_hours = models.IntegerField(default=0)
    joined_date = models.DateField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email