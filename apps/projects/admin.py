from django.contrib import admin
from .models import ResearchProject, ProjectReview


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'applicant', 'college', 'budget', 'status', 'created_at']
    list_filter = ['status', 'category', 'college']
    search_fields = ['title', 'applicant__username', 'college']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 20


@admin.register(ProjectReview)
class ProjectReviewAdmin(admin.ModelAdmin):
    list_display = ['project', 'reviewer', 'result', 'reviewed_at']
    list_filter = ['result']
    search_fields = ['project__title', 'reviewer__username']
    readonly_fields = ['reviewed_at']
    ordering = ['-reviewed_at']
