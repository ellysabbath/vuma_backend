from django.db import models

class Partner(models.Model):
    PARTNER_TYPE_CHOICES = (
        ('development', 'Development Partner'),
        ('environmental', 'Environmental Partner'),
        ('corporate', 'Corporate Partner'),
        ('ngo', 'NGO Partner'),
        ('government', 'Government Partner'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('inactive', 'Inactive'),
    )
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50, choices=PARTNER_TYPE_CHOICES, default='development')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    since = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    projects_count = models.IntegerField(default=0)
    logo_base64 = models.TextField(blank=True, null=True)
    focus_areas = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-since']