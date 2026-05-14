from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Home
    path('', views.index, name='index'),
    path('job/details/<int:job_id>/', views.job_details, name='job_details'),

    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/jobs/', views.student_jobs, name='student_jobs'),
    path('student/applied/', views.student_applied, name='student_applied'),
    
    # Job Application processing path
    path('apply/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    
    # Main Admin Dashboard Layout
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # FIXED: Points directly to the admin_add_jobs function
    path('admin-dashboard/add-jobs/', views.admin_add_jobs, name='admin_add_jobs'),
    
    # FIXED: Points directly to the admin_manage_students function
    path('admin-dashboard/manage-students/', views.admin_manage_students, name='admin_manage_students'),                                      

    # Company URLs
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/applicants/', views.company_applicants, name='company_applicants'),
    path('company/post-job/', views.company_post_jobs, name='company_post_jobs'),
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)