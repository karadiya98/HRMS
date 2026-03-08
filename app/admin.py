from django.contrib import admin
from .models.company import Company
from .models.emp_detail import Employee
from .models.attendance  import Attendance
from .models.leave import LeaveRequest
from .models.task import Task

class CompanyAdmin(admin.ModelAdmin):
    # These fields must match exactly with what you defined in company.py
    list_display = ('com_id','companyname', 'companyregistration_date', 'adminemail','adminname','adminid','adminpassword')
    search_fields = ('companyname',)

class EmpDetail(admin.ModelAdmin):
    list_display=('emp_id','company','fullname','login_id','password','joining_date')   

class attendance(admin.ModelAdmin):
    list_display=('username','date','check_in','check_out','status')

class leave(admin.ModelAdmin):
    list_display=('username','leave_type','start_date','end_date','reason','status')    

class tasktable(admin.ModelAdmin):
    list_display=('username','title','description','deadline','status','github_url')    

# Register the model with the admin class
admin.site.register(Company, CompanyAdmin)
admin.site.register(Employee,EmpDetail)
admin.site.register(Attendance,attendance)
admin.site.register(LeaveRequest,leave)
admin.site.register(Task,tasktable)