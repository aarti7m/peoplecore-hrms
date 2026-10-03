from django import forms
from .models import Salary
from accounts.models import User


class SalaryForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=User.objects.filter(
            role='EMPLOYEE',
            is_active=True
        ).order_by('first_name', 'last_name'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Salary
        fields = [
            'employee',
            'month',
            'basic_salary',
            'allowances',
            'deductions',
            'status',
            'payment_date',
        ]
        widgets = {
            'month': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'basic_salary': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'allowances': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'deductions': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'status': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'payment_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }
