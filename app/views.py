from django.shortcuts import render,redirect
from django.contrib import messages
from .models.company import Company
from .models.emp_detail import Employee
from .models.attendance import Attendance
from .models.leave import LeaveRequest
from .models.task import Task
from .templates.adminsite import *
from django.utils import timezone


def login(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        loginid = request.POST.get('loginid')
        password = request.POST.get('password')

        # 1. Basic validation
        if not loginid or not password:
            messages.error(request, "Please fill all required fields.")
            return render(request, 'login.html')

        # 2. Admin Login Logic
        if role == "admin":
            # Check if a company exists with this ID and Password
            # Note: In a real app, use password hashing!
            admin_user = Company.objects.filter(adminid=loginid, adminpassword=password).first()
          
            
            if admin_user:
                # # Save session data if needed
                request.session['globaladmin'] = admin_user.adminname
                return redirect('adminhomepage')
            else:
                messages.error(request, "Invalid Admin Credentials.")

        # 3. Employee Login Logic
        else:
            # Check if an employee exists with this ID and Password
            emp_user = Employee.objects.filter(login_id=loginid, password=password).first()

            if emp_user:
                request.session['globalusername'] = emp_user.fullname
                return redirect('home')
            else:
                messages.error(request, "Invalid Employee Credentials.")
    return render(request, 'login.html')


def cmpregister(request):
    if request.method == 'POST':
        companyname = request.POST.get('companyname')
        industry = request.POST.get('industryname')
        adminname = request.POST.get('adminname')
        companyemail = request.POST.get('adminemail')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        # making loginid for admin
        prefix = adminname[:2]
        loginid = f"{prefix}{password}"

        # 1. Validation
        if not all([companyname, industry, adminname, companyemail, password, confirm_password]):
            messages.error(request, "Please fill all required parameters.")
            return render(request, 'cmpregister.html')
        
        if Company.objects.filter(companyname=companyname).exists():
            messages.error(request, "Company is already registered")
            return render(request, 'cmpregister.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'cmpregister.html')
        
        # 2. Saving (Note the correct field names)
        new_user = Company(
            companyname=companyname,
            industry=industry,
            adminname=adminname,
            adminemail=companyemail,
            adminpassword=password, # Fixed from password=password
            adminid=loginid         # Must be string if your model says CharField
        ) 
        new_user.save()
        messages.success(request, "Workspace Deployed Successfully!")
        return render(request,'adminhomepage.html')
    return render(request, 'cmpregister.html')


def home(request):
    current_user = request.session.get('globalusername')
    today = timezone.now().date()
    
    # - Today must be >= start_date AND today must be <= end_date
    on_leave = LeaveRequest.objects.filter(
        username=current_user,
        status='Approved',
        start_date__lte=today,
        end_date__gte=today
    ).exists()

    if on_leave:
        user_status = "Leave"
    else:
        # 2. If not on leave, check Attendance
        attendance_entry = Attendance.objects.filter(username=current_user, date=today).last()
        user_status = attendance_entry.status if attendance_entry else "Absent"

    return render(request, 'home.html', {
        'emp': Employee.objects.all(),
        'status': user_status,
        'globalusername': current_user
    })




def attendance(request):
    current_session_user = request.session.get('globalusername')
    today = timezone.now().date()
    now_time = timezone.now().time()

    # 1. NEW: Check if the user is currently on an Approved Leave
    is_on_leave = LeaveRequest.objects.filter(
        username=current_session_user,
        status='Approved',
        start_date__lte=today,
        end_date__gte=today
    ).exists()

    # 2. Look for today's record for this user
    attendance_record = Attendance.objects.filter(username=current_session_user, date=today).first()

    if request.method == "POST":
        action = request.POST.get('action')

        if action == "check_in":
            # BLOCK CHECK-IN IF ON LEAVE
            if is_on_leave:
                messages.error(request, "You are currently on approved leave. No need to check in!")
            elif not attendance_record:
                Attendance.objects.create(
                    username=current_session_user,
                    date=today,
                    check_in=now_time,
                    status='Present'
                )
                messages.success(request, f"Welcome {current_session_user}! Checked in successfully.")
            else:
                messages.warning(request, "Already checked in.")

        elif action == "check_out":
            if attendance_record and not attendance_record.check_out:
                attendance_record.check_out = now_time
                attendance_record.save()
                messages.success(request, "Checked out successfully!")
            else:
                messages.warning(request, "Already checked out or no check-in found.")

        return redirect('attendance')

    # Fetch logs for the table
    logs = Attendance.objects.filter(username=current_session_user).order_by('-date', '-check_in')

    context = {
        'logs': logs,
        'checked_in': attendance_record is not None,
        'checked_out': attendance_record.check_out is not None if attendance_record else False,
        'is_on_leave': is_on_leave  # Pass this to HTML to hide the button
    }
    return render(request, 'attendance.html', context)

def leave(request):
    # Get the user from session
    current_user = request.session.get('globalusername')

    if request.method == "POST":
        # Get data from the modal form
        l_type = request.POST.get('leave_type')
        s_date = request.POST.get('start_date')
        e_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        # Create the record in the database
        LeaveRequest.objects.create(
            username=current_user,
            leave_type=l_type,
            start_date=s_date,
            end_date=e_date,
            reason=reason,
            status='Pending'
        )
        
        messages.success(request, "Leave request submitted successfully!")
        return redirect('leave')

    # Show only the current user's leaves
    user_leaves = LeaveRequest.objects.filter(username=current_user).order_by('-start_date')
    
    return render(request, 'leave.html', {'leaves': user_leaves})
    

    
def tasks(request):
    # Get user from session
    current_user = request.session.get('globalusername')
    
    if not current_user:
        return redirect('login')  # Security: redirect if not logged in

    if request.method == "POST":
        task_id = request.POST.get('task_id')
        github_url = request.POST.get('github_url')
        
        # Find task and update only if github_url is provided
        if github_url:
            task = Task.objects.get(id=task_id, username=current_user)
            task.github_url = github_url
            task.status = 'Completed'
            task.save()
        return redirect('tasks')

    # Fetch tasks assigned to the current user
    user_tasks = Task.objects.filter(username=current_user).order_by('-id')
    
    return render(request, 'tasks.html', {
        'tasks': user_tasks,
        'current_user': current_user
    })


def salary(request):
    return render(request,'salary.html')

def profile(request):
    # 1. Get the name from session
    employeename = request.session.get('globalusername')
    # 2. Fetch the specific employee record
    userdata = Employee.objects.filter(fullname=employeename).first()
    # 3. Pass it to the template
    return render(request, 'profile.html', {'user': userdata})



# --------------------------------------- Admin site is below -------------------------------------------
def adminhomepage(request):
    if request.method == "POST":
        # 1. Get all form data
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        designation = request.POST.get('designation')
        joining_date = request.POST.get('joining_date')
        password = request.POST.get('password')
        # login_id = request.POST.get('login_id')
        company_id = request.POST.get('company') # This comes from the <select>


        prefix = fullname[:2]
        loginid = f"{designation[:3].upper()}_{prefix}{password[:2]}786"

        try:
            # 2. Convert string ID to Integer and look up by 'com_id'
            company_instance = Company.objects.get(com_id=int(company_id))

            # 3. Save the Employee
            Employee.objects.create(
                fullname=fullname,
                email=email,
                designation=designation,
                joining_date=joining_date,
                login_id=loginid,
                password=password,
                company=company_instance 
            )
            return redirect('adminhomepage')
            
        except (Company.DoesNotExist, ValueError, TypeError) as e:
            print(f"Error saving employee: {e}")
           
    employees = Employee.objects.all()
    companies = Company.objects.all() 

    return render(request, 'adminsite/adminhomepage.html', {
        'employees': employees,
        'companies': companies,
    })




def adminsitedetailpage(request):
    # 1. Try to get name from the URL
    emp_name = request.GET.get('name')
    
    if emp_name:
        request.session['globaluser_admin'] = emp_name
    else:
        emp_name = request.session.get('globaluser_admin')

    # Handle the empty case to avoid database errors
    if not emp_name:
        # Redirect back to home if no user is selected
        from django.shortcuts import redirect
        return redirect('adminhomepage')

    # Fetch data
    profiledata = Employee.objects.filter(fullname=emp_name)

    # FIX: Combine everything into ONE dictionary here
    context = {
        'name': emp_name,
        'empdata': profiledata
    }
    
    return render(request, 'adminsite/adminsitedetailpage.html', context)




def attendance_at_admin(request):
    # Get the name from session (saved from the profile/card click)
    emp_name = request.session.get('globaluser_admin')
    
    if not emp_name:
        from django.shortcuts import redirect
        return redirect('adminhomepage')

    # Fetch all attendance records for this specific user
    attendance_records = Attendance.objects.filter(username=emp_name).order_by('-date')
    
    context = {
        'name': emp_name,
        'records': attendance_records
    }
    return render(request, 'adminsite/attendance_at_admin.html', context)




def tasks_at_admin(request):

    global_admin = request.session.get('globaluser_admin')

    if request.method == "POST":
        action = request.POST.get('action')
        
        # 1. CREATE TASK
        if action == "create":
            Task.objects.create(
                username=global_admin,
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                deadline=request.POST.get('deadline'),
                status=request.POST.get('status'),
                github_url=request.POST.get('github_url')
            )
        
        # 2. DELETE TASK
        elif action == "delete":
            task_id = request.POST.get('task_id')
            Task.objects.filter(id=task_id, username=global_admin).delete()

        # 3. UPDATE STATUS (Toggle)
        elif action == "toggle_status":
            task_id = request.POST.get('task_id')
            task = Task.objects.get(id=task_id)
            task.status = 'Completed' if task.status == 'Pending' else 'Pending'
            task.save()

        return redirect('tasks_at_admin')

    # GET logic: Fetch and show tasks
    tasks = Task.objects.filter(username=global_admin).order_by('-id')
    return render(request, 'adminsite/tasks_at_admin.html', {'tasks': tasks})




def leave_at_admin(request):
    # 1. Get the employee name from the session
    emp_name = request.session.get('globaluser_admin')
    
    if not emp_name:
        return redirect('adminhomepage')

    # 2. Handle the "Approve" or "Reject" button click
    if request.method == "POST":
        leave_id = request.POST.get('leave_id')
        new_status = request.POST.get('status') # This will be 'Approved' or 'Rejected'
        
        # Update the database
        leave_record = LeaveRequest.objects.get(id=leave_id)
        leave_record.status = new_status
        leave_record.save()
        
        # Refresh the page to show the updated status
        return redirect('leave_at_admin')

    # 3. Fetch all leave requests for this specific employee
    leaves = LeaveRequest.objects.filter(username=emp_name).order_by('-start_date')
    
    return render(request, 'adminsite/leave_at_admin.html', {
        'leaves': leaves, 
        'name': emp_name
    })


def salary_at_admin(request):
    return render(request,'adminsite/salary_at_admin.html')


def admin_profile(request):
   
    admin_name_from_session = request.session.get('globaladmin')
    admin_data = Company.objects.get(adminname=admin_name_from_session)

  # Logic for initial and a random "System Status" for a modern feel
    context = {
        'admin': admin_data,
        'initial': admin_name_from_session[0].upper(),
        'status': 'System Active'
    }
    return render(request, 'adminsite/admin_profile.html', context)