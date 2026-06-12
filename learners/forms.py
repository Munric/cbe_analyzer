from django import forms
from .models import Learner


class LearnerForm(forms.ModelForm):

    class Meta:
        model = Learner
        fields = '__all__'

        widgets = {
            'assessment_no': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'gender': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            
            'assessment_no': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'grade': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'parent_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'parent_phone': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'learner_photo': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            ),
        }