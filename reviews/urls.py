from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('assignments/', views.assignment_list_view, name='assignment_list'),
    path('assignments/<int:pk>/', views.assignment_detail_view, name='assignment_detail'),
    path('assignments/create/', views.create_assignment_view, name='create_assignment'),
    path('assignments/<int:assignment_pk>/submit/', views.submit_assignment_view, name='submit_assignment'),
    path('submissions/<int:pk>/', views.submission_detail_view, name='submission_detail'),
    path('submissions/<int:submission_pk>/review/', views.review_submission_view, name='review_submission'),
    path('my-submissions/', views.my_submissions_view, name='my_submissions'),
    path('my-reviews/', views.my_reviews_view, name='my_reviews'),
]