from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
import uuid

class Donation(models.Model):
    DONATION_TYPES = [
        ('one-time', 'One-Time'),
        ('monthly', 'Monthly'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa', 'M-PESA'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]
    
    # Reference Information
    reference_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Donation Details
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES, default='one-time')
    amount = models.DecimalField(max_digits=12, decimal_places=0, help_text="Amount in TZS")
    
    # Donor Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True)
    
    # Status Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True, null=True)
    transaction_code = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Admin Notes
    admin_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Donation'
        verbose_name_plural = 'Donations'
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        super().save(*args, **kwargs)
    
    def generate_reference_number(self):
        import time
        import random
        prefix = 'VUMA'
        timestamp = str(int(time.time() * 1000))[-8:]
        random_num = str(random.randint(1, 999)).zfill(3)
        return f"{prefix}-{timestamp}-{random_num}"
    
    def mark_as_completed(self, payment_method, transaction_code):
        self.status = 'completed'
        self.payment_method = payment_method
        self.transaction_code = transaction_code
        self.completed_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.reference_number} - {self.full_name} - {self.amount} TZS"


class DonationLog(models.Model):
    """Log all donation-related activities for tracking"""
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.donation.reference_number} - {self.action} - {self.created_at}"