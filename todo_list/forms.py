from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['text']
        labels = {'text': 'New task'}
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'What do you need to do?',
                'autocomplete': 'off',
            }),
        }
