from django.db import models

class Event(models.Model):
    TYPE_CHOICES = (
        ('Online', 'Online'),
        ('In-Person', 'In-Person'),
        ('Webinar', 'Webinar'),
        ('Hybrid', 'Hybrid'),
    )
    
    title = models.CharField(max_length=200)
    date = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    time = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    image_base64 = models.TextField(blank=True, null=True)
    description = models.TextField()
    full_description = models.TextField(blank=True)
    speakers = models.JSONField(default=list, blank=True)
    capacity = models.IntegerField(default=100)
    registered = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']