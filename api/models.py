from django.db import models
from django.contrib.auth.models import User

# 1. Student Profile
class StudentProfile(models.Model):
    # Use related_name='student_profile' to easily access this from the User object
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    phone = models.CharField(max_length=15)
    course = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True) 
    skills = models.TextField(help_text="Enter skills separated by commas")

    def __str__(self):
        return self.user.username

# 2. Company Profile
class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, default="IT")
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.company_name

# 3. Job Table
class Job(models.Model):
    title = models.CharField(max_length=200)
    # Changed: Jobs should always belong to a company to show on a dashboard
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=50)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=60.00)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.company.company_name}"

# 4. Application Table
class Application(models.Model): 
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
        ('Selected', 'Selected'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='my_applications')
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.student.user.username} -> {self.job.title}"