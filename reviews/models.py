from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

User = get_user_model()

class Assignment(models.Model):
    """
    Model representing an assignment that can be submitted and reviewed
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    max_score = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('reviews:assignment_detail', kwargs={'pk': self.pk})

class Submission(models.Model):
    """
    Model representing a student's submission for an assignment
    """
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    file_upload = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ('assignment', 'submitted_by')
    
    def __str__(self):
        return f"{self.title} by {self.submitted_by.username}"
    
    def get_absolute_url(self):
        return reverse('reviews:submission_detail', kwargs={'pk': self.pk})
    
    def average_score(self):
        """Calculate average score from all reviews"""
        reviews = self.reviews.all()
        if reviews:
            total = sum([review.score for review in reviews])
            return round(total / len(reviews), 2)
        return None

class Review(models.Model):
    """
    Model representing a peer review of a submission
    """
    SCORE_CHOICES = [(i, i) for i in range(1, 11)]  # 1-10 scale
    
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    score = models.IntegerField(choices=SCORE_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(10)])
    feedback = models.TextField()
    strengths = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('submission', 'reviewer')
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.submission.title}"
    
    def get_absolute_url(self):
        return reverse('reviews:review_detail', kwargs={'pk': self.pk})

class ReviewAssignment(models.Model):
    """
    Model to track which submissions a user should review
    """
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_assignments')
    submission_to_review = models.ForeignKey(Submission, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('reviewer', 'submission_to_review')
    
    def __str__(self):
        return f"{self.reviewer.username} reviewing {self.submission_to_review.title}"