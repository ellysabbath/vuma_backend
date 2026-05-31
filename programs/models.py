from django.db import models

class Program(models.Model):
    title = models.CharField(max_length=200)
    icon = models.CharField(max_length=100, default='fas fa-lightbulb')
    color = models.CharField(max_length=50, default='#F9C74F')
    description = models.TextField()
    features = models.JSONField(default=list)
    full_description = models.TextField()
    duration = models.CharField(max_length=100)
    eligibility = models.CharField(max_length=200)
    certification = models.CharField(max_length=200)
    outcomes = models.JSONField(default=list)
    image_base64 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['id']


class Project(models.Model):
    CATEGORY_CHOICES = (
        ('leadership', 'Leadership'),
        ('environment', 'Environment'),
        ('technology', 'Technology'),
        ('education', 'Education'),
    )
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='leadership')
    description = models.TextField()
    image_base64 = models.TextField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']