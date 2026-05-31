from django.db import models

class News(models.Model):
    title = models.CharField(max_length=200)
    date = models.CharField(max_length=100)
    read_time = models.CharField(max_length=50)
    image_base64 = models.TextField(blank=True, null=True)  # Changed from image URL to base64
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    key_highlights = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'News'