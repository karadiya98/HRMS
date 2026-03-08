from django.db import models
from .emp_detail import Employee

class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

   
    username = models.CharField(max_length=255,default='unknown')
    # Task Details
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    
    # Progress tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    github_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.username})"
    
    