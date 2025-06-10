from django import forms
from .models import Assignment, Submission, Review

class AssignmentForm(forms.ModelForm):
    """
    Form for creating and updating assignments
    """
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'max_score']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class SubmissionForm(forms.ModelForm):
    """
    Form for creating and updating submissions
    """
    class Meta:
        model = Submission
        fields = ['title', 'content', 'file_upload']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class ReviewForm(forms.ModelForm):
    """
    Form for creating and updating reviews
    """
    class Meta:
        model = Review
        fields = ['score', 'feedback', 'strengths', 'improvements']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 5}),
            'strengths': forms.Textarea(attrs={'rows': 3}),
            'improvements': forms.Textarea(attrs={'rows': 3}),
            'score': forms.Select(attrs={'class': 'form-select'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['score'].widget.attrs.update({'class': 'form-select'})
        self.fields['feedback'].help_text = "Provide detailed feedback on the submission"
        self.fields['strengths'].help_text = "What did the author do well?"
        self.fields['improvements'].help_text = "What could be improved?"