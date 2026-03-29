from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'due_date', 'late_submission_policy', 'late_penalty_percent', 'max_attempts']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Chapter 1 Quiz'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'late_submission_policy': forms.Select(attrs={'class': 'form-select'}),
            'late_penalty_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'max_attempts': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean(self):
        cleaned = super().clean()
        policy = cleaned.get('late_submission_policy')
        penalty = cleaned.get('late_penalty_percent') or 0

        if policy == Assignment.LATE_POLICY_PENALTY and penalty <= 0:
            self.add_error('late_penalty_percent', 'Set a positive late penalty percentage.')

        if policy != Assignment.LATE_POLICY_PENALTY:
            cleaned['late_penalty_percent'] = 0

        return cleaned

class QuestionForm(forms.Form):
    question_text = forms.CharField(
        max_length=500, 
        label='Question',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    option1 = forms.CharField(
        max_length=200, 
        label='Option 1',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    option2 = forms.CharField(
        max_length=200, 
        label='Option 2',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    option3 = forms.CharField(
        max_length=200, 
        label='Option 3',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    option4 = forms.CharField(
        max_length=200, 
        label='Option 4',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    correct_option = forms.ChoiceField(
        choices=[('1', 'Option 1'), ('2', 'Option 2'), ('3', 'Option 3'), ('4', 'Option 4')], 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
