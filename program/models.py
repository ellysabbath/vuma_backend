from django.db import models

class Program(models.Model):
    """
    Main Program Model - e.g., Youth Leadership, Environmental Resilience, Youth and Opportunity
    """
    PROGRAM_CATEGORIES = [
        ('youth_leadership', 'Youth Leadership'),
        ('environmental_resilience', 'Environmental Resilience and Adaptation'),
        ('youth_opportunity', 'Youth and Opportunity'),
    ]
    
    name = models.CharField(max_length=255, help_text="Program name e.g., Youth Leadership")
    category = models.CharField(max_length=100, choices=PROGRAM_CATEGORIES, unique=True)
    description = models.TextField(blank=True, null=True, help_text="Brief description of the program")
    icon = models.CharField(max_length=100, blank=True, null=True, help_text="Font awesome icon class")
    color = models.CharField(max_length=50, default="#0B3B2F", help_text="Theme color for the program")
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Program"
        verbose_name_plural = "Programs"
    
    def __str__(self):
        return self.name


class Activity(models.Model):
    """
    Activity Model - belongs to a Program
    e.g., Youth interschool essay competition, Leadership boot camps, Ziwa letu, etc.
    """
    program = models.ForeignKey(
        Program, 
        on_delete=models.CASCADE, 
        related_name='activities',
        help_text="The program this activity belongs to"
    )
    name = models.CharField(max_length=255, help_text="Activity name e.g., Youth interschool essay competition")
    description = models.TextField(blank=True, null=True, help_text="Brief description of the activity")
    icon = models.CharField(max_length=100, blank=True, null=True, help_text="Font awesome icon class")
    duration = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., 2 days, 1 week, Monthly")
    target_audience = models.CharField(max_length=255, blank=True, null=True, help_text="Who is this activity for?")
    max_participants = models.IntegerField(null=True, blank=True, help_text="Maximum number of participants")
    order = models.IntegerField(default=0, help_text="Display order within program")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        unique_together = ['program', 'name']  # Prevent duplicate activity names within same program
    
    def __str__(self):
        return f"{self.program.name} - {self.name}"


class Explanation(models.Model):
    """
    Explanation Model - belongs to an Activity
    Detailed explanations, steps, benefits, or key points about the activity
    """
    activity = models.ForeignKey(
        Activity, 
        on_delete=models.CASCADE, 
        related_name='explanations',
        help_text="The activity this explanation belongs to"
    )
    title = models.CharField(max_length=255, help_text="Explanation title e.g., Benefits, How it works, Key features")
    content = models.TextField(help_text="Detailed explanation content")
    explanation_type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        choices=[
            ('overview', 'Overview'),
            ('benefits', 'Benefits'),
            ('process', 'Process / How it works'),
            ('requirements', 'Requirements'),
            ('impact', 'Impact'),
            ('testimonial', 'Testimonial'),
            ('other', 'Other'),
        ],
        help_text="Type of explanation"
    )
    order = models.IntegerField(default=0, help_text="Display order within activity")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Explanation"
        verbose_name_plural = "Explanations"
    
    def __str__(self):
        return f"{self.activity.name} - {self.title}"