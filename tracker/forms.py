from django import forms
from .models import Habit, RecurringHabit, Goal, Journal

class HabitForm(forms.ModelForm):

    class Meta:
        model = Habit

        fields = [
            'title',
            'description',
            'category',
            'start_date',
            'end_date',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Enter habit title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'placeholder': 'Describe your habit',
                'rows':2
            }),
            'category': forms.Select(attrs={
                'class':'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-date',
                'type' : 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-date',
                'type' : 'date'
            }),
        }


class RecurringHabitForm(forms.ModelForm):

    class Meta:
        model = RecurringHabit

        fields = [
            'title',
            'description',
            'category',
            'start_date',
            'end_date',
            'repetition',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Enter habit title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'placeholder': 'Describe your habit',
                'rows':2
            }),
            'category': forms.Select(attrs={
                'class':'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-date',
                'type' : 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-date',
                'type' : 'date'
            }),
            'repetition': forms.Select(attrs={
                'class': 'form-select'
            })
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal

        fields = [
            'title',
            'description',
            'category',
            'target_date',
            'target_hours'
        ]        

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Enter goal title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'placeholder': 'Describe your goal',
                'rows':2
            }),
            'category': forms.Select(attrs={
                'class':'form-select'
            }),
            'target_date': forms.DateInput(attrs={
                'class': 'form-date',
                'type' : 'date'
            }),
            'target_hours' : forms.NumberInput(attrs={
                'class':'form-input',
                'placeholder':'Enter target hours'
            })
        }

class JournalForm(forms.ModelForm):
    class Meta:
        model= Journal

        fields = [
            'title',
            'content',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Enter title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'placeholder': 'journal content',
                'rows':5
            })
        }