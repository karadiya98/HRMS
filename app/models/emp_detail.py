from django.db import models
from .company import Company

class Employee(models.Model):
    emp_id = models.AutoField(primary_key=True)
    # Linking Employee to Company
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    designation = models.CharField(max_length=100)
    joining_date = models.DateField()
    login_id = models.CharField(max_length=50, unique=True) # Generated ID
    password = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.fullname} ({self.company.companyname})"