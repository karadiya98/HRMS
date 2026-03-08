from django.db import models

class Attendance(models.Model):
    
    username = models.CharField(max_length=150, default='Unknown') 
    date = models.DateField()
    check_in = models.TimeField()
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Absent')

    def __str__(self):
        return f"{self.username} - {self.date}"