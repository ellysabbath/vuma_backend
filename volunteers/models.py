from django.db import models

class Volunteer(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    join_date = models.CharField(max_length=100)
    hours_contributed = models.IntegerField(default=0)
    projects_participated = models.IntegerField(default=0)
    image_base64 = models.TextField(blank=True, null=True)
    bio = models.TextField()
    achievements = models.JSONField(default=list, blank=True)
    social = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-hours_contributed']