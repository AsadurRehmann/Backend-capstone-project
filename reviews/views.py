from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.http import Http404
from .models import Assignment, Submission, Review, ReviewAssignment
from .forms import AssignmentForm, SubmissionForm, ReviewForm
import random

@login_required
def dashboard_view(request):
    """
    Main dashboard showing user's assignments, submissions, and reviews
    """
    # Get user's recent submissions
    recent_submissions = request.user.submissions.all()[:5]
    
    # Get assignments user needs to review
    pending_reviews = ReviewAssignment.objects.filter(
        reviewer=request.user, 
        completed=False
    )[:5]
    
    # Get recent reviews received
    reviews_received = Review.objects.filter(
        submission__submitted_by=request.user
    )[:5]
    
    # Get active assignments
    active_assignments = Assignment.objects.filter(is_active=True)[:5]
    
    context = {
        'recent_submissions': recent_submissions,
        'pending_reviews': pending_reviews,
        'reviews_received': reviews_received,
        'active_assignments': active_assignments,
    }
    
    return render(request, 'reviews/dashboard.html', context)

@login_required
def assignment_list_view(request):
    """
    List all active assignments with search functionality
    """
    assignments = Assignment.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        assignments = assignments.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(assignments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reviews/assignment_list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
def assignment_detail_view(request, pk):
    """
    Display assignment details and allow submission
    """
    assignment = get_object_or_404(Assignment, pk=pk)
    user_submission = None
    
    try:
        user_submission = Submission.objects.get(
            assignment=assignment, 
            submitted_by=request.user
        )
    except Submission.DoesNotExist:
        pass
    
    return render(request, 'reviews/assignment_detail.html', {
        'assignment': assignment,
        'user_submission': user_submission
    })

@login_required
def create_assignment_view(request):
    """
    Create a new assignment (for instructors/admins)
    """
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('reviews:assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm()
    
    return render(request, 'reviews/assignment_form.html', {
        'form': form,
        'title': 'Create Assignment'
    })

@login_required
def submit_assignment_view(request, assignment_pk):
    """
    Submit work for an assignment
    """
    assignment = get_object_or_404(Assignment, pk=assignment_pk)
    
    # Check if user already submitted
    try:
        submission = Submission.objects.get(
            assignment=assignment, 
            submitted_by=request.user
        )
        # User is editing existing submission
        editing = True
    except Submission.DoesNotExist:
        submission = None
        editing = False
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.submitted_by = request.user
            submission.save()
            
            # Assign peers for review (simplified random assignment)
            assign_peer_reviews(submission)
            
            action = 'updated' if editing else 'submitted'
            messages.success(request, f'Assignment {action} successfully!')
            return redirect('reviews:submission_detail', pk=submission.pk)
    else:
        form = SubmissionForm(instance=submission)
    
    return render(request, 'reviews/submission_form.html', {
        'form': form,
        'assignment': assignment,
        'editing': editing
    })

def assign_peer_reviews(submission):
    """
    Assign random peers to review this submission
    """
    # Get other submissions for the same assignment
    other_submissions = Submission.objects.filter(
        assignment=submission.assignment
    ).exclude(submitted_by=submission.submitted_by)
    
    if other_submissions.exists():
        # Randomly select up to 3 reviewers
        reviewers = random.sample(
            list(other_submissions.values_list('submitted_by', flat=True)),
            min(3, len(other_submissions))
        )
        
        for reviewer_id in reviewers:
            ReviewAssignment.objects.get_or_create(
                assignment=submission.assignment,
                reviewer_id=reviewer_id,
                submission_to_review=submission
            )

@login_required
def submission_detail_view(request, pk):
    """
    Display submission details and reviews
    """
    submission = get_object_or_404(Submission, pk=pk)
    reviews = submission.reviews.all()
    
    # Check if current user can view this submission
    can_view = (
        submission.submitted_by == request.user or
        reviews.filter(reviewer=request.user).exists() or
        ReviewAssignment.objects.filter(
            reviewer=request.user,
            submission_to_review=submission
        ).exists()
    )
    
    if not can_view:
        raise Http404("You don't have permission to view this submission")
    
    return render(request, 'reviews/submission_detail.html', {
        'submission': submission,
        'reviews': reviews,
        'average_score': submission.average_score()
    })

@login_required
def review_submission_view(request, submission_pk):
    """
    Create or edit a review for a submission
    """
    submission = get_object_or_404(Submission, pk=submission_pk)
    
    # Check if user is assigned to review this submission
    try:
        review_assignment = ReviewAssignment.objects.get(
            reviewer=request.user,
            submission_to_review=submission
        )
    except ReviewAssignment.DoesNotExist:
        messages.error(request, "You are not assigned to review this submission.")
        return redirect('reviews:dashboard')
    
    # Check if review already exists
    try:
        review = Review.objects.get(
            submission=submission,
            reviewer=request.user
        )
        editing = True
    except Review.DoesNotExist:
        review = None
        editing = False
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.submission = submission
            review.reviewer = request.user
            review.save()
            
            # Mark review assignment as completed
            review_assignment.completed = True
            review_assignment.save()
            
            action = 'updated' if editing else 'submitted'
            messages.success(request, f'Review {action} successfully!')
            return redirect('reviews:submission_detail', pk=submission.pk)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'reviews/review_form.html', {
        'form': form,
        'submission': submission,
        'editing': editing
    })

@login_required
def my_submissions_view(request):
    """
    List current user's submissions
    """
    submissions = request.user.submissions.all()
    
    paginator = Paginator(submissions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reviews/my_submissions.html', {
        'page_obj': page_obj
    })

@login_required
def my_reviews_view(request):
    """
    List current user's pending and completed reviews
    """
    pending_reviews = ReviewAssignment.objects.filter(
        reviewer=request.user,
        completed=False
    )
    
    completed_reviews = request.user.reviews_given.all()
    
    return render(request, 'reviews/my_reviews.html', {
        'pending_reviews': pending_reviews,
        'completed_reviews': completed_reviews
    })