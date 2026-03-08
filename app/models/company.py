from django.db import models

class Company(models.Model):
    # Company Basic Info
    com_id = models.AutoField(primary_key=True)
    companyname = models.CharField(max_length=255, unique=True)
    companylogo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    companyregistration_date = models.DateTimeField(auto_now_add=True)

    # Primary Admin Details (Linked to this Company)
    adminname = models.CharField(max_length=255)
    adminemail = models.EmailField(unique=True)
    # Stored as CharField to allow for encrypted password strings
    adminpassword = models.CharField(max_length=255) 
    adminid = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.companyname