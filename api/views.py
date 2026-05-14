from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from .models import StudentProfile, CompanyProfile, Job, Application

# --- 1. HOME / INDEX ---
def index(request):
    # FIXED: Optimized to pull the related company profile fields directly in a single database lookup
    jobs_from_db = Job.objects.select_related('company').all().order_by('-id')
    return render(request, 'index.html', {'jobs': jobs_from_db})


# NEW ACTIONS: Individual landing sheet presentation page for job details lookup
def job_details(request, job_id):
    # FIXED: Finds the exact clicked job card row item or securely fails into a clean 404 message page
    target_job = get_object_or_404(Job.objects.select_related('company'), id=job_id)
    return render(request, 'job-details.html', {'job': target_job})


# --- 2. REGISTRATION ---
def register(request):
    if request.method == "POST":
        u_type = request.POST.get('user_type')
        u_name = request.POST.get('username')
        u_email = request.POST.get('email')
        u_pass = request.POST.get('password')
        
        # Check if username already exists
        if User.objects.filter(username=u_name).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'register.html')

        # 1. Create the Base User
        new_user = User.objects.create_user(username=u_name, email=u_email, password=u_pass)
        
        # 2. Handle Profile Creation
        if u_type == "student":
            StudentProfile.objects.create(
                user=new_user,
                phone=request.POST.get('phone'),
                course=request.POST.get('course'),
                percentage=request.POST.get('percentage') or 0,
                skills=request.POST.get('skills'),
                resume=request.FILES.get('resume')
            )
        elif u_type == "company":
            CompanyProfile.objects.create(
                user=new_user,
                company_name=request.POST.get('company_name'),
                phone=request.POST.get('phone'),
                website=request.POST.get('website', ''),
                industry=request.POST.get('industry', 'IT')
            )

        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')
    
    return render(request, 'register.html')


# --- 3. LOGIN ---
def login_view(request):
    if request.method == "POST":
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        user_type = request.POST.get('user_type')

        try:
            target_user = User.objects.get(email=email_input)
            user = authenticate(request, username=target_user.username, password=password_input)
        except User.DoesNotExist:
            user = None

        if user is not None:
            auth_login(request, user)
            
            # Route users based on their custom profiles dashboard types
            if user.is_staff or user_type == "admin":
                return redirect('admin_dashboard')
            elif user_type == "company":
                return redirect('company_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'login.html')


# --- 4. STUDENT MODULE ---
@login_required
def student_dashboard(request):
    try:
        student_prof = StudentProfile.objects.get(user=request.user)
        my_applications = Application.objects.filter(student=student_prof).select_related('job__company')
        
        context = {
            'student': student_prof,
            'applied_jobs': my_applications, 
            'total_jobs_count': Job.objects.count(),
            'applied_count': my_applications.count(),
        }
        return render(request, 'student-dashboard.html', context)
    except StudentProfile.DoesNotExist:
        return redirect('login')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudentProfile

@login_required
def student_profile(request):
    # Fetch the logged-in student profile record
    student = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == "POST":
        student.phone = request.POST.get('phone')
        student.course = request.POST.get('course')
        
        # FIXED: Changed from 'percentage' to 'cgpa' to match your form input name property!
        student.percentage = request.POST.get('cgpa') 
        
        student.skills = request.POST.get('skills')
        student.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('student_profile') # Safely redirect to avoid double form submissions
        
    return render(request, 'student-profile.html', {'student': student})

@login_required
def student_jobs(request):
    # FIXED: Formats available positions grid smoothly while preserving the related company user fields
    jobs = Job.objects.select_related('company__user').all()
    return render(request, 'student-jobs.html', {'jobs': jobs})


# NEW ACTION: Processes the interactive student application click behaviors
@login_required
def apply_for_job(request, job_id):
    try:
        student_prof = StudentProfile.objects.get(user=request.user)
        job_record = get_object_or_404(Job, id=job_id)
        
        # Stop duplicate submissions
        already_applied = Application.objects.filter(student=student_prof, job=job_record).exists()
        
        if already_applied:
            messages.warning(request, "You have already applied for this position.")
        else:
            Application.objects.create(
                student=student_prof,
                job=job_record,
                status="Applied"
            )
            messages.success(request, f"Application submitted successfully for {job_record.title}!")
            
    except StudentProfile.DoesNotExist:
        messages.error(request, "Account error: Student profile data missing.")
        
    return redirect('student_jobs')


@login_required
def student_applied(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
        applications = Application.objects.filter(student=student).select_related('job__company__user')
    except StudentProfile.DoesNotExist:
        applications = []
    
    return render(request, 'student-applied.html', {'applications': applications})


# --- 5. COMPANY MODULE ---
@login_required
def company_dashboard(request):
    # FIXED: The entire workflow is properly wrapped inside a complete 'try' block setup
    try:
        company_prof = CompanyProfile.objects.get(user=request.user)
        my_jobs = Job.objects.filter(company=company_prof)
        my_applications = Application.objects.filter(job__in=my_jobs).select_related('student__user', 'job')
        
        context = {
            # FIXED: Grabs the profile's explicit company business name value instead of the HR username string
            'company_name': company_prof.company_name, 
            'hr_username': company_prof.user.username,   
            'jobs_posted': my_jobs.count(),
            'total_applicants': my_applications.count(),
            'shortlisted_count': my_applications.filter(status='Shortlisted').count(),
            'recent_applications': my_applications.order_by('-id')[:5], 
        }
        return render(request, 'company-dashboard.html', context)
        
    except CompanyProfile.DoesNotExist:
        return redirect('login')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Job, CompanyProfile

@login_required
def company_post_jobs(request):
    # DEBUG: Look at your VS Code terminal to verify who is attempting to post!
    print(f"Logged in user: {request.user.username}, Is Staff: {request.user.is_staff}")

    # Fetch the profile safely using a direct database filter
    company_profile = CompanyProfile.objects.filter(user=request.user).first()
    
    # If this user is NOT registered as a company, do not send them home silently.
    # Let's catch them and tell you about it.
    if not company_profile:
        print(f"ERROR: The user '{request.user.username}' does not have a CompanyProfile in the database!")
        return redirect('company_dashboard') # Keep them in the dashboard context instead of index

    if request.method == "POST":
        job_role = request.POST.get('job_role') 
        package = request.POST.get('package')
        location = request.POST.get('location')
        eligibility = request.POST.get('eligibility')
        description = request.POST.get('description')
        
        # Save securely
        Job.objects.create(
            company=company_profile,
            title=job_role,        
            salary=package,
            description=f"Location: {location}. Eligibility: {eligibility}%. Description: {description}"
        )
        
        # This will redirect smoothly back to your company dashboard view
        return redirect('company_dashboard')
        
    return render(request, 'company-post-jobs.html')
@login_required
def company_applicants(request):
    try:
        company_prof = CompanyProfile.objects.get(user=request.user)
        applicants_list = Application.objects.filter(job__company=company_prof).select_related('student__user', 'job')
        
        if request.method == "POST":
            application_id = request.POST.get('application_id')
            new_status = request.POST.get('status')
            
            app_record = get_object_or_404(Application, id=application_id, job__company=company_prof)
            app_record.status = new_status
            app_record.save()
            return redirect('company_applicants')
            
    except CompanyProfile.DoesNotExist:
        applicants_list = []
        
    return render(request, 'company-applicants.html', {'applicants': applicants_list})


# --- 6. ADMIN MODULE ---
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('login')
        
    all_apps = Application.objects.select_related('student__user', 'job__company__user').all()
    
    context = {
        'total_students': StudentProfile.objects.count(),
        'total_companies': CompanyProfile.objects.count(),
        'jobs_posted': Job.objects.count(),
        'total_selections': all_apps.filter(status='Shortlisted').count(),
        'recent_updates': all_apps.order_by('-id')[:5]  
    }
    
    return render(request, 'admin-dashboard.html', context)

@login_required
def admin_manage_students(request):
    if not request.user.is_staff:
        return redirect('login')
        
    context = {
        'students': StudentProfile.objects.select_related('user').all()
    }
    # FIXED: Added 's' to match "admin-manage-students.html" in your folder tree
    return render(request, 'admin-manage-students.html', context)


@login_required
def admin_add_jobs(request):
    if not request.user.is_staff:
        return redirect('login')
        
    if request.method == "POST":
        company_profile_id = request.POST.get('company_profile_id')
        job_role = request.POST.get('job_role')
        package = request.POST.get('package')
        eligibility = request.POST.get('eligibility')
        description = request.POST.get('description')
        
        company_profile = get_object_or_404(CompanyProfile, id=company_profile_id)
        
        Job.objects.create(
            company=company_profile,
            title=job_role,
            salary=package,
            description=f"Eligibility: {eligibility}. Description: {description}"
        )
        return redirect('admin_dashboard')
            
    context = {
        'companies': CompanyProfile.objects.select_related('user').all()
    }
    # FIXED: Changed "admin-adds-jobs.html" to "admin-add-jobs.html" to match your folder tree
    return render(request, 'admin-add-jobs.html', context)

# --- 7. LOGOUT ---
def logout_view(request):
    auth_logout(request)
    return redirect('index')