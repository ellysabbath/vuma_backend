from django.db import models

class Leader(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    full_bio = models.TextField(blank=True)
    # Store base64 image string
    image_base64 = models.TextField(blank=True, null=True)
    image_mime_type = models.CharField(max_length=50, blank=True, default='image/jpeg')
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name
    
    def get_image_html(self):
        """Return image as data URL"""
        if self.image_base64:
            # Check if it's already a complete data URL
            if self.image_base64.startswith('data:image'):
                return self.image_base64
            # Otherwise construct it
            return f"data:{self.image_mime_type};base64,{self.image_base64}"
        return None

class Project(models.Model):
    CATEGORY_CHOICES = [
        ('environment', 'Environment'),
        ('leadership', 'Leadership'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image_base64 = models.TextField(blank=True, null=True)
    image_mime_type = models.CharField(max_length=50, blank=True, default='image/jpeg')
    description = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title
    
    def get_image_html(self):
        if self.image_base64:
            if self.image_base64.startswith('data:image'):
                return self.image_base64
            return f"data:{self.image_mime_type};base64,{self.image_base64}"
        return None

class Testimonial(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(default=5)
    date = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.author} - {self.text[:50]}"

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    date = models.CharField(max_length=50)
    read_time = models.CharField(max_length=50, blank=True)
    image_base64 = models.TextField(blank=True, null=True)
    image_mime_type = models.CharField(max_length=50, blank=True, default='image/jpeg')
    content = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return self.title
    
    def get_image_html(self):
        if self.image_base64:
            if self.image_base64.startswith('data:image'):
                return self.image_base64
            return f"data:{self.image_mime_type};base64,{self.image_base64}"
        return None

class Statistic(models.Model):
    label = models.CharField(max_length=100)
    value = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, blank=True)
    suffix = models.CharField(max_length=10, default='+')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label}: {self.value}"