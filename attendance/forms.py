from django import forms
from .models import Attendance
from accounts.models import User


class AttendanceForm(forms.ModelForm):

    employee = forms.ModelChoiceField(
        queryset=User.objects.filter(
            role='EMPLOYEE',
            is_active=True
        ).order_by('first_name', 'last_name'),
        empty_label="Select employee",
        widget=forms.Select(attrs={'class': 'form-control'})

    )

    class Meta:
        model = Attendance
        fields = [
            'employee',
            'date',
            'status',
            'check_in',
            'check_out',
        ]

        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'status': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'check_in': forms.TimeInput(
                attrs={'type': 'time', 'class': 'form-control'}
            ),
            'check_out': forms.TimeInput(
                attrs={'type': 'time', 'class': 'form-control'}
            ),
        }
