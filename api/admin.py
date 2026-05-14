from django.contrib import admin
from .models import StudentProfile, CompanyProfile, Job, Application

admin.site.register(StudentProfile)
admin.site.register(CompanyProfile)
admin.site.register(Job)
admin.site.register(Application)