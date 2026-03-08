from django.db import models
from .emp_detail import Employee

class LeaveRequest(models.Model):
    LEAVE_TYPES = [('Sick', 'Sick'), ('Casual', 'Casual'), ('Paid', 'Paid')]
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]

    
    username = models.CharField(max_length=150, default='Unknown') 
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')