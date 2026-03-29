from django import forms
from .models import Classroom

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Physics 101'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief description of your classroom'})
        }


class JoinClassroomForm(forms.Form):
    join_key = forms.CharField(
        max_length=8,
        min_length=8,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter 8-character join key',
                'autocomplete': 'off',
            }
        ),
    )

    def clean_join_key(self):
        return self.cleaned_data['join_key'].strip().upper()
