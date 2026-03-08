from django.urls import path
from .views import cmpregister,home,attendance,leave,tasks,adminhomepage,adminsitedetailpage,salary,leave_at_admin,attendance_at_admin,tasks_at_admin,salary_at_admin,login,profile,admin_profile

urlpatterns = [
    path('',cmpregister, name='cmpregister'),
    path('login',login,name='login'),
    path('home',home, name='home'),
    path('attendance',attendance, name='attendance'),
    path('leave',leave, name='leave'),
    path('tasks',tasks, name='tasks'),
    path('salary',salary,name='salary'),
    path('profile',profile,name='profile'),
   
# ------------------------------------- Admin site is below -----------------------------------------------------
    
    path('adminhomepage',adminhomepage,name='adminhomepage'),
    path('adminsitedetailpage',adminsitedetailpage,name='adminsitedetailpage'),
    path('tasks_at_admin',tasks_at_admin,name='tasks_at_admin'),
    path('leave_at_admin',leave_at_admin,name='leave_at_admin'),
    path('attendance_at_admin',attendance_at_admin,name='attendance_at_admin'),
    path('salary_at_admin',salary_at_admin,name='salary_at_admin'),
    path('admin_profile',admin_profile,name='admin_profile'),


]