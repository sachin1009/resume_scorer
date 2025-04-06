from django.contrib import admin
from .models import JobRole, Resume, ResumeScore

@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_at')
    list_filter = ('uploaded_at',)
    date_hierarchy = 'uploaded_at'

@admin.register(ResumeScore)
class ResumeScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_role', 'experience_years', 'score', 'created_at')
    list_filter = ('job_role', 'created_at')
    date_hierarchy = 'created_at'