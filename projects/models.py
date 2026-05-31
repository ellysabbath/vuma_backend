from django.db import models

class Project(models.Model):
    CATEGORY_CHOICES = (
        ('Environment', 'Environment'),
        ('Leadership', 'Leadership'),
        ('Technology', 'Technology'),
        ('Education', 'Education'),
    )
    
    STATUS_CHOICES = (
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Planning', 'Planning'),
        ('On Hold', 'On Hold'),
    )
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Environment')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Planning')
    progress = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    image_base64 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']