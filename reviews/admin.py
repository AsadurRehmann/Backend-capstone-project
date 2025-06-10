from django.contrib import admin
from .models import Assignment, Submission, Review, ReviewAssignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'due_date', 'max_score', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'assignment', 'submitted_by', 'submitted_at', 'average_score']
    list_filter = ['submitted_at', 'assignment']
    search_fields = ['title', 'submitted_by__username', 'assignment__title']
    readonly_fields = ['submitted_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('assignment', 'submitted_by')
    
    def average_score(self, obj):
        score = obj.average_score()
        return f"{score}/10" if score else "No reviews yet"
    average_score.short_description = "Average Score"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['submission', 'reviewer', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['submission__title', 'reviewer__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('submission', 'reviewer')

@admin.register(ReviewAssignment)
class ReviewAssignmentAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'submission_to_review', 'assignment', 'completed', 'assigned_at']
    list_filter = ['completed', 'assigned_at']
    search_fields = ['reviewer__username', 'submission_to_review__title']
    readonly_fields = ['assigned_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'reviewer', 'submission_to_review', 'assignment'
        )